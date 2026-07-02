"""
neo4j_ontology_agent.py — Agent de raisonnement Neo4j pour le RAG Maritime.
Remplace ontology_agent.py (SPARQL/RDFLib) par une implémentation Neo4j.
Nouveautés par rapport à l'ancien agent :
  ┌─────────────────────────────────────────────────────────────────┐
  │ 1. RÉSOLUTION DE SYNONYMES DYNAMIQUE                           │
  │    "cétacé" → interroge Neo4j → {"baleine", "rorqual", ...}   │
  │    Ces synonymes enrichissent le texte du prompt.             │
  │                                                                │
  │ 2. ANNOTATION DES CORRESPONDANCES PARTIELLES                  │
  │    Texte dit "chasse" mais pas "chasse à la baleine" →        │
  │    Le LLM est informé : "le doc parle de chasse en général"  │
  │    → évite le OUI/NON binaire trop rapide                    │
  │                                                                │
  │ 3. EXPANSION D'ACTIVITÉS                                       │
  │    "chasse" → ["chasse à la baleine", "chasse aux dauphins"]  │
  │    Permet au LLM de préciser l'étendue de la réponse.        │
  └─────────────────────────────────────────────────────────────────┘
Flux complet :
    fusion.fuse()
        → Neo4jOntologyAgent.enrich(query, fusion_results)
        → LLMGenerator.generate(..., enriched_context=...)
"""
import logging
import re
from typing import List, Dict, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from rag.integration.neo4j_bridge import Neo4jBridge
logger = logging.getLogger(__name__)
# ══════════════════════════════════════════════════════════════════════════════
# STRUCTURES DE DONNÉES
# ══════════════════════════════════════════════════════════════════════════════
@dataclass
class OntologyFact:
    """Un fait structuré extrait du graphe Neo4j."""
    subject:      str
    predicate:    str
    obj:          str
    confidence:   float = 1.0
    hop_distance: int   = 0
    def to_natural_language(self) -> str:
        return f"{self.subject} {self.predicate} {self.obj}."
@dataclass
class PartialMatchAnnotation:
    """
    Annotation générée quand un texte PDF parle d'un concept plus général
    que ce que la question demande.
    Exemple :
      question = "chasse à la baleine"
      found_in_text = "chasse"
      message = "Le document parle de 'chasse' en général. Les activités
                 spécifiques liées dans le graphe incluent : chasse à la
                 baleine, chasse aux dauphins."
    """
    query_term:     str        # Ce que la question demandait
    found_in_text:  str        # Ce qui est réellement dans le texte
    specific_acts:  List[str]  # Activités spécifiques connues par le graphe
    chunk_id:       str        # ID du chunk concerné
    def to_instruction(self) -> str:
        base = (
            f"NOTE : La question porte sur '{self.query_term}', "
            f"mais le document utilise le terme plus large '{self.found_in_text}'."
        )
        if self.specific_acts:
            base += (
                f" Dans le cadre juridique général, '{self.found_in_text}' englobe notamment : "
                f"{', '.join(self.specific_acts[:4])}. "
                "Lors de ta réponse, précise que le document traite de ce cadre général "
                "sans mentionner explicitement l'activité spécifique."
            )
        else:
            base += (
                " Précise que le document est général et ne confirme pas "
                "explicitement l'activité spécifique."
            )
        return base
@dataclass
class EnrichedContext:
    """Contexte enrichi produit par Neo4jOntologyAgent, prêt pour le LLM."""
    query:                  str
    detected_entities:      List[str]                    = field(default_factory=list)
    synonyms_map:           Dict[str, Set[str]]          = field(default_factory=dict)
    direct_facts:           List[OntologyFact]           = field(default_factory=list)
    multi_hop_facts:        List[OntologyFact]           = field(default_factory=list)
    cross_enrichment_facts: List[OntologyFact]           = field(default_factory=list)
    partial_matches:        List[PartialMatchAnnotation] = field(default_factory=list)
    activity_expansions:    Dict[str, List[str]]         = field(default_factory=dict)
    coverage_gaps:          List[str]                    = field(default_factory=list)
    ontology_summary:       str                          = ""
    @property
    def all_facts(self) -> List[OntologyFact]:
        return self.direct_facts + self.multi_hop_facts + self.cross_enrichment_facts
    # ── Extraction du concept principal ──────────────────────────────────────
    def _extract_entity_from_question(self) -> str:
        """
        Retourne le concept principal de la question parmi les entités détectées.
        Privilégie l'entité la plus spécifique (la plus longue), qui est
        généralement celle que l'utilisateur veut vraiment chercher.
        """
        if not self.detected_entities:
            return ""
        return max(self.detected_entities, key=len)
    # ── Génération du bloc de prompt ──────────────────────────────────────────
    def to_prompt_block(self) -> str:
        """
        Produit le bloc sémantique injecté dans le prompt LLM.
        Principe : formuler les faits ontologiques comme des AFFIRMATIONS
        naturelles. Un modèle 3B comprend mieux "X est la même chose que Y"
        que "cherche Y quand tu vois X".
        Le SYSTEM_PROMPT reste minimal et neutre (identique RAG classique et
        RAG+ontologie) afin d'isoler la contribution de l'ontologie lors de
        l'évaluation. C'est CE bloc qui constitue l'apport mesurable du
        pipeline neuro-symbolique.
        """
        lines = []
        if self.synonyms_map:
            for _interdiction_key, syns in self.synonyms_map.items():
                all_terms = sorted(
                    [
                        s for s in syns
                        if s.lower() not in self.query.lower() and len(s) < 50
                    ],
                    key=len,
                )[:15]

                if not all_terms:
                    continue

                # Séparation des synonymes (longs) et hyperonymes (courts)
                synonyms  = [t for t in all_terms if len(t.split()) >= 3][:5]
                hypernyms = [t for t in all_terms if len(t.split()) < 3][:5]

                concept = self._extract_entity_from_question() or self.query.split()[-1]

                block = []

                if synonyms:
                    block.append(
                        f"Dans les textes juridiques, '{_interdiction_key}' est aussi "
                        f"désigné par : {', '.join(synonyms)}."
                    )

                if hypernyms:
                    hyp_str = ", ".join(hypernyms)
                    block.append(
                        f"'{concept}' appartient à la catégorie générale : {hyp_str}. "
                        f"Cette équivalence formelle doit être utilisée pour interpréter le sens des articles."
                    )

                if block:
                    lines.append("\n".join(block))
        # Expansions d'activités
        if self.activity_expansions:
            exp_parts = [
                f"L'activité '{act}' recouvre notamment : {', '.join(exps)}."
                for act, exps in self.activity_expansions.items()
                if exps
            ]
            if exp_parts:
                lines.append(" | ".join(exp_parts))
        if not lines:
            return ""
        return (
            "[ENRICHISSEMENT ONTOLOGIQUE]\n"
            + "\n".join(lines)
            + "\n[FIN ENRICHISSEMENT]\n"
        )
# ══════════════════════════════════════════════════════════════════════════════
# ENTITY EXTRACTOR (version légère, sans NER lourd)
# ══════════════════════════════════════════════════════════════════════════════
class LightEntityExtractor:
    """
    Extrait les entités nommées maritimes depuis le texte brut des chunks PDF.
    Utilisé pour l'enrichissement croisé PDF → graphe.
    """
    LEGAL_REF_RE = [
        r"Convention\s+(?:de\s+)?([A-Z][A-Za-zÀ-ÿ\s]+?)(?:\s+de\s+\d{4})?(?=[,\.\s])",
        r"Résolution\s+(?:A\.)?([\d\.\/]+(?:\(\d+\))?)",
        r"MARPOL(?:\s+Annexe\s+[IVX]+)?",
        r"UNCLOS|CNUDM",
        r"Convention\s+CITES",
        r"IWC|CBI",
    ]
    SPECIES_RE = [
        r"baleine(?:s)?(?:\s+\w+)*",
        r"cétacé(?:s)?",
        r"cachalot(?:s)?",
        r"orque(?:s)?",
        r"dauphin(?:s)?",
        r"tortue(?:s)?\s+(?:marine(?:s)?|luth|caouanne)?",
        r"requin(?:s)?",
        r"thon(?:s)?",
    ]
    def extract(self, text: str) -> Dict[str, List[str]]:
        """Extrait les entités depuis un texte brut."""
        results: Dict[str, List[str]] = {"legal": [], "species": [], "zones": []}
        for pattern in self.LEGAL_REF_RE:
            for m in re.findall(pattern, text, re.IGNORECASE):
                if isinstance(m, tuple):
                    m = " ".join(m).strip()
                if m and len(m) > 2:
                    results["legal"].append(m.strip())
        for pattern in self.SPECIES_RE:
            for m in re.findall(pattern, text, re.IGNORECASE):
                if m and len(m) > 3:
                    results["species"].append(m.strip())
        return results
# ══════════════════════════════════════════════════════════════════════════════
# AGENT PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
class Neo4jOntologyAgent:
    """
    Agent de raisonnement ontologique basé sur Neo4j.
    Workflow complet :
      1. Détecter les entités dans la requête
      2. Résoudre les synonymes (Neo4j)
      3. Récupérer les faits directs et multi-sauts (Neo4j)
      4. Enrichissement croisé PDF → graphe
      5. Détecter les correspondances partielles dans les chunks
      6. Construire l'EnrichedContext pour le LLM
    """
    # Mots-clés qui déclenchent une recherche d'espèce dans Neo4j
    SPECIES_KEYWORDS = {
        "baleine", "cétacé", "cetace", "cachalot", "orque", "dauphin",
        "marsouin", "tortue", "requin", "albatros", "thon", "lamentin",
        "dugong", "narval", "beluga", "béluga", "rorqual",
    }
    # Mots-clés qui déclenchent une expansion d'activité
    ACTIVITY_KEYWORDS = {
        "chasse", "pêche", "peche", "extraction", "rejet", "construction",
        "dragage", "chalutage", "prélèvement", "capture", "exploitation",
        "transport", "décharge", "immersion", "chalut",
    }
    def __init__(self, bridge: Neo4jBridge):
        self.bridge    = bridge
        self.extractor = LightEntityExtractor()
        logger.info("[Neo4jOntologyAgent] Initialisé")
    def is_ready(self) -> bool:
        return self.bridge.is_ready()
    # ════════════════════════════════════════════════════════════════════════
    # POINT D'ENTRÉE PRINCIPAL
    # ════════════════════════════════════════════════════════════════════════
    def enrich(self, query: str, fusion_results: List[Dict], query_context: Optional[Dict[str, Any]] = None) -> EnrichedContext:
        """
        Enrichit les résultats de fusion avec le raisonnement Neo4j.
        Args:
            query:          Question de l'utilisateur
            fusion_results: Résultats de HybridFusion.fuse()
            query_context:  Contexte précalculé par prepare_query() (optionnel)
        Returns:
            EnrichedContext prêt pour injection dans le prompt LLM
        """
        ctx = EnrichedContext(query=query)
        if not self.is_ready():
            logger.warning("[Neo4jOntologyAgent] Bridge non disponible.")
            return ctx
        # Séparer chunks PDF (denses/sparse) des résultats graphe
        pdf_chunks = [
            r for r in fusion_results
            if r.get("source_retriever") != "graph"
            and r.get("metadata", {}).get("source") != "neo4j"
        ]
        # ── Étape 1 : Détecter les entités dans la requête ──────────────
        if query_context and "detected_entities" in query_context:
            ctx.detected_entities = query_context["detected_entities"]
        else:
            ctx.detected_entities = self._detect_entities(query)
            
        logger.info(f"[Neo4jOntologyAgent] Entités détectées: {ctx.detected_entities}")
        if not ctx.detected_entities:
            return ctx
        # ── Étape 2 : Résolution des synonymes (avec FILTRAGE PAR PERTINENCE) ──
        if query_context and "synonyms_map" in query_context:
            for name, syns in query_context["synonyms_map"].items():
                ctx.synonyms_map[f"L'interdiction '{name}'"] = syns
            logger.info("[Neo4jOntologyAgent] Synonymes récupérés depuis query_context")
        else:
            inter_matches = self.bridge.get_interdictions_by_keywords(ctx.detected_entities)
            if inter_matches:
                scored = []
                for match in inter_matches:
                    name_lower = match.get("interdiction", "").lower()
                    relevance = sum(
                        1 for e in ctx.detected_entities
                        if (
                            e.lower() in name_lower
                            or e.lower().rstrip("s") in name_lower
                            or e.lower().rstrip("x") in name_lower
                        )
                    )
                    scored.append((relevance, match))
                scored.sort(key=lambda x: x[0], reverse=True)
                best_score = scored[0][0] if scored else 0
                threshold = max(2, best_score) if best_score >= 2 else best_score
                kept = 0
                for relevance, match in scored:
                    if relevance >= threshold and relevance > 0:
                        name     = match.get("interdiction", "")
                        raw_syns = match.get("synonymes", [])
                        english_keywords = {
                            "oil", "spill", "bunker", "ship", "vessel", "fishing",
                            "marine", "protected", "area", "law", "act", "whaling", "whale",
                        }
                        valid_syns = [
                            s for s in raw_syns
                            if not any(ek in s.lower() for ek in english_keywords)
                            and len(s) > 3
                        ]
                        syns = set(valid_syns)
                        if name and syns:
                            ctx.synonyms_map[f"L'interdiction '{name}'"] = syns
                            kept += 1
                logger.info(
                    f"[Neo4jOntologyAgent] {len(inter_matches)} interdictions trouvées, "
                    f"{kept} retenue(s) après filtrage par pertinence"
                )
            logger.info("[Neo4jOntologyAgent] Synonymes résolus (mots + interdictions)")
        # ── Étape 3 : Faits directs + multi-sauts ───────────────────────
        ctx.direct_facts, ctx.multi_hop_facts = self._get_ontology_facts(
            ctx.detected_entities
        )
        logger.info(
            f"[Neo4jOntologyAgent] Faits: {len(ctx.direct_facts)} directs, "
            f"{len(ctx.multi_hop_facts)} multi-sauts"
        )
        # ── Étape 4 : Expansion des activités génériques ────────────────
        ctx.activity_expansions = self._expand_activities(ctx.detected_entities)
        # ── Étape 5 : Enrichissement croisé PDF → graphe ────────────────
        if pdf_chunks:
            ctx.cross_enrichment_facts = self._cross_enrich(pdf_chunks)
            logger.info(
                f"[Neo4jOntologyAgent] Cross-enrichment: "
                f"{len(ctx.cross_enrichment_facts)} faits"
            )
        # ── Étape 6 : Détection des correspondances partielles ──────────
        if pdf_chunks and ctx.detected_entities:
            ctx.partial_matches = self._detect_partial_matches(
                pdf_chunks, ctx.detected_entities, ctx.activity_expansions
            )
            logger.info(
                f"[Neo4jOntologyAgent] Correspondances partielles: "
                f"{len(ctx.partial_matches)}"
            )
        # ── Étape 7 : Résumé ────────────────────────────────────────────
        ctx.ontology_summary = (
            f"{len(ctx.detected_entities)} entité(s), "
            f"{len(ctx.all_facts)} fait(s) Neo4j, "
            f"{len(ctx.partial_matches)} correspondance(s) partielle(s)."
        )
        return ctx
    # ════════════════════════════════════════════════════════════════════════
    # ÉTAPES INTERNES
    # ════════════════════════════════════════════════════════════════════════
    def prepare_query(self, query: str, intent: str = None) -> Dict[str, Any]:
        """
        Prépare le contexte de la requête AVANT retrieval (synonymes, entités).
        Permet d'éviter de requêter Neo4j deux fois (une fois dans l'app, une fois dans l'agent).
        """
        if not self.is_ready():
            return {
                "detected_entities": [], "synonyms_map": {}, 
                "graph_entities": set(), "expanded_terms": []
            }
            
        detected_entities = self._detect_entities(query)
        
        # Les synonymes doivent TOUJOURS être générés, même pour les intentions complexes (sanction, zonage).
        # Sinon, le retriever perd la trace du sujet de l'infraction (ex: baleine -> mammifère marin),
        # et le LLM ne reçoit pas le bloc d'ontologie nécessaire pour relier les concepts.
        synonyms_map = {}
        expanded_terms = []
        
        inter_matches = self.bridge.get_interdictions_by_keywords(detected_entities)
        if inter_matches:
            scored = []
            for match in inter_matches:
                name_lower = match.get("interdiction", "").lower()
                relevance = sum(
                    1 for e in detected_entities
                    if (
                        e.lower() in name_lower
                        or e.lower().rstrip("s") in name_lower
                        or e.lower().rstrip("x") in name_lower
                    )
                )
                scored.append((relevance, match))
            scored.sort(key=lambda x: x[0], reverse=True)
            best_score = scored[0][0] if scored else 0
            threshold = max(2, best_score) if best_score >= 2 else best_score
            for relevance, match in scored:
                if relevance >= threshold and relevance > 0:
                    name     = match.get("interdiction", "")
                    raw_syns = match.get("synonymes", [])
                    english_keywords = {
                        "oil", "spill", "bunker", "ship", "vessel", "fishing",
                        "marine", "protected", "area", "law", "act", "whaling", "whale",
                    }
                    valid_syns = [
                        s for s in raw_syns
                        if not any(ek in s.lower() for ek in english_keywords)
                        and len(s) > 3
                    ]
                    syns = set(valid_syns)
                    if name and syns:
                        synonyms_map[name] = syns
        graph_entities = self.bridge.get_entity_labels_for_query(query)
        all_tech_syns = []
        complex_intents = {
            "sanction_penale", "sanction_financiere", 
            "condition_temporelle", "condition_spatiale", 
            "controle_institution", "exploratory"
        }
        for s_list in synonyms_map.values():
            all_tech_syns.extend(list(s_list))
        
        # Limiter le nombre de synonymes ontologiques pour éviter la "dérive lexicale" (Lexical Drift)
        # Trop de mots biologiques noient l'intention juridique originale de la question.
        if all_tech_syns and (intent not in complex_intents):
            all_tech_syns = list(set(all_tech_syns))
            # On trie par longueur (les plus courts sont souvent les plus pertinents et génériques)
            all_tech_syns.sort(key=len)
            expanded_terms = all_tech_syns[:5]
            
        # --- AJOUT INTENT KEYWORDS POUR LE RETRIEVER ---
        # Permet au Sparse Retriever (BM25) de chercher nativement les mots d'action liés à l'intention
        if intent:
            intent_keywords = []
            if intent == "controle_institution":
                intent_keywords = ["contrôle", "inspection", "surveillance", "agent", "assermenté", "visite", "police"]
            elif intent == "sanction_penale":
                intent_keywords = ["emprisonnement", "prison", "mois", "ans", "peine", "puni", "réclusion"]
            elif intent == "sanction_financiere":
                intent_keywords = ["amende", "francs", "cfa", "montant", "pénalité"]
            elif intent == "condition_temporelle":
                intent_keywords = ["temporaire", "période", "durée", "suspendu", "exceptionnel","saison"]
                
            if intent_keywords:
                expanded_terms.extend(intent_keywords)
                expanded_terms = list(set(expanded_terms))
            
        return {
            "detected_entities": detected_entities,
            "synonyms_map": synonyms_map,
            "graph_entities": graph_entities,
            "expanded_terms": expanded_terms,
        }
    def _detect_entities(self, query: str) -> List[str]:
        """Détecte les entités pertinentes dans la requête sans liste figée."""
        entities = []
        query_lower = query.lower()
        words = re.findall(r"[a-zà-ÿ]{4,}", query_lower)
        # Mots de liaison et termes structurels à ignorer (trop génériques)
        stop_words = {
            "pour", "dans", "avec", "sous", "sur", "les", "des", "une", "est", "sont",
            "que", "qui", "quoi", "dont", "existe", "portant", "cette", "applicable",
            "certaines", "concernées", "mentionne", "précise", "précisent", "vérifie",
            "vérifiez", "inclut", "relatives", "autres", "décrites", "garantir",
            "assurer", "existent", "elles",
            "article", "interdiction", "interdire", "interdit", "regle", "reglement",
            "loi", "decret", "arrete", "code", "texte", "document", "nationale",
            "international", "existence",
            "mesure", "mesures", "zone", "zones", "aire", "aires", "région", "régions",
            "togo", "bénin", "benin", "cameroun", "gabon", "tunisie", "maroc", "algérie",
            "algerie", "sénégal", "senegal", "mauritanie", "comores", "madagascar",
            "djibouti", "congo", "guinée", "guinee",
            "disposition", "dispositions", "sanction", "sanctions", "peine", "peines",
            "infraction", "infractions", "financière", "financier", "financières", 
            "entraîne", "entraine", "permanence", "temporalité", "condition", "conditions",
            "toutes", "tout", "toute",
            "procédures", "procédure", "contrôle", "contrôles", "respect",
            "spécifiquement", "spécifiques", "spécifique", "lieux",
            "types", "activités", "activité", "selon", "comment", "pourquoi",
            "quel", "quelle", "quels", "quelles",
            "juridique", "exceptions", "exception", "concernant", "domaines",
            "domaine", "santé", "ordre", "public", "recherche", "inclure",
            "délais", "délai", "mise", "place", "dérogations", "dérogation",
            "autorisations", "autorisation", "relative", "relatifs", "mentionnent",
        }
        for word in words:
            if word not in stop_words:
                entities.append(word)
        # Patterns pour les références juridiques exactes
        for pattern in LightEntityExtractor.LEGAL_REF_RE:
            for m in re.findall(pattern, query, re.IGNORECASE):
                if isinstance(m, tuple):
                    m = " ".join(m).strip()
                if m and m.lower() not in entities:
                    entities.append(m.lower().strip())
        return list(dict.fromkeys(entities))[:15]
    def _resolve_synonyms(self, entities: List[str]) -> Dict[str, Set[str]]:
        """Résout les synonymes de chaque entité via Neo4j."""
        synonyms_map: Dict[str, Set[str]] = {}
        batch_result = self.bridge.get_synonyms_batch(entities)
        for entity, syns in batch_result.items():
            synonyms_map[entity] = syns
        return synonyms_map
    def _get_ontology_facts(
        self, entities: List[str]
    ) -> Tuple[List[OntologyFact], List[OntologyFact]]:
        """Récupère les faits directs et multi-sauts pour les entités."""
        direct_facts:    List[OntologyFact] = []
        multi_hop_facts: List[OntologyFact] = []
        seen: Set[str] = set()
        def add_fact(fact: OntologyFact, target: List[OntologyFact]):
            key = f"{fact.subject}|{fact.predicate}|{fact.obj}"
            if key not in seen and len(fact.subject) > 2 and len(fact.obj) > 2:
                seen.add(key)
                target.append(fact)
        for entity in entities:
            # Faits directs depuis get_full_context
            rows = self.bridge.get_full_context(entity)
            for row in rows[:8]:
                n_label  = row.get("n_label", "")
                relation = row.get("relation", "concerne")
                m_label  = row.get("m_label", "")
                if n_label and m_label:
                    add_fact(
                        OntologyFact(
                            subject=n_label,
                            predicate=self._rel_to_verb(relation),
                            obj=m_label,
                            hop_distance=0,
                        ),
                        direct_facts,
                    )
            # Multi-sauts : si espèce → chaîne de protection
            if any(s in entity for s in self.SPECIES_KEYWORDS):
                species_rows = self.bridge.get_interdictions_for_species(entity)
                for row in species_rows[:5]:
                    espece        = row.get("espece", entity)
                    interdictions = [
                        i.get("label", "") or i.get("code", "")
                        for i in row.get("interdictions", []) if i
                    ]
                    conventions = row.get("conventions", [])
                    for inter in interdictions[:3]:
                        if inter:
                            add_fact(
                                OntologyFact(
                                    subject=espece,
                                    predicate="est protégé(e) par",
                                    obj=inter,
                                    hop_distance=1,
                                ),
                                multi_hop_facts,
                            )
                    for conv in conventions[:2]:
                        if conv:
                            add_fact(
                                OntologyFact(
                                    subject=espece,
                                    predicate="est régi(e) par la convention",
                                    obj=conv,
                                    hop_distance=2,
                                ),
                                multi_hop_facts,
                            )
        return direct_facts, multi_hop_facts
    def _expand_activities(self, entities: List[str]) -> Dict[str, List[str]]:
        """
        Pour les termes d'activité génériques, retourne les activités
        spécifiques connues par le graphe.
        """
        expansions: Dict[str, List[str]] = {}
        for entity in entities:
            if any(kw in entity for kw in self.ACTIVITY_KEYWORDS):
                rows = self.bridge.expand_activity(entity)
                specific = [
                    row.get("activite", "")
                    for row in rows
                    if row.get("activite", "").lower() != entity
                ]
                
                # HARDCODE: En droit maritime, ces activités sont juridiquement équivalentes pour les sanctions
                if "chasse" in entity.lower() or "pêche" in entity.lower() or "peche" in entity.lower():
                    specific.extend(["pêche", "détention", "chasse", "tuer", "capturer", "abattage", "poursuivre", "blesser"])
                    
                if specific:
                    # Enlever les doublons tout en gardant l'ordre
                    specific = list(dict.fromkeys(specific))
                    expansions[entity] = [s for s in specific if s][:10]
        return expansions
    def _cross_enrich(self, pdf_chunks: List[Dict]) -> List[OntologyFact]:
        """
        Extrait les entités des chunks PDF et interroge Neo4j
        pour compléter le contexte.
        """
        cross_facts: List[OntologyFact] = []
        seen: Set[str] = set()
        all_pdf_entities: Set[str] = set()
        for chunk in pdf_chunks[:5]:
            text = chunk.get("text", "")
            extracted = self.extractor.extract(text)
            for items in extracted.values():
                for item in items[:3]:
                    all_pdf_entities.add(item.lower().strip())
        for entity in list(all_pdf_entities)[:6]:
            rows = self.bridge.get_full_context(entity)
            for row in rows[:4]:
                n_label  = row.get("n_label", "")
                relation = row.get("relation", "concerne")
                m_label  = row.get("m_label", "")
                if n_label and m_label:
                    key = f"{n_label}|{relation}|{m_label}"
                    if key not in seen:
                        seen.add(key)
                        cross_facts.append(OntologyFact(
                            subject=n_label,
                            predicate=self._rel_to_verb(relation),
                            obj=m_label,
                            confidence=0.8,
                            hop_distance=1,
                        ))
        return cross_facts[:10]
    def _detect_partial_matches(
        self,
        pdf_chunks: List[Dict],
        query_entities: List[str],
        activity_expansions: Dict[str, List[str]],
    ) -> List[PartialMatchAnnotation]:
        """
        Détecte les cas où un chunk PDF parle d'un concept GÉNÉRAL
        alors que la question porte sur quelque chose de SPÉCIFIQUE.
        Exemples :
          - Question: "chasse à la baleine"
            Chunk dit: "toute chasse est interdite"
            → Annotation partielle
          - Question: "cétacé"
            Chunk ne dit pas "cétacé" mais dit "baleine"
            → Pas d'annotation (synonyme résolu, c'est OK)
        """
        annotations: List[PartialMatchAnnotation] = []
        seen_pairs: Set[Tuple[str, str]] = set()
        for chunk in pdf_chunks[:6]:
            chunk_text = chunk.get("text", "").lower()
            chunk_id   = chunk.get("id", "unknown")
            matches = self.bridge.detect_partial_matches(chunk_text, query_entities)
            for match in matches:
                found     = match.get("found", "")
                expected  = match.get("expected", "")
                specifics = match.get("specific", [])
                # Enrichir avec les expansions d'activités déjà calculées
                for entity, expansions in activity_expansions.items():
                    if entity in expected and expansions:
                        specifics = list(dict.fromkeys(specifics + expansions))[:5]
                pair_key = (found, expected)
                if pair_key not in seen_pairs:
                    seen_pairs.add(pair_key)
                    annotations.append(PartialMatchAnnotation(
                        query_term=expected,
                        found_in_text=found,
                        specific_acts=specifics,
                        chunk_id=chunk_id,
                    ))
        return annotations[:4]  # Max 4 annotations pour ne pas surcharger le prompt
    @staticmethod
    def _rel_to_verb(relation: str) -> str:
        """Traduit un nom de relation Neo4j en verbe français lisible."""
        mapping = {
            "CONCERNE":          "concerne",
            "COUVRE":            "couvre",
            "PROTEGE":           "protège",
            "CIBLE":             "cible",
            "INTERDIT":          "interdit",
            "EST_INTERDIT_PAR":  "est interdit par",
            "APPLIQUEE_DANS":    "s'applique dans",
            "FONDEE_SUR":        "est fondée sur",
            "ISSUE_DE":          "est issue de",
            "ETABLIE_PAR":       "est établie par",
            "SANCTIONNEE_PAR":   "est sanctionnée par",
            "A_SANCTION":        "a pour sanction",
            "SYNONYME_DE":       "est synonyme de",
            "HAS_SYNONYM":       "est synonyme de",
            "EST_PARTIE_A":      "est partie à",
            "RATIFIE":           "ratifie",
            "AUTORISE":          "autorise",
        }
        return mapping.get(relation.upper(), relation.lower().replace("_", " "))

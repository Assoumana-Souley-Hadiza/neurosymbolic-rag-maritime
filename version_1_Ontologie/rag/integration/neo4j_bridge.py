"""
neo4j_bridge.py — Pont Neo4j pour le système RAG Maritime.

Remplace ontology_bridge.py (RDFLib/OWL) par un connecteur Neo4j natif.

Responsabilités :
  - Connexion et exécution de requêtes Cypher
  - Résolution de synonymes  (cétacé ↔ baleine ↔ mammifère marin)
  - Expansion d'activités    ("chasse" → "chasse à la baleine", "chasse aux dauphins"...)
  - Extraction du contexte structuré pour le boost RRF
  - Détection de correspondances partielles pour annoter les chunks PDF

Usage :
    bridge = Neo4jBridge.from_config()   # lit NEO4J_CONFIG depuis rag.config
    bridge.get_synonyms("cétacé")        # → {"baleine", "cétacé", "mammifère marin"}
    bridge.expand_activity("chasse")     # → [{"activite": "Chasse à la baleine", ...}]
"""

import logging
import re
from typing import List, Dict, Set, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Noms des relations dans le graphe Neo4j ──────────────────────────────────
# Adaptez ces constantes à votre schéma réel si nécessaire.
_REL_SYNONYME       = "SYNONYME_DE|HAS_SYNONYM|SYNONYME|BROADER_THAN|NARROWER_THAN|RELATED_TO"   # bidirectionnel et hiérarchique
_REL_COUVRE         = "COUVRE|CONCERNE|CIBLE|INTERDIT"       # Interdiction → Activite
_REL_PROTEGE        = "CONCERNE|PROTEGE|CIBLE_ESPECE"       # Interdiction → EspeceMarine
_REL_CONVENTION     = "FONDEE_SUR|ISSUE_DE|ETABLIE_PAR"     # Interdiction → Convention
_REL_ZONE           = "APPLIQUEE_DANS|COUVRE_ZONE|EN_ZONE"  # Interdiction → Zone
_REL_SANCTION       = "SANCTIONNEE_PAR|A_SANCTION"          # Interdiction → Sanction


class Neo4jBridge:
    """
    Pont principal entre Neo4j et le pipeline RAG.

    Toutes les requêtes Cypher sont isolées ici ; les autres modules
    n'interagissent jamais directement avec le driver Neo4j.
    """

    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        self.driver = None
        self._uri = uri
        try:
            from neo4j import GraphDatabase
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
            self._database = database
            logger.info(f"[Neo4j] ✓ Connecté à {uri} (db: {database})")
        except ImportError:
            logger.error("[Neo4j] Le package 'neo4j' n'est pas installé : pip install neo4j")
        except Exception as e:
            logger.error(f"[Neo4j] Connexion échouée sur {uri} : {e}")
            if self.driver:
                try:
                    self.driver.close()
                except:
                    pass
            self.driver = None

    # ── Constructeur alternatif depuis rag.config ────────────────────────────

    @classmethod
    def from_config(cls) -> "Neo4jBridge":
        """Instancie depuis NEO4J_CONFIG dans rag/config.py."""
        try:
            from rag.config import NEO4J_CONFIG
            return cls(
                uri=NEO4J_CONFIG.get("uri", "bolt://localhost:7687"),
                user=NEO4J_CONFIG.get("user", "neo4j"),
                password=NEO4J_CONFIG.get("password", ""),
                database=NEO4J_CONFIG.get("database", "neo4j"),
            )
        except ImportError:
            logger.warning("[Neo4j] NEO4J_CONFIG introuvable dans rag.config, utilisation des valeurs par défaut.")
            return cls("bolt://localhost:7687", "neo4j", "")

    # ── Utilitaire d'exécution Cypher ────────────────────────────────────────

    def run(self, cypher: str, params: Optional[Dict] = None) -> List[Dict]:
        """Exécute une requête Cypher et retourne les enregistrements sous forme de dicts."""
        if not self.driver:
            return []
            
        try:
            with self.driver.session(database=self._database) as session:
                result = session.run(cypher, params or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"[Neo4j] Erreur Cypher: {e}\nRequête: {cypher[:200]}")
            return []

    def is_ready(self) -> bool:
        return self.driver is not None

    def close(self):
        if self.driver:
            self.driver.close()

    # ════════════════════════════════════════════════════════════════════════
    # RÉSOLUTION DE SYNONYMES
    # ════════════════════════════════════════════════════════════════════════

    def get_synonyms(self, term: str) -> Set[str]:
        """
        Résout les synonymes d'un terme en 1 ou 2 sauts dans le graphe.
        Exemple : "cétacé" → {"baleine", "cétacé", "mammifère marin", "Balaenoptera"}

        Retourne toujours au moins {term} même si Neo4j ne répond pas.
        """
        cypher = """
        MATCH (n)
        WHERE toLower(coalesce(n.label, n.name, '')) CONTAINS toLower($term)

        // Synonymes directs (1 saut, bidirectionnel)
        OPTIONAL MATCH (n)-[:SYNONYME_DE|HAS_SYNONYM|SYNONYME]-(syn1)

        // Synonymes de synonymes (2 sauts)
        OPTIONAL MATCH (n)-[:SYNONYME_DE|HAS_SYNONYM|SYNONYME]-(syn1b)
                           -[:SYNONYME_DE|HAS_SYNONYM|SYNONYME]-(syn2)

        RETURN
            coalesce(n.label, n.name)       AS term_label,
            collect(DISTINCT coalesce(syn1.label, syn1.name))  AS syn1,
            collect(DISTINCT coalesce(syn2.label, syn2.name))  AS syn2
        LIMIT 1
        """
        results = self.run(cypher, {"term": term})
        synonyms: Set[str] = {term}

        for row in results:
            if row.get("term_label"):
                synonyms.add(row["term_label"])
            for s in row.get("syn1", []) + row.get("syn2", []):
                if s and len(s) > 1:
                    synonyms.add(s)

        logger.debug(f"[Neo4j] Synonymes de '{term}': {synonyms}")
        return synonyms

    # ── Extension sémantique forcée pour le domaine maritime ────────────────
    # Utilisé quand le graphe est incomplet sur les verbes fondamentaux.
    MARITIME_DOMAIN_EXPANSION = {
        "chasse":      {"pêche", "capture", "prélèvement", "harponnage", "récolte"},
        "pêche":       {"chasse", "capture", "prélèvement", "récolte", "exploitation"},
        "capture":     {"pêche", "chasse", "prélèvement", "détention", "prise"},
        "rejet":       {"déversement", "immersion", "pollution", "décharge", "évacuation"},
        "pollution":   {"rejet", "déversement", "nuisance", "contamination"},
        "baleine":     {"cétacé", "mammifère marin", "espèce protégée", "grand pélagique"},
        "dauphin":     {"cétacé", "mammifère marin", "petit cétacé"},
        "construction": {"édification", "aménagement", "installation", "ouvrage", "travaux", "aedificandi", "bâtir", "constructible"},
    }

    def get_synonyms_batch(self, terms: List[str]) -> Dict[str, Set[str]]:
        """Résolution de synonymes pour plusieurs termes en une seule requête."""
        if not terms:
            return {}

        cypher = """
        UNWIND $terms AS term
        MATCH (n)
        WHERE toLower(coalesce(n.label, n.prefLabel, n.name, '')) CONTAINS toLower(term)
        
        // On récupère les synonymes via relations
        OPTIONAL MATCH (n)-[:SYNONYME_DE|HAS_SYNONYM|SYNONYME]-(syn_node)
        
        RETURN term,
               coalesce(n.label, n.prefLabel, n.name) AS node_label,
               n.synonym AS direct_synonym,
               collect(DISTINCT coalesce(syn_node.label, syn_node.prefLabel, syn_node.name)) AS rel_synonyms
        """
        results = self.run(cypher, {"terms": terms})
        mapping: Dict[str, Set[str]] = {t: {t} for t in terms}

        # 1. Ajouter les synonymes issus de Neo4j
        for row in results:
            original = row["term"]
            if row.get("node_label"):
                mapping[original].add(row["node_label"])
            
            ds = row.get("direct_synonym")
            if ds:
                if isinstance(ds, list):
                    mapping[original].update([s for s in ds if s])
                else:
                    mapping[original].add(ds)
            
            for s in row.get("rel_synonyms", []):
                if s and len(s) > 1:
                    mapping[original].add(s)

        # 2. Ajouter l'expansion sémantique forcée (Maritime Domain)
        for term in terms:
            term_lower = term.lower()
            if term_lower in self.MARITIME_DOMAIN_EXPANSION:
                mapping[term].update(self.MARITIME_DOMAIN_EXPANSION[term_lower])
            # Vérifier aussi si le terme contient l'un des mots-clés
            for key, values in self.MARITIME_DOMAIN_EXPANSION.items():
                if key in term_lower:
                    mapping[term].update(values)

        return mapping

    def get_interdictions_by_keywords(self, keywords: List[str]) -> List[Dict]:
        """
        Cherche des interdictions liées aux entités (Activités, Espèces, etc.) matchant les mots-clés.
        Retourne l'interdiction, ses synonymes ET ses hyperonymes (termes plus larges).
        Filtre automatiquement les termes anglais maritimes courants.
        """
        if not keywords:
            return []

        cypher = """
        UNWIND $keywords AS k
        MATCH (i:Interdiction)
        OPTIONAL MATCH (i)-[:SYNONYME_DE|HAS_SYNONYM|SYNONYME|COUVRE|CONCERNE|CIBLE|INTERDIT]-(n)
        WITH i, k, collect(coalesce(n.label, n.prefLabel, n.name, '')) AS related_labels
        WHERE toLower(coalesce(i.label, i.prefLabel, i.name, '')) CONTAINS toLower(k)
           OR any(label IN related_labels WHERE toLower(label) CONTAINS toLower(k))
           
        WITH i, count(DISTINCT k) AS score
        WHERE score >= 1
        
        // 1. Synonymes directs de l'interdiction (1 saut)
        OPTIONAL MATCH (i)-[:SYNONYME_DE|HAS_SYNONYM|SYNONYME|RELATED_TO]-(syn_direct)
        
        // 2. Synonymes des activités/entités liées (2 sauts)
        OPTIONAL MATCH (i)-[:COUVRE|CONCERNE|CIBLE|INTERDIT]-(act)-[:SYNONYME_DE|HAS_SYNONYM|SYNONYME|RELATED_TO]-(syn_act)
        
        // 3. Hyperonymes : chaîne hiérarchique (BROADER/NARROWER) jusqu'à 3 niveaux
        OPTIONAL MATCH (i)-[:COUVRE|CONCERNE|CIBLE|INTERDIT]-(ent)-[:BROADER_THAN|NARROWER_THAN*1..3]-(hyper)
        
        RETURN 
            coalesce(i.label, i.prefLabel, i.name) AS interdiction,
            i.synonym AS direct_synonym,
            collect(DISTINCT coalesce(syn_direct.label, syn_direct.prefLabel, syn_direct.name)) 
                + collect(DISTINCT coalesce(syn_act.label, syn_act.prefLabel, syn_act.name)) AS rel_synonyms,
            collect(DISTINCT coalesce(hyper.label, hyper.prefLabel, hyper.name)) AS hypernyms,
            score
        ORDER BY score DESC
        LIMIT 5
        """
        results = self.run(cypher, {"keywords": keywords})
        final_results = []
        
        # Filtre Regex anti-anglais
        anti_english_pattern = re.compile(r'(?i).*\b(whaling|fishing|hunting|sea|marine|oil|spill|bunker|ship|vessel|protected|area|law|act)\b.*')

        for row in results:
            syns = set(s for s in row.get("rel_synonyms", []) if s)
            # Ajouter les hyperonymes dans le même ensemble
            hypers = set(h for h in row.get("hypernyms", []) if h)
            syns.update(hypers)
            
            ds = row.get("direct_synonym")
            if ds:
                if isinstance(ds, list): syns.update(ds)
                else: syns.add(ds)
            
            # Nettoyage des synonymes
            clean_synonyms = [s for s in syns if not anti_english_pattern.match(s) and len(s) > 3]
            
            final_results.append({
                "interdiction": row["interdiction"],
                "synonymes": clean_synonyms,
                "score": row["score"]
            })
            
        return final_results

    # ════════════════════════════════════════════════════════════════════════
    # EXPANSION D'ACTIVITÉS
    # ════════════════════════════════════════════════════════════════════════

    def expand_activity(self, keyword: str) -> List[Dict]:
        """
        Depuis un terme générique (ex: "chasse"), trouve :
          - Toutes les activités spécifiques dans le graphe
          - Leurs synonymes
          - Les interdictions associées
          - Les espèces ciblées par ces interdictions

        Exemple:
          expand_activity("chasse") → [
            {"activite": "Chasse à la baleine",
             "synonymes": ["Pêche à la baleine", "Whaling"],
             "interdictions": ["I001 — Moratoire IWC", ...],
             "especes": ["Baleine bleue", "Rorqual commun"]},
            ...
          ]
        """
        cypher = f"""
        MATCH (a:Activite)
        WHERE toLower(coalesce(a.label, a.name, '')) CONTAINS toLower($keyword)
        
        OPTIONAL MATCH (a)-[:{_REL_SYNONYME}]-(syn)
        OPTIONAL MATCH (i:Interdiction)-[:{_REL_COUVRE}]->(a)
        OPTIONAL MATCH (i)-[:{_REL_PROTEGE}]->(e:EspeceMarine)
        OPTIONAL MATCH (i)-[:{_REL_CONVENTION}]->(c:Convention)

        RETURN
            coalesce(a.label, a.name)                            AS activite,
            a.id                                                 AS activite_id,
            collect(DISTINCT coalesce(syn.label, syn.name))      AS synonymes,
            collect(DISTINCT {{label: coalesce(i.label, i.code), code: i.code}}) AS interdictions,
            collect(DISTINCT coalesce(e.label, e.name))          AS especes,
            collect(DISTINCT coalesce(c.label, c.name))          AS conventions
        ORDER BY activite
        LIMIT 20
        """
        return self.run(cypher, {"keyword": keyword})

    # ════════════════════════════════════════════════════════════════════════
    # CONTEXTE D'INTERDICTION (multi-sauts)
    # ════════════════════════════════════════════════════════════════════════

    def get_interdictions_for_species(self, species_keyword: str) -> List[Dict]:
        """
        Chemin complet: espèce → interdictions → activités → conventions → zones.
        Utilisé pour enrichir le contexte quand la question porte sur une espèce.
        """
        cypher = f"""
        MATCH (e:EspeceMarine)
        WHERE toLower(coalesce(e.label, e.name, '')) CONTAINS toLower($keyword)

        // Chercher aussi les synonymes de l'espèce
        OPTIONAL MATCH (e)-[:{_REL_SYNONYME}]-(syn_e)

        // Interdictions qui concernent cette espèce
        OPTIONAL MATCH (i:Interdiction)-[:{_REL_PROTEGE}]->(e)

        // Activités couvertes par ces interdictions
        OPTIONAL MATCH (i)-[:{_REL_COUVRE}]->(a:Activite)
        OPTIONAL MATCH (a)-[:{_REL_SYNONYME}]-(syn_a)   // synonymes de l'activité

        // Sources juridiques de l'interdiction
        OPTIONAL MATCH (i)-[:{_REL_CONVENTION}]->(c:Convention)

        // Zones d'application
        OPTIONAL MATCH (i)-[:{_REL_ZONE}]->(z:Zone)

        RETURN
            coalesce(e.label, e.name)                               AS espece,
            collect(DISTINCT coalesce(syn_e.label, syn_e.name))    AS synonymes_espece,
            collect(DISTINCT {{
                label:       coalesce(i.label, i.code),
                code:        i.code,
                description: i.description
            }})                                                     AS interdictions,
            collect(DISTINCT coalesce(a.label, a.name))            AS activites,
            collect(DISTINCT coalesce(syn_a.label, syn_a.name))    AS synonymes_activites,
            collect(DISTINCT coalesce(c.label, c.name))            AS conventions,
            collect(DISTINCT coalesce(z.label, z.name))            AS zones
        LIMIT 10
        """
        return self.run(cypher, {"keyword": species_keyword})

    def get_full_context(self, keyword: str) -> List[Dict]:
        """
        Requête universelle : depuis n'importe quel nœud dont le label
        contient `keyword`, explore toutes les relations directes.
        Retourne les faits structurés pour l'OntologyAgent.
        """
        cypher = """
        MATCH (n)
        WHERE toLower(coalesce(n.label, n.name, '')) CONTAINS toLower($keyword)

        OPTIONAL MATCH (n)-[r]->(m)
        RETURN
            labels(n)                              AS n_types,
            coalesce(n.label, n.name)              AS n_label,
            type(r)                                AS relation,
            labels(m)                              AS m_types,
            coalesce(m.label, m.name, m.code)      AS m_label
        LIMIT 60
        """
        return self.run(cypher, {"keyword": keyword})

    # ════════════════════════════════════════════════════════════════════════
    # DÉTECTION DE CORRESPONDANCES PARTIELLES
    # ════════════════════════════════════════════════════════════════════════

    def detect_partial_matches(
        self, chunk_text: str, query_entities: List[str]
    ) -> List[Dict]:
        """
        Analyse un chunk de texte PDF et détecte les correspondances partielles.

        Exemple:
          - Question: "interdiction chasse à la baleine"
          - Texte du chunk: "...toute chasse est interdite..."
          - Résultat: {"type": "partial", "found": "chasse",
                       "expected": "chasse à la baleine",
                       "message": "Le texte mentionne 'chasse' en général ..."}

        Cette annotation est injectée dans le prompt LLM pour qu'il
        puisse nuancer sa réponse sans halluciner.
        """
        if not chunk_text or not query_entities:
            return []

        text_lower = chunk_text.lower()
        matches = []

        for entity in query_entities:
            entity_lower = entity.lower()

            # 1. Correspondance exacte → pas besoin d'annoter
            if entity_lower in text_lower:
                continue

            # 2. Vérifier si un sous-terme de l'entité est présent (match partiel)
            words = entity_lower.split()
            if len(words) < 2:
                continue

            for word in words:
                if len(word) > 3 and word in text_lower:
                    # Récupérer depuis Neo4j les activités spécifiques liées à ce mot générique
                    specific_activities = self._get_specific_activities(word, entity_lower)

                    matches.append({
                        "type":         "partial_match",
                        "found":        word,
                        "expected":     entity_lower,
                        "specific":     specific_activities,
                        "message": (
                            f"Le document mentionne '{word}' en termes généraux "
                            f"mais ne précise pas '{entity_lower}' explicitement. "
                            + (
                                f"Activités spécifiques possibles dans ce contexte : "
                                f"{', '.join(specific_activities[:3])}."
                                if specific_activities else ""
                            )
                        ),
                    })
                    break  # Un seul match partiel par entité

        return matches

    def _get_specific_activities(self, generic_term: str, full_term: str) -> List[str]:
        """
        Pour "chasse" → retourne ["Chasse à la baleine", "Chasse aux dauphins", ...]
        depuis le graphe Neo4j.
        """
        results = self.expand_activity(generic_term)
        activities = []
        for row in results:
            act = row.get("activite", "")
            if act and act.lower() != generic_term and act.lower() != full_term:
                activities.append(act)
        return activities[:5]

    # ════════════════════════════════════════════════════════════════════════
    # LABELS D'ENTITÉS (pour le boost RRF dans fusion.py)
    # ════════════════════════════════════════════════════════════════════════

    def get_entity_labels_for_query(self, query: str) -> Set[str]:
        """
        Extrait tous les labels et synonymes des entités matchées par la requête.
        Utilisé par HybridFusion pour le boost ontologique.

        Retourne un ensemble de tous les termes (label + synonymes) à rechercher
        dans le texte des chunks pour décider d'un boost de score.
        """
        # Tokenisation simple des mots significatifs de la requête (> 3 caractères)
        import re
        words = re.findall(r"[a-zà-ÿ]{4,}", query.lower())

        if not words:
            return set()

        cypher = """
        UNWIND $words AS word
        MATCH (n)
        WHERE toLower(coalesce(n.label, n.name, '')) CONTAINS word

        OPTIONAL MATCH (n)-[:SYNONYME_DE|HAS_SYNONYM|SYNONYME]-(syn)

        RETURN
            coalesce(n.label, n.name)                              AS label,
            collect(DISTINCT coalesce(syn.label, syn.name))        AS synonyms
        LIMIT 40
        """
        results = self.run(cypher, {"words": words})
        labels: Set[str] = set()

        for row in results:
            if row.get("label"):
                labels.add(row["label"].lower())
            for s in row.get("synonyms", []):
                if s and len(s) > 2:
                    labels.add(s.lower())

        return labels

    # ════════════════════════════════════════════════════════════════════════
    # STATISTIQUES
    # ════════════════════════════════════════════════════════════════════════

    def get_stats(self) -> Dict:
        """Retourne des statistiques sur le graphe Neo4j."""
        if not self.is_ready():
            return {"ready": False}

        counts = {}
        for label in ["Interdiction", "Activite", "EspeceMarine", "Convention", "Zone", "Sanction"]:
            rows = self.run(f"MATCH (n:{label}) RETURN count(n) AS cnt")
            counts[label] = rows[0]["cnt"] if rows else 0

        rel_row = self.run("MATCH ()-[r]->() RETURN count(r) AS cnt")
        counts["total_relations"] = rel_row[0]["cnt"] if rel_row else 0

        return {"ready": True, "uri": self._uri, "node_counts": counts}
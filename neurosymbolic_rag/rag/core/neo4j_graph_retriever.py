"""
neo4j_graph_retriever.py — GraphRetriever Neo4j pour le RAG Maritime.

Remplace la classe GraphRetriever (SPARQL/RDFLib) de core/retrievers.py
par une implémentation Cypher native.

Différences clés avec l'ancienne version :
  - Pas de CONCEPT_MAP statique : les concepts sont résolus dynamiquement
    via les synonymes et labels stockés dans Neo4j.
  - Expansion automatique des activités génériques ("chasse" → sous-activités).
  - Les résultats incluent les synonymes ET les activités spécifiques,
    qui seront utilisés pour le boost RRF et l'annotation du prompt LLM.

Intégration dans le pipeline :
    neo4j_retriever = Neo4jGraphRetriever(bridge)
    results = neo4j_retriever.retrieve("interdiction chasse baleine", top_k=10)
"""

import logging
import re
from typing import List, Dict, Set, Optional, Any

from rag.integration.neo4j_bridge import Neo4jBridge

logger = logging.getLogger(__name__)


class Neo4jGraphRetriever:
    """
    Retriever structurel basé sur Neo4j.

    Remplace GraphRetriever (RDFLib/SPARQL).
    Hérite de la même interface (retrieve / is_ready) pour compatibilité
    avec HybridFusion.
    """

    # ── Termes déclencheurs d'une expansion d'activité ──────────────────────
    ACTIVITY_TRIGGERS = {
        "chasse", "pêche", "pechage", "extraction", "rejet", "déversement",
        "construction", "dragage", "chalutage", "prélèvement", "capture",
        "exploitation", "transport", "décharge", "immersion",
    }

    # ── Termes déclencheurs d'une résolution d'espèce ───────────────────────
    SPECIES_TRIGGERS = {
        "baleine", "cétacé", "cetace", "cachalot", "orque", "dauphin",
        "marsouin", "tortue", "requin", "albatros", "pétrel", "thon",
        "espadon", "lamentin", "dugong", "narval", "béluga",
    }

    def __init__(self, bridge: Neo4jBridge):
        self.bridge = bridge
        logger.info("[Neo4jGraphRetriever] Initialisé")

    def is_ready(self) -> bool:
        return self.bridge.is_ready()

    # ════════════════════════════════════════════════════════════════════════
    # POINT D'ENTRÉE PRINCIPAL
    # ════════════════════════════════════════════════════════════════════════

    def retrieve(self, query: str, top_k: Any = 10) -> List[Dict]:
        top_k = int(top_k)
        """
        Recherche structurelle dans Neo4j à partir de la requête.

        Stratégie :
          1. Tokenisation de la requête → mots-clés significatifs
          2. Pour chaque mot-clé :
             a. Si déclencheur d'espèce  → get_interdictions_for_species()
             b. Si déclencheur d'activité → expand_activity()
             c. Sinon                     → get_full_context() (requête générique)
          3. Fusion des résultats → dédupliqués, formatés comme résultats RAG
        """
        if not self.is_ready():
            return []

        keywords = self._extract_keywords(query)
        if not keywords:
            logger.debug("[Neo4jGraphRetriever] Aucun mot-clé détecté.")
            return []

        logger.info(f"[Neo4jGraphRetriever] Mots-clés: {keywords}")

        raw_results: List[Dict] = []
        seen_ids: Set[str] = set()

        for kw in keywords:
            kw_lower = kw.lower()

            if any(t in kw_lower for t in self.SPECIES_TRIGGERS):
                rows = self.bridge.get_interdictions_for_species(kw)
                raw_results.extend(self._format_species_rows(rows, kw))

            elif any(t in kw_lower for t in self.ACTIVITY_TRIGGERS):
                rows = self.bridge.expand_activity(kw)
                raw_results.extend(self._format_activity_rows(rows, kw))

            else:
                rows = self.bridge.get_full_context(kw)
                raw_results.extend(self._format_generic_rows(rows, kw))

        # Déduplication et tri par richesse (nombre de caractères du texte)
        unique_results: List[Dict] = []
        for r in raw_results:
            if r["id"] not in seen_ids:
                seen_ids.add(r["id"])
                unique_results.append(r)

        # Trier : résultats issus d'espèces d'abord (plus précis), puis activités
        unique_results.sort(key=lambda x: len(x.get("text", "")), reverse=True)

        # Ajouter les rangs
        for rank, result in enumerate(unique_results[:top_k], 1):
            result["rank"] = rank
            result["score"] = 1.0 / rank

        logger.info(f"[Neo4jGraphRetriever] {len(unique_results[:top_k])} résultats retournés.")
        return unique_results[:top_k]

    # ════════════════════════════════════════════════════════════════════════
    # FORMATAGE DES RÉSULTATS — Résultats espèce
    # ════════════════════════════════════════════════════════════════════════

    def _format_species_rows(self, rows: List[Dict], keyword: str) -> List[Dict]:
        """
        Formate les résultats de get_interdictions_for_species().

        Le texte synthétique inclut :
          - L'espèce et ses synonymes (pour le boost RRF)
          - LES HYPERONYMES POUR ENRICHISSEMENT CONTEXTUEL
          - Les interdictions qui la protègent
          - Les activités couvertes ET leurs synonymes (pour la détection partielle)
          - Les conventions et zones applicables
        """
        formatted = []
        for row in rows:
            espece = row.get("espece", keyword)
            syn_e  = [s for s in row.get("synonymes_espece", []) if s]
            hyp_e  = [h for h in row.get("hypernyms_espece", []) if h]  # NOUVEAU
            
            interdictions = [
                x for x in (
                    (i.get("label", "") or i.get("code", "") or "")
                    for i in row.get("interdictions", []) if i
                ) if x
            ]
            activites      = [a for a in row.get("activites", []) if a]
            syn_a          = [s for s in row.get("synonymes_activites", []) if s]
            hyp_a          = [h for h in row.get("hypernyms_activites", []) if h]  # NOUVEAU
            conventions    = [c for c in row.get("conventions", []) if c]
            zones          = [z for z in row.get("zones", []) if z]

            if not espece:
                continue

            # ── Construction du texte synthétique ───────────────────────────
            parts = [f"Espèce : {espece}."]

            if syn_e:
                parts.append(f"Aussi appelé(e) : {', '.join(syn_e)}.")
            
            if hyp_e:
                parts.append(f"Catégories générales : {', '.join(hyp_e)}.")

            if interdictions:
                parts.append(
                    f"Protégé(e) par les interdictions : {', '.join(interdictions)}."
                )

            if activites:
                # Inclure les synonymes et hyperonymes pour couvrir les termes génériques du texte
                all_activites = list(dict.fromkeys(activites + syn_a + hyp_a))  # dédupliqués
                parts.append(
                    f"Activités réglementées : {', '.join(all_activites)}."
                )

            if conventions:
                parts.append(f"Conventions applicables : {', '.join(conventions)}.")

            if zones:
                parts.append(f"Zones d'application : {', '.join(zones)}.")

            result_id = f"neo4j_species_{espece.lower().replace(' ', '_')}"
            formatted.append({
                "id":               result_id,
                "rank":             0,   # sera assigné après déduplication
                "text":             " ".join(parts),
                "metadata": {
                    "source":   "neo4j",
                    "category": "species_protection",
                    "espece":   espece,
                    "synonymes_espece":   syn_e,
                    "hypernyms_espece":   hyp_e,  # NOUVEAU
                    "synonymes_activites": syn_a,
                    "hypernyms_activites": hyp_a,  # NOUVEAU
                },
                "score":            0.0,
                "source_retriever": "graph",
                # Données structurées utilisées par OntologyAgent et PartialMatchAnnotator
                "graph_data": {
                    "label":              espece,
                    "synonymes":          syn_e,
                    "hypernyms":          hyp_e,  # NOUVEAU
                    "interdictions":      interdictions,
                    "activites":          activites,
                    "synonymes_activites": syn_a,
                    "hypernyms_activites": hyp_a,  # NOUVEAU
                    "conventions":        conventions,
                    "zones":              zones,
                    "node_type":          "EspeceMarine",
                },
            })

        return formatted

    # ── Formatage résultats activité ─────────────────────────────────────────

    def _format_activity_rows(self, rows: List[Dict], keyword: str) -> List[Dict]:
        """Formate les résultats de expand_activity() en incluant les hyperonymes."""
        formatted = []
        for row in rows:
            activite = row.get("activite", keyword)
            synonymes = [s for s in row.get("synonymes", []) if s]
            hypernyms = [h for h in row.get("hypernyms", []) if h]  # NOUVEAU
            
            interdictions = [
                x for x in (
                    (i.get("label", "") or i.get("code", "") or "")
                    for i in row.get("interdictions", []) if i
                ) if x
            ]
            especes    = [e for e in row.get("especes", []) if e]
            conventions = [c for c in row.get("conventions", []) if c]

            if not activite:
                continue

            parts = [f"Activité : {activite}."]
            
            if synonymes:
                parts.append(f"Aussi appelé(e) : {', '.join(synonymes)}.")
            
            if hypernyms:
                parts.append(f"Catégories générales : {', '.join(hypernyms)}.")
            
            if interdictions:
                parts.append(f"Soumis(e) aux interdictions : {', '.join(interdictions)}.")
            
            if especes:
                parts.append(f"Espèces concernées : {', '.join(especes)}.")
            
            if conventions:
                parts.append(f"Conventions applicables : {', '.join(conventions)}.")

            result_id = f"neo4j_activity_{activite.lower().replace(' ', '_')[:40]}"
            formatted.append({
                "id":               result_id,
                "rank":             0,
                "text":             " ".join(parts),
                "metadata": {
                    "source":   "neo4j",
                    "category": "activity",
                    "activite": activite,
                    "synonymes": synonymes,
                    "hypernyms": hypernyms,  # NOUVEAU
                },
                "score":            0.0,
                "source_retriever": "graph",
                "graph_data": {
                    "label":       activite,
                    "synonymes":   synonymes,
                    "hypernyms":   hypernyms,  # NOUVEAU
                    "interdictions": interdictions,
                    "especes":     especes,
                    "node_type":   "Activite",
                },
            })

        return formatted

    # ── Formatage résultats génériques ──────────────────────────────────────

    def _format_generic_rows(self, rows: List[Dict], keyword: str) -> List[Dict]:
        """
        Formate les résultats de get_full_context().
        Groupe les relations par nœud source.
        """
        # Agréger les relations par nœud source
        entities: Dict[str, Dict] = {}
        for row in rows:
            n_label   = row.get("n_label", "")
            n_types   = row.get("n_types", [])
            relation  = row.get("relation", "")
            m_label   = row.get("m_label", "")

            if not n_label:
                continue

            key = n_label
            if key not in entities:
                entities[key] = {
                    "label": n_label,
                    "types": n_types,
                    "relations": [],
                }
            if relation and m_label:
                entities[key]["relations"].append(f"{relation}: {m_label}")

        formatted = []
        for label, data in list(entities.items())[:10]:
            parts = [f"{label}."]
            if data["relations"]:
                parts.append(" ".join(f"{r}." for r in data["relations"][:5]))

            node_types = data.get("types", [])
            result_id = f"neo4j_generic_{label.lower().replace(' ', '_')[:40]}"
            formatted.append({
                "id":               result_id,
                "rank":             0,
                "text":             " ".join(parts),
                "metadata": {
                    "source":   "neo4j",
                    "category": "generic",
                    "types":    node_types,
                },
                "score":            0.0,
                "source_retriever": "graph",
                "graph_data": {
                    "label":     label,
                    "types":     node_types,
                    "relations": data["relations"],
                },
            })

        return formatted

    # ════════════════════════════════════════════════════════════════════════
    # EXTRACTION DE MOTS-CLÉS
    # ════════════════════════════════════════════════════════════════════════

    def _extract_keywords(self, query: str) -> List[str]:
        """
        Extrait les mots-clés significatifs de la requête.

        Stratégie :
          1. Suppression des stop-words français
          2. Conservation des mots > 3 caractères
          3. Priorisation des déclencheurs espèce/activité
        """
        STOP_WORDS = {
            "les", "des", "une", "est", "son", "sur", "par", "que", "qui",
            "dans", "avec", "pour", "pas", "plus", "cette", "aussi",
            "donc", "mais", "elle", "leurs", "quel", "quelle", "quels",
            "quelles", "comme", "tout", "tous", "toute", "toutes",
            "être", "avoir", "faire", "dire", "voir", "aller", "venir",
            "bien", "très", "plus", "moins", "même", "aussi", "encore",
            "déjà", "toujours", "jamais", "souvent", "parfois", "alors",
        }

        raw_words = re.findall(r"[a-zà-ÿ]{3,}", query.lower())
        keywords = [w for w in raw_words if w not in STOP_WORDS]

        # Prioriser : espèces et activités en premier
        priority = []
        normal = []
        for kw in keywords:
            if any(t in kw for t in self.SPECIES_TRIGGERS | self.ACTIVITY_TRIGGERS):
                priority.append(kw)
            else:
                normal.append(kw)

        return list(dict.fromkeys(priority + normal))[:6]  # Max 6 pour performance

    # ════════════════════════════════════════════════════════════════════════
    # STATS
    # ════════════════════════════════════════════════════════════════════════

    def get_stats(self) -> Dict:
        stats = self.bridge.get_stats()
        stats["retriever"] = "neo4j_graph"
        return stats
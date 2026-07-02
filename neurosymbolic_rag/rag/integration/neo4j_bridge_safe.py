"""
neo4j_bridge_safe.py — Wrapper Neo4j avec fallback gracieux.

Permet au système de continuer à fonctionner même si Neo4j est down,
en basculant vers RDFLib.
"""

import logging
from typing import Optional, Dict, List, Set
from pathlib import Path

logger = logging.getLogger(__name__)


class Neo4jBridgeSafe:
    """
    Wrapper Neo4j avec fallback à RDFLib si indisponible.
    """

    def __init__(self):
        self.neo4j_available = False
        self.rdf_fallback = None
        self.bridge = None
        self._initialize()

    def _initialize(self):
        """Initialise Neo4j ou RDF fallback."""
        try:
            from rag.integration.neo4j_bridge import Neo4jBridge
            self.bridge = Neo4jBridge.from_config()
            if self.bridge.is_ready():
                self.neo4j_available = True
                logger.info("✅ Neo4j disponible - utilisation de Neo4jBridge")
            else:
                self._init_rdf_fallback()
        except Exception as e:
            logger.warning(f"⚠️  Neo4j indisponible: {e}")
            self._init_rdf_fallback()

    def _init_rdf_fallback(self):
        """Initialise le fallback RDFLib."""
        try:
            from rag.core.neo4j_graph_retriever import RDFGraphRetriever
            self.rdf_fallback = RDFGraphRetriever()
            logger.info("✅ Fallback RDFLib activé")
        except Exception as e:
            logger.error(f"❌ Impossible d'initialiser RDF fallback: {e}")

    def is_ready(self) -> bool:
        """Vérifie si le bridge est opérationnel."""
        if self.neo4j_available and self.bridge:
            try:
                return self.bridge.is_ready()
            except Exception:
                # Fallback si Neo4j devient indisponible en cours de route
                self.neo4j_available = False
                self._init_rdf_fallback()
        
        return self.rdf_fallback is not None

    def retrieve(self, query: str, top_k: int = 10) -> List[Dict]:
        """Retrive avec fallback automatique."""
        if self.neo4j_available and self.bridge:
            try:
                return self.bridge.retrieve(query, top_k)
            except Exception as e:
                logger.warning(f"❌ Erreur Neo4j, basculage vers RDF: {e}")
                self.neo4j_available = False
                if not self.rdf_fallback:
                    self._init_rdf_fallback()
        
        if self.rdf_fallback:
            try:
                return self.rdf_fallback.retrieve(query, top_k)
            except Exception as e:
                logger.error(f"❌ Erreur RDF fallback: {e}")
                return []
        
        return []

    def get_synonyms(self, term: str) -> Set[str]:
        """Get synonymes avec fallback."""
        if self.neo4j_available and self.bridge:
            try:
                return self.bridge.get_synonyms(term)
            except Exception as e:
                logger.warning(f"⚠️  Erreur get_synonyms Neo4j: {e}")
        
        # RDF fallback
        if self.rdf_fallback:
            try:
                return self.rdf_fallback.get_synonyms(term)
            except Exception:
                pass
        
        return {term}

    def get_synonyms_batch(self, terms: List[str]) -> Dict[str, Set[str]]:
        """Get synonymes en batch avec fallback."""
        if self.neo4j_available and self.bridge:
            try:
                return self.bridge.get_synonyms_batch(terms)
            except Exception as e:
                logger.warning(f"⚠️  Erreur get_synonyms_batch Neo4j: {e}")
        
        # RDF fallback
        if self.rdf_fallback:
            try:
                return self.rdf_fallback.get_synonyms_batch(terms)
            except Exception:
                pass
        
        # Fallback minimal: chaque terme = lui-même
        return {term: {term} for term in terms}

    def detect_entities(self, query: str) -> Set[str]:
        """Détecte les entités avec fallback."""
        if self.neo4j_available and self.bridge:
            try:
                return self.bridge.detect_entities(query)
            except Exception as e:
                logger.warning(f"⚠️  Erreur detect_entities Neo4j: {e}")
        
        if self.rdf_fallback:
            try:
                return self.rdf_fallback.detect_entities(query)
            except Exception:
                pass
        
        return set()

    def get_status(self) -> str:
        """Retourne le statut actuel."""
        if self.neo4j_available:
            return "🟢 Neo4j"
        elif self.rdf_fallback:
            return "🟡 RDF Fallback"
        else:
            return "🔴 Indisponible"

    def get_interdictions_for_species(self, species_keyword: str) -> List[Dict]:
        """Proxy pour get_interdictions_for_species avec fallback."""
        if self.neo4j_available and self.bridge:
            try:
                return self.bridge.get_interdictions_for_species(species_keyword)
            except Exception as e:
                logger.warning(f"⚠️  Erreur get_interdictions_for_species Neo4j: {e}")
        
        # Le fallback RDFLib ne supporte potentiellement pas cette méthode
        # On retourne une liste vide pour éviter de faire planter le script
        return []

    def expand_activity(self, keyword: str) -> List[Dict]:
        """Proxy pour expand_activity avec fallback."""
        if self.neo4j_available and self.bridge:
            try:
                return self.bridge.expand_activity(keyword)
            except Exception as e:
                logger.warning(f"⚠️  Erreur expand_activity Neo4j: {e}")
                
        return []

    def get_full_context(self, keyword: str) -> List[Dict]:
        """Proxy pour get_full_context avec fallback."""
        if self.neo4j_available and self.bridge:
            try:
                return self.bridge.get_full_context(keyword)
            except Exception as e:
                logger.warning(f"⚠️  Erreur get_full_context Neo4j: {e}")
                
        return []

    def get_stats(self) -> Dict:
        """Proxy pour get_stats avec fallback."""
        if self.neo4j_available and self.bridge:
            try:
                return self.bridge.get_stats()
            except Exception as e:
                logger.warning(f"⚠️  Erreur get_stats Neo4j: {e}")
                
        return {"ready": False, "error": "Neo4j non disponible"}

    def get_entity_labels_for_query(self, query: str) -> Set[str]:
        """Proxy pour get_entity_labels_for_query avec fallback."""
        if self.neo4j_available and self.bridge:
            try:
                return self.bridge.get_entity_labels_for_query(query)
            except Exception as e:
                logger.warning(f"⚠️  Erreur get_entity_labels_for_query Neo4j: {e}")
                
        return set()

    def detect_partial_matches(self, chunk_text: str, query_entities: List[str]) -> List[Dict]:
        """Proxy pour detect_partial_matches avec fallback."""
        if self.neo4j_available and self.bridge:
            try:
                return self.bridge.detect_partial_matches(chunk_text, query_entities)
            except Exception as e:
                logger.warning(f"⚠️  Erreur detect_partial_matches Neo4j: {e}")
                
        return []

    def get_interdictions_by_keywords(self, keywords: List[str]) -> List[Dict]:
        """Proxy pour get_interdictions_by_keywords avec fallback."""
        if self.neo4j_available and self.bridge:
            try:
                return self.bridge.get_interdictions_by_keywords(keywords)
            except Exception as e:
                logger.warning(f"⚠️  Erreur get_interdictions_by_keywords Neo4j: {e}")
                
        return []



def get_safe_bridge() -> Neo4jBridgeSafe:
    """Factory pour accéder au bridge safe."""
    return Neo4jBridgeSafe()

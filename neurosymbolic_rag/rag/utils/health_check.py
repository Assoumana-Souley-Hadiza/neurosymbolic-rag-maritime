"""
health_check.py — Vérification de la santé du système RAG.

Permet de vérifier la disponibilité des composants et signaler les problèmes.
"""

import logging
from typing import Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)


class RAGHealthCheck:
    """Vérifie l'état du système RAG."""

    def __init__(self):
        self.health_status: Dict[str, bool] = {}
        self.error_messages: Dict[str, str] = {}

    def check_dense_retriever(self) -> bool:
        """Vérifie si DenseRetriever est disponible."""
        try:
            from rag.core.retrievers import DenseRetriever
            retriever = DenseRetriever()
            is_ready = retriever.is_ready()
            if is_ready:
                logger.info("✅ DenseRetriever: OK")
                self.health_status["dense"] = True
            else:
                msg = "ChromaDB vide ou manquant"
                logger.warning(f"⚠️  DenseRetriever: {msg}")
                self.health_status["dense"] = False
                self.error_messages["dense"] = msg
            return is_ready
        except Exception as e:
            msg = str(e)
            logger.error(f"❌ DenseRetriever: {msg}")
            self.health_status["dense"] = False
            self.error_messages["dense"] = msg
            return False

    def check_sparse_retriever(self) -> bool:
        """Vérifie si SparseRetriever est disponible."""
        try:
            from rag.core.retrievers import SparseRetriever
            retriever = SparseRetriever()
            is_ready = retriever.is_ready()
            if is_ready:
                logger.info("✅ SparseRetriever: OK")
                self.health_status["sparse"] = True
            else:
                msg = "BM25 index manquant"
                logger.warning(f"⚠️  SparseRetriever: {msg}")
                self.health_status["sparse"] = False
                self.error_messages["sparse"] = msg
            return is_ready
        except Exception as e:
            msg = str(e)
            logger.error(f"❌ SparseRetriever: {msg}")
            self.health_status["sparse"] = False
            self.error_messages["sparse"] = msg
            return False

    def check_neo4j_bridge(self) -> bool:
        """Vérifie si Neo4jBridge est disponible."""
        try:
            from rag.integration.neo4j_bridge import Neo4jBridge
            bridge = Neo4jBridge.from_config()
            is_ready = bridge.is_ready()
            if is_ready:
                logger.info("✅ Neo4jBridge: OK")
                self.health_status["neo4j"] = True
            else:
                msg = "Neo4j indisponible"
                logger.warning(f"⚠️  Neo4jBridge: {msg}")
                self.health_status["neo4j"] = False
                self.error_messages["neo4j"] = msg
            return is_ready
        except Exception as e:
            msg = str(e)
            logger.warning(f"⚠️  Neo4jBridge: {msg}")
            self.health_status["neo4j"] = False
            self.error_messages["neo4j"] = msg
            return False

    def check_graph_retriever(self) -> bool:
        """Vérifie si Neo4jGraphRetriever est disponible."""
        try:
            from rag.core.neo4j_graph_retriever import Neo4jGraphRetriever
            from rag.integration.neo4j_bridge import Neo4jBridge
            
            bridge = Neo4jBridge.from_config()
            if not bridge.is_ready():
                raise RuntimeError("Neo4j bridge not ready")
            
            retriever = Neo4jGraphRetriever(bridge)
            logger.info("✅ GraphRetriever: OK")
            self.health_status["graph"] = True
            return True
        except Exception as e:
            msg = str(e)
            logger.warning(f"⚠️  GraphRetriever: {msg}")
            self.health_status["graph"] = False
            self.error_messages["graph"] = msg
            return False

    def check_ollama(self) -> bool:
        """Vérifie si Ollama est disponible."""
        try:
            import requests
            from rag.config import LLM_CONFIG
            
            url = f"{LLM_CONFIG['base_url']}/api/tags"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info("✅ Ollama: OK")
                self.health_status["ollama"] = True
                return True
            else:
                msg = f"Ollama HTTP error: {response.status_code}"
                logger.warning(f"⚠️  Ollama: {msg}")
                self.health_status["ollama"] = False
                self.error_messages["ollama"] = msg
                return False
        except Exception as e:
            msg = str(e)
            logger.warning(f"⚠️  Ollama: {msg}")
            self.health_status["ollama"] = False
            self.error_messages["ollama"] = msg
            return False

    def check_data_paths(self) -> bool:
        """Vérifie que les répertoires essentiels existent."""
        from rag.config import CHROMA_DB_DIR, BM25_INDEX_DIR, CHUNKS_DIR, OUTPUT_DIR
        
        paths = {
            "output": OUTPUT_DIR,
            "chroma": CHROMA_DB_DIR,
            "bm25": BM25_INDEX_DIR,
            "chunks": CHUNKS_DIR,
        }
        
        all_exist = True
        for name, path in paths.items():
            try:
                path.mkdir(parents=True, exist_ok=True)
                logger.info(f"✅ {name}: {path}")
            except Exception as e:
                logger.error(f"❌ {name}: {e}")
                self.error_messages[f"path_{name}"] = str(e)
                all_exist = False
        
        self.health_status["data_paths"] = all_exist
        return all_exist

    def full_check(self) -> bool:
        """Exécute tous les checks."""
        logger.info("=" * 70)
        logger.info("🔍 VÉRIFICATION SANTÉ DU SYSTÈME RAG")
        logger.info("=" * 70)
        
        self.check_data_paths()
        dense_ok = self.check_dense_retriever()
        sparse_ok = self.check_sparse_retriever()
        neo4j_ok = self.check_neo4j_bridge()
        graph_ok = self.check_graph_retriever()
        ollama_ok = self.check_ollama()
        
        # Au moins un retriever doit être opérationnel
        has_retriever = dense_ok or sparse_ok or neo4j_ok or graph_ok
        
        logger.info("=" * 70)
        if has_retriever and ollama_ok:
            logger.info("✅ SYSTÈME: OPÉRATIONNEL (avec dégradation possible)")
            return True
        elif has_retriever:
            logger.warning("⚠️  SYSTÈME: DÉGRADÉ (LLM indisponible)")
            return False
        else:
            logger.error("❌ SYSTÈME: INOPÉRATIONNEL")
            return False

    def get_status_dict(self) -> Dict[str, bool]:
        """Retourne le statut complet."""
        return self.health_status

    def get_errors(self) -> Dict[str, str]:
        """Retourne les messages d'erreur."""
        return self.error_messages

    def print_report(self) -> str:
        """Génère un rapport texte."""
        lines = ["📋 RAPPORT SANTÉ RAG", "=" * 50]
        
        for component, status in sorted(self.health_status.items()):
            symbol = "✅" if status else "❌"
            lines.append(f"{symbol} {component}: {'OK' if status else 'ERREUR'}")
            if component in self.error_messages:
                lines.append(f"   → {self.error_messages[component]}")
        
        return "\n".join(lines)


def get_health_check() -> RAGHealthCheck:
    """Factory pour accéder au HealthCheck."""
    return RAGHealthCheck()

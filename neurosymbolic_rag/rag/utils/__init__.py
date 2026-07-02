"""
rag/utils — Utilitaires pour le système RAG.

Modules:
  - versioning: Gestion des versions d'embeddings et indexes
  - metrics: Enregistrement des métriques de qualité
  - health_check: Vérification de santé du système
"""

from .versioning import VersionManager, get_version_manager
from .metrics import RetrievalMetrics, get_metrics_logger
from .health_check import RAGHealthCheck, get_health_check

__all__ = [
    "VersionManager",
    "get_version_manager",
    "RetrievalMetrics",
    "get_metrics_logger",
    "RAGHealthCheck",
    "get_health_check",
]

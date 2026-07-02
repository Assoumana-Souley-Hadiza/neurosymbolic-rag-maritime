"""
versioning.py — Gestion des versions d'embeddings et d'indexes.

Permet le versioning des modèles et des indexes pour faciliter
le rollback et l'expérimentation.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class VersionManager:
    """Gère le versioning des embeddings et indexes."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.metadata_file = output_dir / "versions.json"
        self.versions: Dict[str, Any] = self._load_versions()

    def _load_versions(self) -> Dict[str, Any]:
        """Charge les métadonnées de versions existantes."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️  Impossible de charger versions.json: {e}")
        return {}

    def save_embedding_version(
        self,
        version: str,
        model_name: str,
        model_version: str,
        embedding_dim: int,
        num_documents: int,
    ) -> None:
        """Enregistre une nouvelle version d'embeddings."""
        self.versions[version] = {
            "type": "embeddings",
            "model_name": model_name,
            "model_version": model_version,
            "embedding_dim": embedding_dim,
            "num_documents": num_documents,
            "created_at": datetime.utcnow().isoformat(),
            "path": f"chroma_db_{version}",
        }
        self._persist()
        logger.info(f"✅ Version embeddings enregistrée: {version}")

    def save_index_version(
        self,
        version: str,
        index_type: str,  # "bm25", "sparse", etc.
        num_documents: int,
        description: Optional[str] = None,
    ) -> None:
        """Enregistre une nouvelle version d'index."""
        self.versions[version] = {
            "type": index_type,
            "num_documents": num_documents,
            "created_at": datetime.utcnow().isoformat(),
            "description": description or "",
            "path": f"{index_type}_{version}",
        }
        self._persist()
        logger.info(f"✅ Version index enregistrée: {version}")

    def get_active_version(self, version_type: str) -> Optional[str]:
        """Retourne la version la plus récente d'un type donné."""
        matching = [
            (v_name, v_data)
            for v_name, v_data in self.versions.items()
            if v_data.get("type") == version_type
        ]
        if not matching:
            return None
        # Tri par date de création décroissante
        sorted_versions = sorted(
            matching, key=lambda x: x[1].get("created_at", ""), reverse=True
        )
        return sorted_versions[0][0]

    def list_versions(self, version_type: Optional[str] = None) -> list:
        """Liste toutes les versions, optionnellement filtrées par type."""
        versions_list = []
        for v_name, v_data in self.versions.items():
            if version_type is None or v_data.get("type") == version_type:
                versions_list.append({
                    "name": v_name,
                    "type": v_data.get("type"),
                    "created_at": v_data.get("created_at"),
                    "num_documents": v_data.get("num_documents"),
                })
        return sorted(
            versions_list, key=lambda x: x.get("created_at", ""), reverse=True
        )

    def _persist(self) -> None:
        """Persiste les métadonnées dans versions.json."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(self.versions, f, indent=2, ensure_ascii=False)

    def export_summary(self) -> str:
        """Exporte un résumé texte des versions."""
        lines = ["📦 VERSIONS ENREGISTRÉES", "=" * 50]
        for v_name, v_data in self.versions.items():
            lines.append(f"\n🏷️  {v_name}")
            lines.append(f"   Type: {v_data.get('type')}")
            lines.append(f"   Docs: {v_data.get('num_documents', 'N/A')}")
            lines.append(f"   Créé: {v_data.get('created_at', 'N/A')}")
            if v_data.get("model_name"):
                lines.append(f"   Modèle: {v_data.get('model_name')}")
        return "\n".join(lines)


def get_version_manager(output_dir: Path) -> VersionManager:
    """Factory pour accéder au VersionManager."""
    return VersionManager(output_dir)

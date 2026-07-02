"""
embeddings_pipeline.py — Pipeline d'ingestion : extraction + indexation hybride.

Orchestre l'indexation simultanée dans :
  - DenseRetriever  (ChromaDB)
  - SparseRetriever (BM25)
"""

import logging
import json
from pathlib import Path
from typing import List, Dict

from rag.config import CHUNKS_DIR
from rag.core.retrievers import DenseRetriever, SparseRetriever

logger = logging.getLogger(__name__)

# Champs autorisés comme métadonnées filtrables dans ChromaDB
# (pas de None, pas de listes — scalaires uniquement)
METADATA_FIELDS = [
    "source", "doc_title", "category", "country", "page",
    "doc_type", "doc_number", "doc_date",
    "titre", "chapitre", "section", "article", "annexe",
    "word_count", "quality_score",
]

# Seuil minimum de qualité — les chunks en dessous ne sont pas indexés
MIN_QUALITY_SCORE = 0.5


class EmbeddingsPipeline:
    """Pipeline d'ingestion et d'indexation hybride (Vectoriel + BM25)."""

    def __init__(self):
        logger.info("[INIT] Initialisation EmbeddingsPipeline...")
        self.dense = DenseRetriever()
        self.sparse = SparseRetriever()

    def load_chunks(self, chunk_file: str = "all_chunks.json") -> List[Dict]:
        """Charge les chunks depuis JSON."""
        chunk_path = CHUNKS_DIR / chunk_file
        if not chunk_path.exists():
            logger.error(f"Fichier chunks non trouvé: {chunk_path}")
            return []

        with open(chunk_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)

        logger.info(f"Chunks chargés: {len(chunks)}")
        return chunks

    def filter_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Filtre les chunks avant indexation :
          - Supprime les chunks sous le seuil de qualité
          - Supprime les doublons par content_hash (sécurité si pipeline relancé)
        """
        seen_hashes = set()
        filtered = []

        for c in chunks:
            # Filtre qualité
            if c.get("quality_score", 1.0) < MIN_QUALITY_SCORE:
                continue
            # Déduplication
            h = c.get("content_hash", c["id"])
            if h in seen_hashes:
                continue
            seen_hashes.add(h)
            filtered.append(c)

        removed = len(chunks) - len(filtered)
        if removed:
            logger.info(f"Filtrés avant indexation : {removed} chunks (qualité ou doublons)")

        return filtered

    def _build_embedding_text(self, chunk: Dict) -> str:
        """
        Contextual embedding : on concatène le breadcrumb au texte pour que
        le vecteur encode à la fois le contenu ET la provenance légale.

        Ex: "Maroc | Loi n°11-03 | Article 15\n\nArt. 15 - Il est interdit..."

        Le breadcrumb n'est PAS stocké dans le payload (il est dans les métadonnées),
        il sert uniquement à enrichir le vecteur.
        """
        breadcrumb = chunk.get("breadcrumb", "").strip()
        text = chunk.get("text", "").strip()
        if breadcrumb:
            return f"{breadcrumb}\n\n{text}"
        return text

    def _build_metadata(self, chunk: Dict) -> Dict:
        """
        Extrait les métadonnées filtrables pour ChromaDB.
        ChromaDB n'accepte que des scalaires (str, int, float, bool) — pas de None ni de listes.
        """
        metadata = {}
        for field in METADATA_FIELDS:
            val = chunk.get(field, "")
            # Forcer les None → ""
            if val is None:
                val = ""
            # Forcer les types non-scalaires → str
            if isinstance(val, (list, dict)):
                val = json.dumps(val, ensure_ascii=False)
            metadata[field] = val
        return metadata

    def index_all(self, chunks: List[Dict], batch_size: int = 32) -> None:
        """Indexe les chunks dans les deux retrievers simultanément."""
        logger.info(f"\n{'='*60}")
        logger.info(f"[START] Indexation Hybride de {len(chunks)} chunks")
        logger.info(f"{'='*60}")

        # Filtrage qualité + déduplication avant indexation
        chunks = self.filter_chunks(chunks)
        logger.info(f"Chunks retenus pour indexation : {len(chunks)}")

        # Préparer les données pour ChromaDB
        ids        = [c["id"] for c in chunks]
        # Texte enrichi avec breadcrumb pour l'embedding (contextual embedding)
        documents  = [self._build_embedding_text(c) for c in chunks]
        metadatas  = [self._build_metadata(c) for c in chunks]

        # 1. Dense (ChromaDB)
        self.dense.create_collection()

        # Vérifier les IDs déjà présents pour éviter l'erreur sur relance
        existing_ids = set(self.dense.get_existing_ids())
        new_indices = [i for i, id_ in enumerate(ids) if id_ not in existing_ids]

        if not new_indices:
            logger.info("[DENSE] Tous les chunks sont déjà indexés, rien à faire.")
        else:
            skipped = len(chunks) - len(new_indices)
            if skipped:
                logger.info(f"[DENSE] {skipped} chunks déjà présents, {len(new_indices)} nouveaux à indexer")

            # Indexation par batch avec gestion d'erreur par batch
            success, failed = 0, 0
            for start in range(0, len(new_indices), batch_size):
                batch_idx = new_indices[start:start + batch_size]
                try:
                    self.dense.index_chunks(
                        ids=[ids[i] for i in batch_idx],
                        documents=[documents[i] for i in batch_idx],
                        metadatas=[metadatas[i] for i in batch_idx],
                    )
                    success += len(batch_idx)
                except Exception as e:
                    failed += len(batch_idx)
                    logger.error(f"[DENSE] Erreur batch {start}-{start + batch_size}: {e}")

            logger.info(f"[DENSE] {success} indexés, {failed} échoués")

        # 2. Sparse (BM25) — reconstruit toujours sur le texte pur (pas le breadcrumb)
        # BM25 travaille sur les tokens exacts : on veut le texte juridique brut
        self.sparse.build_index(chunks)

        logger.info(f"[SUCCESS] Indexation hybride complétée")

    def get_stats(self) -> Dict:
        """Statistiques combinées des deux index."""
        return {
            "dense": self.dense.get_stats(),
            "sparse": self.sparse.get_stats(),
        }


def main():
    """Pipeline principale d'embedding."""
    logger.info("[START] Démarrage pipeline d'embedding hybride")

    pipeline = EmbeddingsPipeline()
    chunks = pipeline.load_chunks()
    if not chunks:
        logger.error("Aucun chunk à indexer!")
        return None

    pipeline.index_all(chunks)

    stats = pipeline.get_stats()
    logger.info(f"\n{'='*60}")
    logger.info("[STATS] INDEXATION COMPLÉTÉE")
    logger.info(f"{'='*60}")
    for retriever_name, retriever_stats in stats.items():
        logger.info(f"\n{retriever_name}:")
        for key, value in retriever_stats.items():
            logger.info(f"  {key}: {value}")

    return pipeline


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    pipeline = main()
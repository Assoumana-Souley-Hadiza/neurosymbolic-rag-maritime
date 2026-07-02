"""
retrievers.py — Deux voies de retrieval documentaire pour le RAG Maritime.

Architecture :
  - DenseRetriever  : Recherche sémantique via ChromaDB + SentenceTransformer (bge-m3)
  - SparseRetriever : Recherche lexicale via BM25 avec tokenization améliorée

Note : Le troisième retriever (Graph) est dans neo4j_graph_retriever.py
       et utilise Cypher sur Neo4j au lieu de SPARQL sur un fichier OWL.
"""

import logging
import json
import pickle
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod

from rag.config import (
    CHUNKS_DIR, CHROMA_DB_DIR, CHROMA_CONFIG,
    EMBEDDING_CONFIG, BM25_INDEX_DIR
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# BASE RETRIEVER (Interface commune)
# ═══════════════════════════════════════════════════════════════════

class BaseRetriever(ABC):
    """Interface abstraite pour tous les retrievers."""

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 10, expanded_terms: Optional[List[str]] = None, country_filter: Optional[str] = None) -> List[Dict]:
        """Retourne une liste de résultats scorés."""
        ...

    @abstractmethod
    def is_ready(self) -> bool:
        """Vérifie si le retriever est opérationnel."""
        ...


# ═══════════════════════════════════════════════════════════════════
# DENSE RETRIEVER (Vectoriel — ChromaDB + SentenceTransformer)
# ═══════════════════════════════════════════════════════════════════

class DenseRetriever(BaseRetriever):
    """
    Recherche sémantique via embeddings denses.
    Utilise ChromaDB comme vector store et bge-m3 comme modèle d'embedding.
    """

    def __init__(self, collection_name: str = "maritime_docs"):
        import chromadb
        from sentence_transformers import SentenceTransformer

        logger.info("[INIT] Initialisation DenseRetriever...")
        self.collection: Any = None
        
        self.model = SentenceTransformer(
            EMBEDDING_CONFIG["model_name"],
            device=EMBEDDING_CONFIG["device"]
        )
        logger.info(
            f"  Modèle chargé: {EMBEDDING_CONFIG['model_name']} "
            f"(Dim: {EMBEDDING_CONFIG['embedding_dim']})"
        )

        self.client = chromadb.PersistentClient(
            path=CHROMA_CONFIG["persist_directory"]
        )

        # Tenter de récupérer une collection existante
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(
                f"  Collection '{collection_name}' chargée "
                f"({self.collection.count()} documents)"
            )
        except Exception:
            self.collection = None
            logger.warning(f"  Collection '{collection_name}' non trouvée.")

    def is_ready(self) -> bool:
        return self.collection is not None and self.collection.count() > 0

    def create_collection(self, collection_name: str = "maritime_docs") -> None:
        """Crée ou réinitialise une collection ChromaDB."""
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"  Collection existante supprimée: {collection_name}")
        except Exception:
            pass

        self.collection = self.client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"  Collection créée: {collection_name}")

    def get_existing_ids(self) -> List[str]:
        """
        Retourne la liste des IDs déjà présents dans la collection.
        Utilisé par embeddings_pipeline pour éviter les doublons sur relance.
        """
        if not self.collection:
            return []
        try:
            result = self.collection.get(include=[])   # include=[] = IDs seulement, pas de vecteurs
            return result["ids"]
        except Exception as e:
            logger.warning(f"  get_existing_ids: {e}")
            return []

    def index_chunks(
        self,
        # Forme 1 (appelée par embeddings_pipeline) : données déjà préparées
        ids: Optional[List[str]] = None,
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        # Forme 2 (rétrocompatibilité) : liste de chunks bruts
        chunks: Optional[List[Dict[str, Any]]] = None,
        batch_size: int = 32,
    ) -> None:
        """
        Indexe les chunks dans ChromaDB.

        Accepte deux formes d'appel :
          - index_chunks(ids=[...], documents=[...], metadatas=[...])
            → appelé par embeddings_pipeline (contextual embedding déjà appliqué)
          - index_chunks(chunks=[...])
            → appel direct legacy avec liste de chunks bruts
        """
        if not self.collection:
            raise ValueError("Collection non initialisée. Appelez create_collection().")

        # ── Normalisation des arguments ───────────────────────────────────
        if chunks is not None:
            # Forme legacy : on construit ids/documents/metadatas depuis les chunks
            ids       = [c["id"] for c in chunks]
            documents = [c["text"] for c in chunks]
            metadatas = [
                {
                    "source":        str(c.get("source", "")),
                    "category":      str(c.get("category", "")),
                    "country":       str(c.get("country", "")),
                    "page":          str(c.get("page", "")),
                    "word_count":    str(c.get("word_count", "")),
                    "quality_score": str(c.get("quality_score", "")),
                    "article":       str(c.get("article", "")),
                    "chapitre":      str(c.get("chapitre", "")),
                    "doc_type":      str(c.get("doc_type", "")),
                    "doc_number":    str(c.get("doc_number", "")),
                }
                for c in chunks
            ]

        if not ids or not documents or not metadatas:
            logger.warning("index_chunks: aucune donnée à indexer.")
            return

        logger.info(f"[START] Indexation vectorielle de {len(ids)} chunks...")
        total_batches = (len(ids) + batch_size - 1) // batch_size

        for batch_start in range(0, len(ids), batch_size):
            batch_end = min(batch_start + batch_size, len(ids))

            batch_ids       = ids[batch_start:batch_end]
            batch_documents = documents[batch_start:batch_end]
            batch_metadatas = metadatas[batch_start:batch_end]

            # Encoder les textes enrichis (breadcrumb + text)
            embeddings = self.model.encode(
                batch_documents, show_progress_bar=False
            )

            self.collection.add(
                ids=batch_ids,
                embeddings=embeddings.tolist(),
                documents=batch_documents,
                metadatas=batch_metadatas,
            )

            current_batch = (batch_start // batch_size) + 1
            if current_batch % 5 == 0 or current_batch == total_batches:
                logger.info(f"  [OK] Batch vectoriel {current_batch}/{total_batches}")

        logger.info("[SUCCESS] Indexation vectorielle complétée")

    def retrieve(self, query: str, top_k: Any = 10, expanded_terms: Optional[List[str]] = None, country_filter: Optional[str] = None) -> List[Dict]:
        top_k = int(top_k)
        """Recherche vectorielle par similarité cosinus avec Query Expansion."""
        if not self.is_ready():
            return []

        search_query = query
        if expanded_terms:
            unique_terms = list(dict.fromkeys(expanded_terms))[:8]  # Limit to 8 unique terms to avoid noise
            search_query = query + " " + " ".join(unique_terms)

        query_embedding = self.model.encode([search_query], show_progress_bar=False)[0]
        
        query_kwargs = {
            "query_embeddings": [query_embedding.tolist()],
            "n_results": top_k
        }
        if country_filter:
            query_kwargs["where"] = {"country": country_filter.capitalize()}

        results = self.collection.query(**query_kwargs)

        formatted = []
        if results["ids"] and len(results["ids"]) > 0:
            for rank, doc_id in enumerate(results["ids"][0]):
                distance = (
                    results["distances"][0][rank]
                    if "distances" in results else None
                )
                formatted.append({
                    "id": doc_id,
                    "rank": rank + 1,
                    "text": results["documents"][0][rank],
                    "metadata": results["metadatas"][0][rank],
                    "score": 1.0 - distance if distance is not None else 0.0,
                    "source_retriever": "dense",
                })

        return formatted

    def get_stats(self) -> Dict:
        stats = {
            "retriever": "dense",
            "model": EMBEDDING_CONFIG["model_name"],
            "embedding_dim": EMBEDDING_CONFIG["embedding_dim"],
        }
        if self.collection:
            stats["total_documents"] = self.collection.count()
            stats["collection_name"] = self.collection.name
        return stats


# ═══════════════════════════════════════════════════════════════════
# SPARSE RETRIEVER (Lexical — BM25 avec tokenization améliorée)
# ═══════════════════════════════════════════════════════════════════

class SparseRetriever(BaseRetriever):
    """
    Recherche lexicale via BM25Okapi.
    Utilise une tokenization par regex pour le français au lieu de .split().
    """

    # Regex tokenizer : garde les mots, apostrophes, tirets
    _TOKEN_RE = re.compile(r"[a-zà-ÿ0-9]+(?:[-'][a-zà-ÿ0-9]+)*", re.IGNORECASE)

    def __init__(self):
        logger.info("[INIT] Initialisation SparseRetriever (BM25)...")
        self.bm25 = None
        self.chunks: List[Dict] = []
        self._load_index()

    def _tokenize(self, text: str) -> List[str]:
        """Tokenization améliorée pour le français."""
        return self._TOKEN_RE.findall(text.lower())

    def _load_index(self) -> None:
        """Charge l'index BM25 persisté s'il existe."""
        index_path = BM25_INDEX_DIR / "bm25_index.pkl"
        chunks_path = BM25_INDEX_DIR / "bm25_chunks.pkl"

        if index_path.exists() and chunks_path.exists():
            try:
                with open(index_path, 'rb') as f:
                    self.bm25 = pickle.load(f)
                with open(chunks_path, 'rb') as f:
                    self.chunks = pickle.load(f)
                logger.info(f"  Index BM25 chargé ({len(self.chunks)} documents)")
            except Exception as e:
                logger.error(f"  Erreur chargement BM25: {e}")
                self.bm25 = None
                self.chunks = []

    def is_ready(self) -> bool:
        return self.bm25 is not None and len(self.chunks) > 0

    def build_index(self, chunks: List[Dict]) -> None:
        """
        Construit l'index BM25 sur le texte pur (pas le breadcrumb).
        BM25 travaille sur les tokens exacts — on veut le texte juridique brut.
        """
        from rank_bm25 import BM25Okapi

        logger.info(f"[START] Construction index BM25 ({len(chunks)} chunks)...")
        self.chunks = chunks

        tokenized_corpus = [self._tokenize(chunk["text"]) for chunk in chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

        # Persister l'index
        BM25_INDEX_DIR.mkdir(parents=True, exist_ok=True)
        with open(BM25_INDEX_DIR / "bm25_index.pkl", 'wb') as f:
            pickle.dump(self.bm25, f)
        with open(BM25_INDEX_DIR / "bm25_chunks.pkl", 'wb') as f:
            pickle.dump(self.chunks, f)

        logger.info("[SUCCESS] Index BM25 construit et persisté")

    def retrieve(self, query: str, top_k: Any = 10, expanded_terms: Optional[List[str]] = None, country_filter: Optional[str] = None) -> List[Dict]:
        top_k = int(top_k)
        """Recherche lexicale BM25 avec Query Expansion."""
        if not self.is_ready() or self.bm25 is None:
            return []

        tokenized_query = self._tokenize(query)
        if expanded_terms:
            for term in expanded_terms:
                tokenized_query.extend(self._tokenize(term))

        scores = self.bm25.get_scores(tokenized_query)

        # Trier par score décroissant
        sorted_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )

        top_indices = []
        for idx in sorted_indices:
            if scores[idx] <= 0:
                continue
            chunk = self.chunks[idx]
            if country_filter and str(chunk.get("country", "")).capitalize() != country_filter.capitalize():
                continue
            top_indices.append(idx)
            if len(top_indices) >= top_k:
                break

        formatted = []
        for rank, idx in enumerate(top_indices):
            if scores[idx] > 0:
                chunk = self.chunks[idx]
                formatted.append({
                    "id": chunk["id"],
                    "rank": rank + 1,
                    "text": chunk["text"],
                    "metadata": {
                        "source":   chunk.get("source", ""),
                        "category": chunk.get("category", ""),
                        "country":  chunk.get("country", ""),
                        "page":     str(chunk.get("page", "")),
                    },
                    "score": float(scores[idx]),
                    "source_retriever": "sparse",
                })

        return formatted

    def get_stats(self) -> Dict:
        return {
            "retriever": "sparse",
            "algorithm": "BM25Okapi",
            "tokenizer": "regex_french",
            "total_documents": len(self.chunks),
            "ready": self.is_ready(),
        }

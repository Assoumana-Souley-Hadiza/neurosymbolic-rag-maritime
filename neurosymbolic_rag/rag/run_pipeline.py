"""
run_pipeline.py — Orchestration complète du système RAG Maritime (v3 Neo4j).
Exécute les 3 phases : Extraction PDF → Indexation Hybride → Vérification
"""
import logging
import sys
import argparse
import json
from pathlib import Path

if sys.platform == "win32":
    for _stream_name in ("stdout", "stderr"):
        _stream = getattr(sys, _stream_name, None)
        if _stream is not None and hasattr(_stream, "reconfigure"):
            try:
                _stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.config import LOG_FILE, LOG_LEVEL, CHUNKS_DIR
from rag.ingestion.pdf_extractor import PDFExtractor
from rag.ingestion.embeddings_pipeline import EmbeddingsPipeline

# ── Remplacement de OntologyBridge (RDFLib) par Neo4jBridge ──────────────
from rag.integration.neo4j_bridge import Neo4jBridge
from rag.core.neo4j_graph_retriever import Neo4jGraphRetriever

from rag.core.retrievers import DenseRetriever, SparseRetriever
from rag.core.fusion import HybridFusion
from rag.core.query_analyzer import QueryAnalyzer

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def print_banner(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(description="Orchestration RAG Maritime v3")
    parser.add_argument("--skip-extraction", action="store_true")
    parser.add_argument("--skip-indexing",   action="store_true")
    args = parser.parse_args()

    print_banner("[START] RAG MARITIME HYBRIDE v3 (Neo4j) — DÉMARRAGE")

    try:
        chunks = []

        # ── PHASE 1: Extraction PDF ──────────────────────────────────────
        if not args.skip_extraction:
            print_banner("PHASE 1: EXTRACTION PDF")
            extractor = PDFExtractor()
            chunks, stats = extractor.process_all_pdfs()
            if not chunks:
                logger.error("[ERROR] Aucun chunk créé.")
                return False
            extractor.save_chunks(chunks)
            logger.info(f"[OK] Phase 1 — {len(chunks)} chunks créés")
        else:
            logger.info("[SKIP] Phase 1 sautée.")

        # ── PHASE 2: Indexation Hybride ──────────────────────────────────
        if not args.skip_indexing:
            print_banner("PHASE 2: INDEXATION HYBRIDE (Dense + Sparse)")
            if not chunks:
                chunk_file = CHUNKS_DIR / "all_chunks.json"
                if chunk_file.exists():
                    with open(chunk_file, 'r', encoding='utf-8') as f:
                        chunks = json.load(f)
                else:
                    logger.error("[ERROR] Aucun chunk trouvé.")
                    return False
            EmbeddingsPipeline().index_all(chunks)
            logger.info("[OK] Phase 2 complétée")
        else:
            logger.info("[SKIP] Phase 2 sautée.")

        # ── PHASE 3: Vérification ────────────────────────────────────────
        print_banner("PHASE 3: VÉRIFICATION HYBRIDE")

        dense    = DenseRetriever()
        sparse   = SparseRetriever()
        analyzer = QueryAnalyzer()
        fusion   = HybridFusion()

        # Connexion Neo4j (remplace OntologyBridge)
        neo4j_bridge    = Neo4jBridge.from_config()
        neo4j_retriever = Neo4jGraphRetriever(neo4j_bridge)

        if not neo4j_bridge or not neo4j_bridge.is_ready():
            logger.warning(
                "[Neo4j] Bridge non connecté. Le GraphRetriever sera ignoré. "
                "Vérifiez NEO4J_CONFIG dans rag/config.py."
            )

        test_queries = [
            "interdiction chasse à la baleine au Maroc",
            "rejets d'hydrocarbures en mer",
            "protection des cétacés au Sénégal",
            "extraction de sable côtier Bénin",
        ]

        for query in test_queries:
            intent, weights, country_filter, category_filter = analyzer.analyze(query)
            logger.info(
                f"\n[QUERY] '{query}' | intent={intent} | pays={country_filter} | cat={category_filter}"
            )

            retriever_results = {}

            # ── Obtenir les synonym_sets depuis Neo4j ──────────────────
            synonym_sets = {}
            expanded_terms = []
            if neo4j_bridge and neo4j_bridge.is_ready():
                import re
                words = re.findall(r"[a-zà-ÿ]{4,}", query.lower())
                synonym_sets = neo4j_bridge.get_synonyms_batch(words)
                for syns in synonym_sets.values():
                    expanded_terms.extend(list(syns))
                expanded_terms = list(set(expanded_terms))

            if dense and dense.is_ready():
                retriever_results["dense"]  = dense.retrieve(query, top_k=5, expanded_terms=expanded_terms)

            if sparse and sparse.is_ready():
                retriever_results["sparse"] = sparse.retrieve(query, top_k=5, expanded_terms=expanded_terms)

            if neo4j_retriever and neo4j_retriever.is_ready():
                retriever_results["graph"]  = neo4j_retriever.retrieve(query, top_k=5)

            results = fusion.fuse(
                retriever_results=retriever_results,
                weights=weights,
                synonym_sets=synonym_sets,
                ontology_boost=0.5,
                top_k=3,
                country_filter=country_filter,
                category_filter=category_filter,
                query=query,
            )

            for i, result in enumerate(results, 1):
                sources = result.get("retriever_sources", [])
                logger.info(
                    f"  {i}. [{'+'.join(sources)}] "
                    f"(Score: {result.get('hybrid_score', 0):.4f}) "
                    f"{result['text'][:80]}..."
                )

        # ── RÉSUMÉ FINAL ─────────────────────────────────────────────────
        neo4j_stats = neo4j_bridge.get_stats() if neo4j_bridge.is_ready() else {}
        node_counts = neo4j_stats.get("node_counts", {})

        print_banner("[OK] SYSTÈME RAG MARITIME v3 (Neo4j) INITIALISÉ")
        logger.info(f"""
Système prêt :
  [OK] Dense Retriever (ChromaDB + bge-m3)
  [OK] Sparse Retriever (BM25)
  [OK] Graph Retriever (Neo4j + Cypher)
       Nœuds : {node_counts}
  [OK] Fusion RRF + boost synonymes Neo4j
  [OK] Analyse d'intention + filtre pays

Lancer l'interface :
  streamlit run rag/api/app_streamlit.py
        """)
        return True

    except Exception as e:
        logger.error(f"[ERROR] Erreur fatale: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
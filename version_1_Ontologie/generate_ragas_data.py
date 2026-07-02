#!/usr/bin/env python3
"""
generate_ragas_data.py — Génère automatiquement le fichier ragas_data_*.json
à partir des questions de benchmark_queries.py.

Architecture calquée sur batch_query.py (pipeline Full neurosymbolique) :
  Dense enrichi + Sparse + Fusion RRF + Reranker + OntologyAgent
  LLM appelé via llm_gen.generate(query, fusion_results, intent, enriched_context, stream=True)

Pour chaque question :
  1. Analyse de la requête (QueryAnalyzer)
  2. Construction des synonymes via Neo4j (comme batch_query.py)
  3. Retrieval Dense (avec expanded_terms) + Sparse
  4. Fusion RRF + Reranker
  5. Enrichissement OntologyAgent
  6. Génération LLM (streaming → string)
  7. Extraction des textes de contexte depuis fusion_results
  8. Sauvegarde RAGAS : question / answer / contexts / ground_truth

Modes d'architecture (--arch) :
  classic        : Dense uniquement, pas de Sparse, pas d'expansion, pas d'OntologyAgent.
  sans_sparse    : Dense (pur) + OntologyAgent (pas de Sparse).
  sans_ontologie : Dense (pur) + Sparse (pas d'OntologyAgent, pas d'expansion).
  complete       : Pipeline Full neurosymbolique (défaut).

Usage :
    python generate_ragas_data.py                        # Pipeline Full (complete)
    python generate_ragas_data.py --arch classic         # RAG Classique
    python generate_ragas_data.py --arch sans_sparse     # Sans BM25
    python generate_ragas_data.py --arch sans_ontologie  # Sans OntologyAgent
    python generate_ragas_data.py --arch complete        # RAG Complet
    python generate_ragas_data.py --resume                # Reprend depuis checkpoint
    python generate_ragas_data.py --skip-piege            # Ignore les questions pièges
    python generate_ragas_data.py --dry-run               # Sans LLM ni retrieval
    python generate_ragas_data.py --k 10                  # Nombre de chunks (défaut: 6)
"""

import json
import re
import sys
import time
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

# Forcer UTF-8
for _stream in ("stdout", "stderr"):
    s = getattr(sys, _stream, None)
    if s and hasattr(s, "reconfigure"):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
logging.basicConfig(level=logging.WARNING, format="%(message)s")

from rag.core.fusion import HybridFusion
from rag.core.query_analyzer import QueryAnalyzer
from rag.llm_generator import LLMGenerator
from rag.integration.neo4j_bridge import Neo4jBridge
from rag.core.retrievers import DenseRetriever, SparseRetriever
from rag.neo4j_ontology_agent import Neo4jOntologyAgent

from benchmark_queries import BENCHMARK_QUERIES_EVAL as BENCHMARK_QUERIES

# Noms de pays pour filtrage bruit synonymes
_PAYS_NOMS = {
    "bénin", "cameroun", "comores", "congo", "côte d'ivoire", "djibouti",
    "gabon", "guinée", "madagascar", "maroc", "mauritanie", "sénégal",
    "togo", "tunisie",
}

# Les constantes _NOISE_WORDS et _ENGLISH_KW ont été supprimées car on utilise OntologyAgent.


# =============================================================================
# EXTRACTION DES CONTEXTES depuis les fusion_results
# =============================================================================

def extract_contexts(fusion_results: List[Dict]) -> List[str]:
    """
    Extrait les textes de contexte depuis les documents retournés par la fusion.
    Reproduit le format attendu par RAGAS : liste de strings.
    Inclut la référence source si disponible (comme dans les chunks réels).
    """
    contexts = []
    for doc in fusion_results:
        text = (
            doc.get("text")
            or doc.get("content")
            or doc.get("page_content")
            or ""
        )
        if not text:
            meta = doc.get("metadata", {})
            if isinstance(meta, dict):
                text = meta.get("text", "")

        if not text:
            continue

        # Construire la référence source (format chunks réels)
        meta = doc.get("metadata", {}) or {}
        parts = []
        for key in ("source", "document_id", "doc_id", "article", "pays", "country", "loi"):
            val = meta.get(key)
            if val:
                parts.append(str(val))

        # Identifiant de chunk si dispo
        chunk_id = doc.get("id") or doc.get("chunk_id") or meta.get("chunk_id")
        if chunk_id and chunk_id not in parts:
            parts.insert(0, str(chunk_id))

        prefix = f"[{' | '.join(parts)}]\n" if parts else ""
        contexts.append((prefix + text).strip())

    return contexts if contexts else ["Aucun contexte pertinent trouvé."]


# =============================================================================
# PIPELINE RAG COMPLET (calqué sur batch_query.py → interroger_question)
# =============================================================================

class RagasGenerator:

    def __init__(self):
        self.dense    = None
        self.sparse   = None
        self.bridge   = None
        self.agent    = None
        self.llm      = None
        self.fusion   = None
        self.qa       = None
        self._ready   = False

    def load(self):
        print("📦 Chargement des composants...")

        try:
            self.dense = DenseRetriever()
            print("  ✓ Dense Retriever")
        except Exception as e:
            print(f"  ✗ Dense Retriever : {e}")

        try:
            self.sparse = SparseRetriever()
            print("  ✓ Sparse Retriever")
        except Exception as e:
            print(f"  ✗ Sparse Retriever : {e}")

        try:
            self.bridge = Neo4jBridge.from_config()
            if self.bridge and self.bridge.is_ready():
                print("  ✓ Neo4j Bridge")
                self.agent = Neo4jOntologyAgent(self.bridge)
                print("  ✓ Ontology Agent")
            else:
                self.bridge = None
                print("  ✗ Neo4j Bridge (non connecté) — enrichissement désactivé")
        except Exception as e:
            print(f"  ✗ Neo4j Bridge/Agent : {e}")

        try:
            self.llm = LLMGenerator()
            print("  ✓ LLM Generator")
        except Exception as e:
            print(f"  ✗ LLM Generator : {e}")

        try:
            self.fusion = HybridFusion()
            print("  ✓ Hybrid Fusion")
        except Exception as e:
            print(f"  ✗ Hybrid Fusion : {e}")

        self.qa = QueryAnalyzer()
        print("  ✓ Query Analyzer")
        self._ready = True
        print()

    # -------------------------------------------------------------------------
    # Synonymes — reproduction exacte de batch_query.py
    # -------------------------------------------------------------------------

    def _build_synonyms(self, question: str, intent: str = None):
        """
        Construit synonym_sets, expanded_terms et graph_entities
        de la même façon que BatchQuerySystem.interroger_question().
        """
        synonym_sets   = {}
        expanded_terms = []
        graph_entities = set()

        if not self.agent or not self.agent.is_ready():
            return synonym_sets, expanded_terms, graph_entities

        query_context = self.agent.prepare_query(question, intent=intent)
        synonym_sets = query_context.get("synonyms_map", {})
        graph_entities = query_context.get("graph_entities", set())
        expanded_terms = query_context.get("expanded_terms", [])

        return synonym_sets, expanded_terms, graph_entities, query_context

    # -------------------------------------------------------------------------
    # Pipeline complet pour une question
    # -------------------------------------------------------------------------

    def process_question(self, q: Dict, k: int = 6, arch: str = "complete") -> Dict:
        """
        Exécute le pipeline RAG et retourne un dict au format RAGAS + métadonnées.

        arch='classic'        → Dense pur.
        arch='sans_sparse'    → Dense pur + Ontologie (pas de sparse).
        arch='sans_ontologie' → Dense pur + Sparse (pas d'enrichissement ontologie).
        arch='complete'       → Pipeline Full.
        """
        question     = str(q["question"])
        country      = q.get("country")
        ground_truth = q.get("ground_truth")
        q_id         = q.get("id", "")
        is_piege     = q.get("is_piege", False)

        _RETRIEVER_K = max(k * 2, 12)

        try:
            # ── 1. Analyse requête ──────────────────────────────────────────
            # On extrait le pays purement à partir de la question (comme dans l'application réelle)
            intent, weights, country_filter, category_filter = self.qa.analyze(question)

            use_sparse    = arch in ["complete", "sans_ontologie"]
            use_expansion = arch == "complete"
            use_ontology  = arch in ["complete", "sans_sparse"]

            # ── 2. Synonymes / expanded_terms ───────────────────────────────
            query_context = None
            if use_expansion:
                synonym_sets, expanded_terms, graph_entities, query_context = self._build_synonyms(question, intent=intent)
            else:
                synonym_sets, expanded_terms, graph_entities, query_context = {}, [], set(), None

            # ── 3. Retrieval Dense + Sparse ─────────────────────────────────
            retriever_results = {}

            if self.dense and self.dense.is_ready():
                retriever_results["dense"] = self.dense.retrieve(
                    question,
                    top_k=_RETRIEVER_K,
                    expanded_terms=expanded_terms if use_expansion else None,
                    country_filter=country_filter,
                )

            if use_sparse and self.sparse and self.sparse.is_ready():
                retriever_results["sparse"] = self.sparse.retrieve(
                    question,
                    top_k=_RETRIEVER_K,
                    expanded_terms=expanded_terms,
                    country_filter=country_filter,
                )

            if not retriever_results:
                raise RuntimeError("Aucun retriever actif")

            # ── 4. Fusion RRF + Reranker ────────────────────────────────────
            if arch == "classic":
                # CLASSIC STRICT: pas de rerank, pas de fusion, on prend le dense brut
                fused = retriever_results.get("dense", [])[:k]
            else:
                fused = self.fusion.fuse(
                    retriever_results=retriever_results,
                    weights=weights,
                    graph_entities=graph_entities,
                    synonym_sets=synonym_sets,
                    ontology_boost=0.5,
                    top_k=k,
                    country_filter=country_filter,
                    category_filter=category_filter,
                    query=question,
                    expanded_terms=expanded_terms if use_expansion else None,
                    disable_reranker=False,
                    intent=intent,
                )

            # ── 5. Enrichissement OntologyAgent ─────────────────────────────
            enriched_context = None
            if use_ontology and self.agent and self.agent.is_ready():
                try:
                    enriched_context = self.agent.enrich(question, fused, query_context=query_context)
                except Exception:
                    pass  # non bloquant

            # ── 6. Extraction des contextes (AVANT génération) ──────────────
            contexts = extract_contexts(fused)

            # ── 7. Génération LLM (streaming) ────────────────────────────────
            answer = "[Erreur génération]"
            if self.llm:
                resp = self.llm.generate(
                    query=question,
                    fusion_results=fused,
                    intent=intent,
                    enriched_context=enriched_context,
                    stream=True,
                )
                if resp.get("error"):
                    answer = f"[Erreur LLM : {resp['error']}]"
                else:
                    full = "".join(list(resp["stream_generator"]))
                    # Nettoyer les balises <analyse>...</analyse> comme batch_query.py
                    answer = re.sub(
                        r"<analyse>.*?(?:</analyse>|$)", "", full, flags=re.DOTALL
                    ).strip()

            return {
                # ── Champs RAGAS obligatoires ──
                "question":     question,
                "answer":       answer,
                "contexts":     contexts,
                "ground_truth": ground_truth,
                # ── Métadonnées traçabilité ──
                "id":           q_id,
                "axe":          q.get("axe", ""),
                "axe_label":    q.get("axe_label", ""),
                "theme":        q.get("theme", ""),
                "country":      country or "",
                "is_piege":     is_piege,
                "n_contexts":   len(fused),
                "n_synonyms":   sum(len(v) for v in synonym_sets.values()),
                "architecture": arch,
            }

        except Exception as e:
            return {
                "question":     question,
                "answer":       f"[Erreur : {e}]",
                "contexts":     [],
                "ground_truth": ground_truth,
                "id":           q_id,
                "axe":          q.get("axe", ""),
                "axe_label":    q.get("axe_label", ""),
                "theme":        q.get("theme", ""),
                "country":      country or "",
                "is_piege":     is_piege,
                "n_contexts":   0,
                "n_synonyms":   0,
                "architecture": arch,
            }


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Génère ragas_data_*.json à partir des questions benchmark"
    )
    parser.add_argument("--k",          type=int,  default=6,  help="Chunks par question (défaut: 6)")
    parser.add_argument("--skip-piege", action="store_true",   help="Ignorer les questions pièges")
    parser.add_argument("--resume",     action="store_true",   help="Reprendre depuis checkpoint")
    parser.add_argument("--dry-run",    action="store_true",   help="Test sans LLM ni retrieval")
    parser.add_argument("--arch",       type=str,  default="complete",
                        choices=["classic", "sans_sparse", "sans_ontologie", "complete"],
                        help="Architecture RAG (classic, sans_sparse, sans_ontologie, complete)")
    args = parser.parse_args()

    output_dir = Path("results/eval")
    output_dir.mkdir(parents=True, exist_ok=True)

    arch            = args.arch
    ts              = time.strftime("%Y%m%d_%H%M%S")
    output_file     = output_dir / f"ragas_data_{ts}_{arch}.json"
    checkpoint_file = output_dir / f"ragas_data_checkpoint_{arch}.json"

    # Filtrer les questions
    queries = list(BENCHMARK_QUERIES)
    if args.skip_piege:
        queries = [q for q in queries if not q.get("is_piege")]

    total_q    = len(queries)
    piege_q    = sum(1 for q in BENCHMARK_QUERIES if q.get("is_piege"))
    normale_q  = len(BENCHMARK_QUERIES) - piege_q

    labels = {
        "classic": "RAG Classique (Dense seul)",
        "sans_sparse": "RAG Sans Sparse (Dense pur + Ontologie)",
        "sans_ontologie": "RAG Sans Ontologie (Dense pur + Sparse)",
        "complete": "RAG Complet (Full Neurosymbolique)"
    }
    arch_label = labels.get(arch, arch)

    print("=" * 70)
    print(f"🚀 Génération RAGAS — {arch_label}")
    print(f"   Architecture : {arch}")
    print(f"   {len(BENCHMARK_QUERIES)} questions totales "
          f"({normale_q} normales · {piege_q} pièges)")
    print(f"   {total_q} questions à traiter · k={args.k} chunks/question")
    if args.skip_piege:
        print("   (questions pièges exclues)")
    print("=" * 70)

    # Charger checkpoint si reprise
    evaluated: List[Dict] = []
    done_ids: set         = set()

    if args.resume and checkpoint_file.exists():
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            evaluated = json.load(f)
        done_ids = {item["id"] for item in evaluated if item.get("id")}
        print(f"🔄 Reprise checkpoint : {len(evaluated)}/{total_q} déjà traitées.\n")

    # Charger le pipeline (sauf dry-run)
    gen = RagasGenerator()
    if not args.dry_run:
        gen.load()
    else:
        gen._ready = True
        print("⚠️  Mode DRY-RUN — pas d'appel au LLM ni au retriever.\n")

    errors = 0

    for i, q in enumerate(queries):
        q_id     = q.get("id", f"Q{i+1:03d}")
        question = str(q["question"])

        if q_id in done_ids:
            print(f"[{i+1:03d}/{total_q}] {q_id} — déjà traité, skip.")
            continue

        is_piege = q.get("is_piege", False)
        print(f"\n[{i+1:03d}/{total_q}] {q_id} {'🪤' if is_piege else '  '} "
              f"{question[:65]}{'…' if len(question) > 65 else ''}")
        print(f"  Pays: {q.get('country', 'N/A')} | "
              f"Thème: {q.get('theme', '?')} | "
              f"Axe {q.get('axe', '?')}: {q.get('axe_label', '')}")

        t0 = time.time()

        if args.dry_run:
            entry = {
                "question":     question,
                "answer":       "[DRY-RUN]",
                "contexts":     ["[DRY-RUN]"],
                "ground_truth": q.get("ground_truth"),
                "id":           q_id,
                "axe":          q.get("axe", ""),
                "axe_label":    q.get("axe_label", ""),
                "theme":        q.get("theme", ""),
                "country":      q.get("country", ""),
                "is_piege":     is_piege,
                "n_contexts":   0,
                "n_synonyms":   0,
                "architecture": arch,
            }
        else:
            entry = gen.process_question(q, k=args.k, arch=arch)

        elapsed = int((time.time() - t0) * 1000)
        has_err = str(entry.get("answer", "")).startswith("[Erreur")
        if has_err:
            errors += 1

        print(f"  {'❌' if has_err else '✓'} {elapsed}ms | "
              f"contexts={entry['n_contexts']} | "
              f"synonymes={entry['n_synonyms']}")
        if entry.get("ground_truth"):
            gt = str(entry["ground_truth"])
            print(f"  GT: {gt[:60]}{'…' if len(gt) > 60 else ''}")

        evaluated.append(entry)
        done_ids.add(q_id)

        # Checkpoint après chaque question
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(evaluated, f, ensure_ascii=False, indent=2)

        time.sleep(0.3)

    # ── Export final ──────────────────────────────────────────────────────────
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(evaluated, f, ensure_ascii=False, indent=2)

    # Supprimer checkpoint si aucune erreur
    if errors == 0 and checkpoint_file.exists():
        checkpoint_file.unlink()
        print("\n🗑️  Checkpoint supprimé.")

    has_gt = sum(1 for e in evaluated if e.get("ground_truth"))

    print("\n" + "=" * 70)
    print("✅ Génération terminée")
    print(f"   {len(evaluated)} questions traitées | {errors} erreur(s)")
    print(f"   {has_gt}/{len(evaluated)} ground_truth remplis")
    print(f"\n📁 {output_file}")
    if errors:
        print(f"📁 Checkpoint : {checkpoint_file}")
    print("\n➡️  Lancer ensuite : python run_benchmark.py --ragas-only")
    print("=" * 70)


if __name__ == "__main__":
    main()
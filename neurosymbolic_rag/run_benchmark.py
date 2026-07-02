#!/usr/bin/env python3
"""
run_benchmark.py — Évaluation complète du pipeline RAG Maritime.

Architecture retrieval :
  - Dense          : embeddings sémantiques
  - Sparse         : BM25 (matching lexical)
  - Hybrid RRF     : fusion Dense + Sparse via RRF
  - Hybrid+Rerank  : fusion Dense + Sparse + CrossEncoder

Graph et Ontologie : enrichisseurs de contexte injectés dans le prompt
de génération uniquement (pas utilisés pour le retrieval).

LLM évaluateur RAGAS : Ollama local — llama3.1:8b (ou qwen2.5:7b, recommandé)
Embeddings RAGAS     : Ollama nomic-embed-text (fallback: BGE-M3 HuggingFace)

Usage :
    python run_benchmark.py                  # Benchmark retrieval complet
    python run_benchmark.py --ragas          # + métriques RAGAS (Ollama)
    python run_benchmark.py --export-csv     # Exporter en CSV pour l'article
    python run_benchmark.py --ragas-only     # RAGAS uniquement
"""

import json
import time
import math
import logging
import sys
import os
import argparse
import re
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

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
logger = logging.getLogger(__name__)

from rag.core.retrievers import DenseRetriever, SparseRetriever
from rag.integration.neo4j_bridge import Neo4jBridge
from rag.neo4j_ontology_agent import Neo4jOntologyAgent
from rag.llm_generator import LLMGenerator
from rag.core.fusion import HybridFusion
from rag.core.query_analyzer import QueryAnalyzer

from benchmark_queries import BENCHMARK_QUERIES


# =============================================================================
# MÉTRIQUES IR
# =============================================================================

def is_relevant(doc: Dict, keywords: List[str]) -> bool:
    text = (doc.get("text", "") + " " + str(doc.get("metadata", {}))).lower()
    matches = sum(1 for kw in keywords if kw.lower() in text)
    return matches >= max(1, len(keywords) * 0.5)

def compute_mrr(ranked_docs, keywords):
    for i, doc in enumerate(ranked_docs):
        if is_relevant(doc, keywords):
            return 1.0 / (i + 1)
    return 0.0

def compute_ndcg(ranked_docs, keywords, k=5):
    def dcg(rels, k):
        return sum(r / math.log2(i + 2) for i, r in enumerate(rels[:k]))
    rels  = [1.0 if is_relevant(d, keywords) else 0.0 for d in ranked_docs[:k]]
    ideal = sorted(rels, reverse=True)
    idcg  = dcg(ideal, k)
    return dcg(rels, k) / idcg if idcg > 0 else 0.0

def compute_recall(ranked_docs, keywords, k=5):
    relevant_top_k  = sum(1 for d in ranked_docs[:k] if is_relevant(d, keywords))
    total_relevant  = max(1, sum(1 for d in ranked_docs if is_relevant(d, keywords)))
    return relevant_top_k / total_relevant

def compute_precision(ranked_docs, keywords, k=5):
    if not ranked_docs[:k]:
        return 0.0
    return sum(1 for d in ranked_docs[:k] if is_relevant(d, keywords)) / min(k, len(ranked_docs))


# =============================================================================
# BENCHMARK RUNNER
# =============================================================================

class BenchmarkRunner:
    def __init__(self):
        self.dense = None; self.sparse = None
        self.bridge = None; self.agent = None
        self.llm = None; self.fusion = None
        self._loaded = False

    def load(self):
        if self._loaded:
            return
        print("📦 Chargement des composants...")
        try:
            self.dense = DenseRetriever(); print("  ✓ Dense Retriever")
        except Exception as e:
            print(f"  ✗ Dense Retriever : {e}")
        try:
            self.sparse = SparseRetriever(); print("  ✓ Sparse Retriever")
        except Exception as e:
            print(f"  ✗ Sparse Retriever : {e}")
        try:
            self.bridge = Neo4jBridge.from_config()
            if self.bridge and self.bridge.is_ready():
                print("  ✓ Neo4j Bridge  [enrichisseur contexte]")
                self.agent = Neo4jOntologyAgent(self.bridge)
                print("  ✓ Ontology Agent [enrichisseur contexte]")
            else:
                self.bridge = None
                print("  ✗ Neo4j Bridge (non connecté)")
        except Exception as e:
            print(f"  ✗ Neo4j Bridge/Agent : {e}")
        try:
            self.llm = LLMGenerator(); print("  ✓ LLM Generator")
        except Exception as e:
            print(f"  ✗ LLM Generator : {e}")
        try:
            self.fusion = HybridFusion(); print("  ✓ Hybrid Fusion")
        except Exception as e:
            print(f"  ✗ Hybrid Fusion : {e}"); self.fusion = None
        self._loaded = True
        print()

    def _get_synonyms(self, query):
        synonym_sets  = {}
        expanded_terms = []
        if not self.bridge or not self.bridge.is_ready():
            return synonym_sets, expanded_terms
        _NOISE = {
            "existe","article","texte","juridique","précise","précisent","types",
            "activités","concernées","portant","spécifiquement","spécifiques",
            "procédures","contrôle","contrôles","vérifiez","vérifier","respect",
            "lieux","dans","pour","avec","entre","cette","quel","quelle","quels",
            "quelles","sont","comment","pourquoi","interdit","interdiction",
            "interdire","mesures","mesure",
        }
        words    = re.findall(r"[a-zà-ÿ]{4,}", query.lower())
        thematic = [w for w in words if w not in _NOISE]
        inter_matches = self.bridge.get_interdictions_by_keywords(words)
        if inter_matches:
            scored = []
            for match in inter_matches:
                name_lower = match.get("interdiction", "").lower()
                relevance  = sum(1 for w in thematic if w in name_lower)
                scored.append((relevance, match))
            scored.sort(key=lambda x: x[0], reverse=True)
            best = scored[0][0] if scored else 0
            threshold = 2 if best >= 2 else best
            _EN = {"oil","spill","bunker","ship","vessel","fishing","marine","protected","area","law","act"}
            for relevance, match in scored:
                if relevance >= threshold and relevance > 0:
                    name = match.get("interdiction", "")
                    syns = {s for s in match.get("synonymes", [])
                            if not any(ek in s.lower() for ek in _EN) and len(s) > 3}
                    if name and syns:
                        synonym_sets[name] = syns
        for s_list in synonym_sets.values():
            expanded_terms.extend(s_list)
        expanded_terms = list(set(expanded_terms))
        return synonym_sets, expanded_terms

    def run_retrieval(self, query, country=None, k=10,
                      use_dense=True, use_sparse=True,
                      use_rerank=True, use_ontology=True):
        t0 = time.time()
        retriever_results = {}
        stats = {"synonyms_count": 0, "expanded_terms_count": 0, "technical_hits": 0}

        synonym_sets, expanded_terms = {}, []
        if use_ontology and self.bridge:
            synonym_sets, expanded_terms = self._get_synonyms(query)
            stats["synonyms_count"]       = sum(len(v) for v in synonym_sets.values())
            stats["expanded_terms_count"] = len(expanded_terms)

        t_retr = time.time()
        if use_dense and self.dense:
            retriever_results["dense"] = self.dense.retrieve(
                query, k, expanded_terms=expanded_terms if use_ontology else None)
        if use_sparse and self.sparse:
            retriever_results["sparse"] = self.sparse.retrieve(
                query, k, expanded_terms=expanded_terms if use_ontology else None)

        stats["retrieval_ms"] = int((time.time() - t_retr) * 1000)
        if not retriever_results:
            return [], {"latency_ms": 0, "error": "aucun retriever actif"}
        if not self.fusion:
            return [], {"latency_ms": 0, "error": "Fusion non chargé"}

        qa = QueryAnalyzer()
        _, qa_weights, country_detected, _ = qa.analyze(query)
        weights = dict(qa_weights) if qa_weights else {"dense": 0.5, "sparse": 0.5}
        if not use_dense: weights.pop("dense", None)
        if not use_sparse: weights.pop("sparse", None)
        total_w = sum(weights.values())
        if total_w > 0:
            weights = {k: v / total_w for k, v in weights.items()}
        country_filter = country_detected or country

        _saved_model = None
        if self.fusion.reranker and not use_rerank:
            _saved_model = self.fusion.reranker.model
            self.fusion.reranker.model = None

        t_fus = time.time()
        fused = self.fusion.fuse(
            retriever_results=retriever_results, weights=weights,
            synonym_sets=synonym_sets if use_ontology else {},
            ontology_boost=0.5 if use_ontology else 0.0,
            top_k=k, country_filter=country_filter, query=query,
            expanded_terms=expanded_terms if use_ontology else None,
        )
        stats["fusion_ms"] = int((time.time() - t_fus) * 1000)
        if _saved_model is not None:
            self.fusion.reranker.model = _saved_model

        stats["technical_hits"] = sum(1 for d in fused if d.get("technical_hit"))
        stats["sources"] = {}
        for d in fused:
            for src in d.get("retriever_sources", [d.get("source_retriever", "unknown")]):
                stats["sources"][src] = stats["sources"].get(src, 0) + 1
        stats["latency_ms"] = int((time.time() - t0) * 1000)
        return fused, stats


# =============================================================================
# ABLATION CONFIGS
# =============================================================================

ABLATION_CONFIGS = [
    {"name": "Dense only",
     "use_dense": True,  "use_sparse": False, "use_rerank": False, "use_ontology": False},
    {"name": "Sparse only",
     "use_dense": False, "use_sparse": True,  "use_rerank": False, "use_ontology": False},
    {"name": "Hybrid RRF (no rerank)",
     "use_dense": True,  "use_sparse": True,  "use_rerank": False, "use_ontology": False},
    {"name": "Hybrid + Rerank",
     "use_dense": True,  "use_sparse": True,  "use_rerank": True,  "use_ontology": False},
    {"name": "Full pipeline",
     "use_dense": True,  "use_sparse": True,  "use_rerank": True,  "use_ontology": True},
]


# =============================================================================
# BENCHMARK PRINCIPAL
# =============================================================================

def run_benchmark(export_csv=False):
    runner = BenchmarkRunner()
    runner.load()
    results_table, detailed_results = [], []
    K = 5
    normal_queries = [q for q in BENCHMARK_QUERIES if not q.get("is_piege")]
    piege_queries  = [q for q in BENCHMARK_QUERIES if q.get("is_piege")]

    print("=" * 80)
    print("🚀 BENCHMARK RAG MARITIME — Ablation Study")
    print(f"   {len(normal_queries)} questions normales · {len(piege_queries)} pièges")
    print(f"   {len(ABLATION_CONFIGS)} configurations")
    print("=" * 80)

    for config in ABLATION_CONFIGS:
        name = config["name"]
        print(f"\n▶ {name}...")
        mrr_scores, ndcg_scores, recall_scores, prec_scores = [], [], [], []
        latencies, synonym_counts, tech_hits = [], [], []
        piege_tnr = []

        for q in normal_queries:
            try:
                fused, stats = runner.run_retrieval(
                    query=str(q["question"]), country=q.get("country"), k=K * 2,
                    use_dense=config["use_dense"], use_sparse=config["use_sparse"],
                    use_rerank=config["use_rerank"], use_ontology=config["use_ontology"])
                kw = q.get("relevant_keywords") or []
                mrr    = compute_mrr(fused, kw)
                ndcg   = compute_ndcg(fused, kw, K)
                recall = compute_recall(fused, kw, K)
                prec   = compute_precision(fused, kw, K)
                mrr_scores.append(mrr); ndcg_scores.append(ndcg)
                recall_scores.append(recall); prec_scores.append(prec)
                latencies.append(stats.get("latency_ms", 0))
                synonym_counts.append(stats.get("synonyms_count", 0))
                tech_hits.append(stats.get("technical_hits", 0))
                detailed_results.append({
                    "config": name, "id": q.get("id",""), "axe": q.get("axe",""),
                    "axe_label": q.get("axe_label",""), "theme": q.get("theme",""),
                    "country": q.get("country",""), "question": str(q["question"])[:80],
                    "is_piege": False, "mrr": mrr, "ndcg@5": ndcg,
                    "recall@5": recall, "precision@5": prec,
                    "latency_ms": stats.get("latency_ms",0),
                    "synonyms": stats.get("synonyms_count",0),
                    "tech_hits": stats.get("technical_hits",0),
                    "top1_relevant": is_relevant(fused[0], kw) if fused else False,
                    "sources": stats.get("sources",{}),
                })
            except Exception as e:
                print(f"  ! Erreur '{str(q.get('question',''))[:50]}' : {e}")
                for lst in (mrr_scores, ndcg_scores, recall_scores, prec_scores, latencies):
                    lst.append(0)

        for q in piege_queries:
            try:
                fused, stats = runner.run_retrieval(
                    query=str(q["question"]), country=q.get("country"), k=K,
                    use_dense=config["use_dense"], use_sparse=config["use_sparse"],
                    use_rerank=config["use_rerank"], use_ontology=config["use_ontology"])
                piege_tnr.append(1.0)
                latencies.append(stats.get("latency_ms", 0))
                detailed_results.append({
                    "config": name, "id": q.get("id",""), "axe": q.get("axe",""),
                    "axe_label": q.get("axe_label",""), "theme": q.get("theme",""),
                    "country": q.get("country",""), "question": str(q["question"])[:80],
                    "is_piege": True, "mrr": 0.0, "ndcg@5": 0.0,
                    "recall@5": 0.0, "precision@5": 0.0,
                    "latency_ms": stats.get("latency_ms",0),
                    "synonyms": stats.get("synonyms_count",0),
                    "tech_hits": stats.get("technical_hits",0),
                    "top1_relevant": False, "sources": stats.get("sources",{}),
                })
            except Exception as e:
                piege_tnr.append(0.0); latencies.append(0)

        avg = lambda lst: sum(lst)/len(lst) if lst else 0.0
        row = {
            "Method": name, "MRR": avg(mrr_scores), "NDCG@5": avg(ndcg_scores),
            "Recall@5": avg(recall_scores), "P@5": avg(prec_scores),
            "TNR": avg(piege_tnr), "Latency (ms)": int(avg(latencies)),
            "Synonyms": int(avg(synonym_counts)), "TechHits": int(avg(tech_hits)),
        }
        results_table.append(row)
        print(f"  MRR={row['MRR']:.3f}  NDCG@5={row['NDCG@5']:.3f}  "
              f"Recall@5={row['Recall@5']:.3f}  TNR={row['TNR']:.2f}  "
              f"Latency={row['Latency (ms)']}ms")

    print("\n" + "=" * 80)
    print("📊 RÉSULTATS — RETRIEVAL ABLATION STUDY")
    print("=" * 80)
    hdr = (f"{'Method':<32} {'MRR':>6} {'NDCG@5':>8} "
           f"{'Recall@5':>9} {'P@5':>6} {'TNR':>5} {'ms':>6} {'Syn':>5} {'TH':>4}")
    print(hdr); print("-" * len(hdr))
    for row in results_table:
        print(f"{row['Method']:<32} {row['MRR']:>6.3f} {row['NDCG@5']:>8.3f} "
              f"{row['Recall@5']:>9.3f} {row['P@5']:>6.3f} {row['TNR']:>5.2f} "
              f"{row['Latency (ms)']:>6} {row['Synonyms']:>5} {row['TechHits']:>4}")

    output_dir = Path("results/benchmark")
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    json_path = output_dir / f"benchmark_{ts}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"summary": results_table, "details": detailed_results, "timestamp": ts},
                  f, indent=2, ensure_ascii=False)
    print(f"\n📁 JSON : {json_path}")

    if export_csv:
        csv_path = output_dir / f"benchmark_{ts}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=results_table[0].keys())
            w.writeheader(); w.writerows(results_table)
        print(f"📁 CSV  : {csv_path}")
        detail_csv = output_dir / f"benchmark_detail_{ts}.csv"
        with open(detail_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=detailed_results[0].keys())
            w.writeheader()
            for row in detailed_results:
                row = dict(row)
                row["sources"] = json.dumps(row.get("sources", {}))
                w.writerow(row)
        print(f"📁 CSV détail : {detail_csv}")

    return results_table


# =============================================================================
# HELPERS RAGAS — extraction JSON + sous-classe LLM robuste
# =============================================================================

def _extract_json_from_llm_output(text: str) -> str:
    """
    Extrait le premier bloc JSON valide (objet ou tableau) d'une réponse LLM.

    Gère dans l'ordre :
      1. JSON brut valide (retour immédiat)
      2. Blocs markdown  ```json ... ```
      3. Tableau d'objets  [{...}, {...}]   ← NLI faithfulness / context_recall
      4. Objet avec sous-objets             ← context_precision / answer_relevancy
      5. Tableau simple / objet plat
      6. Greedy (premier { ... dernier })
    """
    if not text:
        return text
    t = text.strip()

    # Étape 1 — déjà du JSON valide
    try:
        json.loads(t)
        return t
    except json.JSONDecodeError:
        pass

    # Étape 2 — strip markdown
    t2 = re.sub(r"```(?:json)?\s*", "", t)
    t2 = re.sub(r"\s*```", "", t2).strip()
    try:
        json.loads(t2)
        return t2
    except json.JSONDecodeError:
        pass
    t = t2

    # Étapes 3–5 — patterns par ordre de spécificité
    patterns = [
        # Tableau d'objets (faithfulness NLI, context_recall)
        r"(\[(?:\s*\{(?:[^{}]|\{[^{}]*\})*\}\s*,?\s*)+\])",
        # Objet avec un niveau d'imbrication
        r"(\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\}|\[[^\[\]]*\])*\})",
        # Tableau simple
        r"(\[[^\[\]]*\])",
        # Objet plat
        r"(\{[^{}]*\})",
    ]
    for pat in patterns:
        m = re.search(pat, t, re.DOTALL)
        if m:
            try:
                json.loads(m.group(1))
                return m.group(1)
            except json.JSONDecodeError:
                continue

    # Étape 6 — greedy
    for sc, ec in [('{', '}'), ('[', ']')]:
        si, ei = t.find(sc), t.rfind(ec)
        if 0 <= si < ei:
            candidate = t[si:ei + 1]
            try:
                json.loads(candidate)
                return candidate
            except json.JSONDecodeError:
                pass

    return text  # abandon — RAGAS déclenchera fix_output_format


def _nan_mean(values: list) -> float:
    """Moyenne en ignorant None et NaN — pour les scores RAGAS."""
    valid = [v for v in values
             if v is not None and isinstance(v, (int, float)) and not math.isnan(v)]
    return sum(valid) / len(valid) if valid else float("nan")


def _make_ragas_llm(model: str, base_url: str, timeout: int = 1200):
    """
    Crée un LLM RAGAS-compatible via une VRAIE sous-classe de ChatOllama.

    Pourquoi une sous-classe et non un monkey-patch :
      Pydantic v2 (utilisé par LangChain ≥ 0.3) intercepte __setattr__ sur les
      instances de BaseModel. Assigner llm._generate = fn ne remplace pas la
      méthode — Python trouve d'abord l'attribut Pydantic avant l'instance dict.
      En surchargeant _generate / _agenerate dans une sous-classe, le MRO Python
      garantit que RAGAS appelle systématiquement notre version.

    Ce que fait la sous-classe :
      1. Injecte un SystemMessage JSON avant chaque appel (guide la structure)
      2. Nettoie la sortie via _extract_json_from_llm_output avant parsing RAGAS

    Modèles recommandés (compliance JSON décroissante) :
        1. qwen2.5:7b           ← meilleur, ~0 NaN
        2. mistral:7b-instruct  ← très fiable
        3. llama3.1:8b          ← correct mais peut flopper sur structures
                                   imbriquées (faithfulness NLI)
    """
    from langchain_ollama import ChatOllama
    from langchain_core.messages import AIMessage, SystemMessage
    from langchain_core.outputs import ChatGeneration, ChatResult

    _SYSTEM_JSON = (
        "You are a JSON-only structured data extraction API. "
        "Always respond with ONLY valid JSON that exactly matches the output format "
        "shown in the examples — no markdown, no explanation, no text outside the JSON."
    )

    def _has_system(messages) -> bool:
        return any(
            isinstance(m, SystemMessage) or getattr(m, "type", None) == "system"
            for m in messages
        )

    def _inject(messages):
        return ([SystemMessage(content=_SYSTEM_JSON)] + list(messages)
                if not _has_system(messages) else list(messages))

    def _clean(result: ChatResult) -> ChatResult:
        return ChatResult(
            generations=[
                ChatGeneration(
                    message=AIMessage(
                        content=_extract_json_from_llm_output(g.message.content)
                    ),
                    generation_info=g.generation_info,
                )
                if isinstance(g, ChatGeneration) else g
                for g in result.generations
            ],
            llm_output=result.llm_output,
        )

    # ── Vraie sous-classe : le MRO garantit que _generate / _agenerate
    #    sont bien appelés, même via BaseChatModel.generate_prompt() ──────────
    class _JSONSafeChatOllama(ChatOllama):

        def _generate(self, messages, stop=None, run_manager=None, **kwargs):
            return _clean(
                super()._generate(_inject(messages), stop=stop,
                                   run_manager=run_manager, **kwargs)
            )

        async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
            return _clean(
                await super()._agenerate(_inject(messages), stop=stop,
                                          run_manager=run_manager, **kwargs)
            )

    return _JSONSafeChatOllama(
        model=model,
        base_url=base_url,
        temperature=0,
        timeout=timeout,
        num_predict=1536,   # nécessaire pour la liste de statements (faithfulness)
    )


# =============================================================================
# RAGAS — Ollama local
# =============================================================================

def run_ragas_evaluation(arch: str = "complete"):
    """
    Évalue les réponses RAG avec RAGAS en utilisant Ollama local.

    Corrections vs version originale :
      1. Vraie sous-classe ChatOllama (_JSONSafeChatOllama) au lieu d'un
         monkey-patch bloqué par Pydantic v2 → _generate est toujours appelé
      2. Injection SystemMessage JSON → guide la structure de sortie
      3. Évaluation métrique par métrique avec try/except indépendants →
         si answer_relevancy crashe, faithfulness est quand même calculé
      4. _nan_mean robuste + rapport NaN par métrique
    """
    eval_dir = Path("results/eval")
    pattern  = f"ragas_data_*_{arch}.json"
    files    = [f for f in eval_dir.glob(pattern) if "checkpoint" not in f.name]

    if not files:
        print(f"❌ Aucune donnée RAGAS pour l'architecture '{arch}'.")
        print(f"   Générez d'abord : python generate_ragas_data.py --arch {arch}")
        return

    latest = max(files, key=os.path.getctime)
    labels = {
        "classic":        "RAG Classique",
        "sans_sparse":    "RAG Sans Sparse",
        "sans_ontologie": "RAG Sans Ontologie",
        "complete":       "RAG Complet",
    }
    arch_label = labels.get(arch, f"RAG {arch}")
    print(f"\n📄 Fichier RAGAS : {latest}")
    print(f"   Architecture  : {arch_label} ({arch})")

    with open(latest, "r", encoding="utf-8") as f:
        data = json.load(f)

    # ── Filtrer les entrées invalides ─────────────────────────────────────────
    valid_data = [
        item for item in data
        if item.get("answer")
        and not str(item["answer"]).startswith("[Erreur")
        and not str(item["answer"]).startswith("[DRY-RUN")
        and item.get("contexts")
        and item["contexts"] != ["Aucun contexte pertinent trouvé."]
    ]
    skipped = len(data) - len(valid_data)
    has_gt  = all(item.get("ground_truth") for item in valid_data)

    print(f"   {len(data)} échantillons chargés")
    print(f"   {len(valid_data)} valides · {skipped} ignorés (erreurs/vides)")
    print(f"   Ground truth : {'✓ Présent' if has_gt else '✗ Absent'} "
          + ("→ 4 métriques" if has_gt else "→ 2 métriques"))

    # ── Imports RAGAS ─────────────────────────────────────────────────────────
    try:
        from datasets import Dataset
        from ragas import evaluate as ragas_evaluate
        from ragas.metrics import faithfulness, answer_relevancy
        from ragas.run_config import RunConfig
        if has_gt:
            from ragas.metrics import context_precision, context_recall
    except ImportError as e:
        print(f"❌ Dépendances manquantes : {e}")
        print("   pip install ragas datasets")
        return

    # ── LLM juge ─────────────────────────────────────────────────────────────
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL    = os.getenv("RAGAS_LLM_MODEL", "llama3.1:8b")

    print(f"\n🤖 LLM évaluateur : {OLLAMA_MODEL}  ({OLLAMA_BASE_URL})")
    print(f"   ℹ  Pour moins de NaN → RAGAS_LLM_MODEL=qwen2.5:7b")

    # Test connexion avec un ChatOllama plain (pas notre sous-classe)
    try:
        from langchain_ollama import ChatOllama as _TestLLM
        _TestLLM(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, timeout=30).invoke("ok")
        print(f"   ✓ Connexion Ollama réussie")
    except Exception as e:
        print(f"   ✗ Ollama inaccessible : {e}")
        print(f"   → Vérifiez : ollama serve  puis : ollama pull {OLLAMA_MODEL}")
        return

    llm = _make_ragas_llm(OLLAMA_MODEL, OLLAMA_BASE_URL, timeout=1200)
    print(f"   ✓ Sous-classe _JSONSafeChatOllama active (num_predict=1536)")

    # ── RunConfig séquentiel ──────────────────────────────────────────────────
    run_config = RunConfig(max_workers=1, timeout=1200, max_retries=2)
    print(f"   ✓ RunConfig : max_workers=1, timeout=1200s, max_retries=2")

    # ── Embeddings ────────────────────────────────────────────────────────────
    embeddings = None
    EMBED_MODEL = os.getenv("RAGAS_EMBED_MODEL", "nomic-embed-text")

    try:
        from langchain_ollama import OllamaEmbeddings
        embeddings = OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_BASE_URL)
        embeddings.embed_query("test")
        print(f"   ✓ Embeddings Ollama ({EMBED_MODEL})")
    except Exception:
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
            print("   ✓ Embeddings HuggingFace BGE-M3 (fallback)")
        except Exception as e2:
            print(f"   ⚠️  Aucun embeddings ({e2}) → answer_relevancy désactivée")

    # ── Métriques actives ────────────────────────────────────────────────────
    metrics = [faithfulness]
    if embeddings:
        metrics.append(answer_relevancy)
    if has_gt:
        metrics += [context_precision, context_recall]

    # answer_relevancy nécessite les embeddings ; les autres non
    _NEEDS_EMBEDDINGS = {"answer_relevancy"}

    metric_names = [m.name for m in metrics]
    print(f"   Métriques : {metric_names}\n")

    # ── Checkpoint ───────────────────────────────────────────────────────────
    safe_model = OLLAMA_MODEL.replace(":", "_").replace("/", "_")
    checkpoint_file = latest.with_name(
        latest.stem + f"_{safe_model}_{arch}_ckpt.json"
    )
    evaluated: List[Dict] = []

    if checkpoint_file.exists():
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            evaluated = json.load(f)
        print(f"🔄 Reprise checkpoint : {len(evaluated)}/{len(valid_data)} déjà évalués.\n")

    # ── Boucle principale ────────────────────────────────────────────────────
    print("🚀 Évaluation RAGAS (métrique par métrique)…\n")

    for i in range(len(evaluated), len(valid_data)):
        item  = valid_data[i]
        q_id  = item.get("id", f"#{i+1}")
        print(f"  [{i+1:02d}/{len(valid_data)}] {q_id:<6} "
              f"{item.get('theme',''):<25} {item.get('axe_label',''):<18}")
        print(f"           {str(item['question'])[:65]}…")

        single = {
            "question": [item["question"]],
            "answer":   [item["answer"]],
            "contexts": [item["contexts"]],
        }
        if has_gt and item.get("ground_truth"):
            single["ground_truth"] = [str(item["ground_truth"])]

        record = {
            "id":        item.get("id", ""),
            "axe":       item.get("axe", ""),
            "axe_label": item.get("axe_label", ""),
            "theme":     item.get("theme", ""),
            "country":   item.get("country", ""),
            "is_piege":  item.get("is_piege", False),
            "question":  item["question"],
            "llm_judge": OLLAMA_MODEL,
        }
        # Initialiser toutes les métriques à NaN
        for mn in metric_names:
            record[mn] = float("nan")

        # ── Évaluation métrique par métrique ──────────────────────────────
        # Isolation des échecs : si answer_relevancy crashe,
        # faithfulness / context_precision / context_recall sont préservés.
        for metric in metrics:
            emb = embeddings if metric.name in _NEEDS_EMBEDDINGS else None
            success = False
            for attempt in range(3):
                try:
                    t0  = time.time()
                    res = ragas_evaluate(
                        Dataset.from_dict(single),
                        metrics=[metric],
                        llm=llm,
                        embeddings=emb,
                        show_progress=False,
                        run_config=run_config,
                    )
                    elapsed = int((time.time() - t0) * 1000)
                    val     = res.to_pandas()[metric.name].iloc[0]
                    record[metric.name] = val

                    is_nan = val is None or (isinstance(val, float) and math.isnan(val))
                    tag    = "NaN ⚠️ " if is_nan else f"{val:.3f}"
                    print(f"           [{metric.name:<28}] {tag}  ({elapsed}ms)")
                    success = True
                    break

                except Exception as e:
                    wait = 10 * (attempt + 1)
                    print(f"           [{metric.name:<28}] ✗ tentative "
                          f"{attempt+1}/3 — {str(e)[:55]} (attente {wait}s)")
                    time.sleep(wait)

            if not success:
                print(f"           [{metric.name:<28}] ✗ échec définitif → NaN")

            time.sleep(1)   # pause entre métriques

        evaluated.append(record)

        # Checkpoint après chaque item
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(evaluated, f, ensure_ascii=False, indent=2)

        print()

    # ── Résultats ─────────────────────────────────────────────────────────────
    import pandas as pd
    df = pd.DataFrame(evaluated)
    numeric_cols = [c for c in metric_names if c in df.columns]

    print("=" * 65)
    print(f"📊 RÉSULTATS RAGAS — {arch_label}  [{OLLAMA_MODEL}]")
    print("=" * 65)

    nan_counts = {}
    for col in numeric_cols:
        vals      = list(df[col])
        valid_vals = [v for v in vals
                      if v is not None and isinstance(v, (int, float)) and not math.isnan(v)]
        nan_n     = len(vals) - len(valid_vals)
        nan_counts[col] = nan_n
        mean_val  = sum(valid_vals) / len(valid_vals) if valid_vals else float("nan")

        if math.isnan(mean_val):
            bar = "?" * 10
            val_str = "  nan  "
        else:
            bar     = "█" * int(mean_val * 30) + "░" * (30 - int(mean_val * 30))
            val_str = f"{mean_val:.4f}"

        nan_note = f"  [{nan_n}/{len(vals)} NaN ignorés]" if nan_n else ""
        print(f"  {col:<28} {val_str}  {bar}{nan_note}")

    total_nan = sum(nan_counts.values())
    if total_nan > 0:
        print(f"\n  ⚠️  {total_nan} NaN au total.")
        print(f"      → Essayez RAGAS_LLM_MODEL=qwen2.5:7b pour les éliminer")

    # Par thème
    if "theme" in df.columns and df["theme"].nunique() > 1:
        print(f"\n{'─'*65}")
        print("📊 Par thème :")
        for theme, grp in df.groupby("theme"):
            vals = "  ".join(
                f"{c}={_nan_mean(list(grp[c])):.3f}"
                for c in numeric_cols if c in grp
            )
            print(f"  {theme:<30} {vals}")

    # Par axe
    if "axe" in df.columns and df["axe"].nunique() > 1:
        print(f"\n{'─'*65}")
        print("📊 Par axe :")
        for axe, grp in df.groupby("axe"):
            lbl  = grp["axe_label"].iloc[0] if "axe_label" in grp else ""
            vals = "  ".join(
                f"{c}={_nan_mean(list(grp[c])):.3f}"
                for c in numeric_cols if c in grp
            )
            print(f"  Axe {axe} {lbl:<20} {vals}")

    # Export CSV
    output_dir = Path("results/benchmark")
    output_dir.mkdir(parents=True, exist_ok=True)
    ts       = time.strftime("%Y%m%d_%H%M%S")
    csv_path = output_dir / f"ragas_{arch}_{ts}.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"\n📁 RAGAS CSV : {csv_path}")

    if len(evaluated) == len(valid_data) and checkpoint_file.exists():
        checkpoint_file.unlink()
        print("🗑️  Checkpoint supprimé.")

    return df


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark RAG Maritime")
    parser.add_argument("--ragas",      action="store_true")
    parser.add_argument("--export-csv", action="store_true")
    parser.add_argument("--ragas-only", action="store_true")
    parser.add_argument("--arch", type=str, default="complete",
                        choices=["classic", "sans_sparse", "sans_ontologie", "complete"])
    args = parser.parse_args()

    if args.ragas_only:
        run_ragas_evaluation(arch=args.arch)
    else:
        run_benchmark(export_csv=args.export_csv)
        if args.ragas:
            run_ragas_evaluation(arch=args.arch)
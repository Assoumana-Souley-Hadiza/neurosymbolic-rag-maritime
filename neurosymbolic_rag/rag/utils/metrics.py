"""
metrics.py — Enregistrement des métriques de qualité et performance du RAG.

Permet d'exporter les requêtes et résultats pour analyse offline.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class RetrievalMetrics:
    """Enregistre les métriques de retrieval et LLM generation."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metrics: List[Dict[str, Any]] = []

    def log_query(
        self,
        query: str,
        intent: str,
        weights: Dict[str, float],
        sources_retrieved: Dict[str, int],  # {"dense": 5, "sparse": 5, "graph": 3}
        top_scores: Dict[str, float],  # {"dense": 0.92, "sparse": 0.85, "graph": 0.78}
        response_time_ms: int,
        country_filter: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """Enregistre une requête et ses résultats."""
        self.metrics.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query": query[:200],  # Limiter la longueur
            "intent": intent,
            "weights": weights,
            "sources_retrieved": sources_retrieved,
            "top_scores": top_scores,
            "response_time_ms": response_time_ms,
            "country_filter": country_filter,
            "user_id": user_id,
        })

    def log_generation(
        self,
        query: str,
        response: str,
        tokens_generated: int,
        generation_time_ms: int,
        model: str = "mistral",
    ) -> None:
        """Enregistre la génération LLM."""
        self.metrics.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "generation",
            "query": query[:200],
            "response_preview": response[:300],
            "tokens_generated": tokens_generated,
            "generation_time_ms": generation_time_ms,
            "model": model,
        })

    def log_retriever_error(
        self,
        retriever_name: str,
        query: str,
        error: str,
    ) -> None:
        """Enregistre une erreur de retriever."""
        self.metrics.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "error",
            "retriever": retriever_name,
            "query": query[:200],
            "error": error[:500],
        })

    def export_json(self, filename: Optional[str] = None) -> Path:
        """Exporte les métriques en JSON."""
        if filename is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"metrics_{timestamp}.json"

        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Métriques exportées: {filepath}")
        return filepath

    def export_csv(self, filename: Optional[str] = None) -> Path:
        """Exporte les métriques en CSV (format simple)."""
        import csv

        if filename is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"metrics_{timestamp}.csv"

        filepath = self.output_dir / filename

        # Extraire les clés uniques
        all_keys = set()
        for metric in self.metrics:
            all_keys.update(metric.keys())

        all_keys = sorted(list(all_keys))

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_keys)
            writer.writeheader()
            for metric in self.metrics:
                # Convertir les dicts/listes en JSON strings
                row = {}
                for key, value in metric.items():
                    if isinstance(value, (dict, list)):
                        row[key] = json.dumps(value)
                    else:
                        row[key] = value
                writer.writerow(row)

        logger.info(f"✅ Métriques CSV exportées: {filepath}")
        return filepath

    def log_fusion_impact(
        self,
        query: str,
        fused_results: List[Dict],
        retriever_results: Dict[str, List[Dict]],
        boost_count: int = 0
    ) -> None:
        """Calcule et logue l'impact de chaque composant sur la fusion finale."""
        top_k_sources = [r.get("source_retriever", "unknown") for r in fused_results]
        source_counts = {s: top_k_sources.count(s) for s in set(top_k_sources)}
        
        # Calculer la "pureté" (combien de docs sont trouvés par plusieurs retrievers)
        multi_retriever_count = sum(1 for r in fused_results if r.get("multi_retriever", False))

        self.metrics.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "fusion_impact",
            "query": query[:200],
            "top_k_distribution": source_counts,
            "multi_retriever_overlap": multi_retriever_count,
            "ontology_boosts_applied": boost_count,
            "total_candidates": sum(len(v) for v in retriever_results.values())
        })

    def summary_stats(self) -> Dict[str, Any]:
        """Retourne un résumé statistique des métriques."""
        if not self.metrics:
            return {}

        queries = [m for m in self.metrics if m.get("event_type") == "fusion_impact"]
        gens = [m for m in self.metrics if m.get("event_type") == "generation"]
        
        response_times = [m.get("response_time_ms", 0) for m in self.metrics if "response_time_ms" in m]
        
        # Moyenne de contribution du graphe
        graph_contrib = [m.get("top_k_distribution", {}).get("graph", 0) for m in queries]
        avg_graph_contrib = sum(graph_contrib) / len(graph_contrib) if graph_contrib else 0

        return {
            "total_queries": len(queries),
            "avg_response_time_ms": sum(response_times) / len(response_times) if response_times else 0,
            "avg_graph_contribution": avg_graph_contrib,
            "avg_tokens_generated": sum(m.get("tokens_generated", 0) for m in gens) / len(gens) if gens else 0,
            "total_boosts": sum(m.get("ontology_boosts_applied", 0) for m in queries)
        }

    def print_summary(self) -> None:
        """Affiche un résumé des métriques."""
        stats = self.summary_stats()
        logger.info("📊 RÉSUMÉ DES MÉTRIQUES:")
        logger.info(f"  Total requêtes: {stats.get('total_queries', 0)}")
        logger.info(f"  Total erreurs: {stats.get('total_errors', 0)}")
        logger.info(f"  Temps moyen: {stats.get('avg_response_time_ms', 0):.0f}ms")


def get_metrics_logger(output_dir: Path) -> RetrievalMetrics:
    """Factory pour accéder à RetrievalMetrics."""
    return RetrievalMetrics(output_dir)

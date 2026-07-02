#!/usr/bin/env python3
"""
Maritime Ontology & RAG — Point d'entrée unifié.

Usage:
    python main.py ontology              # Pipeline ontologie complète
    python main.py ontology --validate   # Validation OWL uniquement
    python main.py ontology --sparql-only # Questions SPARQL uniquement
    python main.py rag                   # Pipeline RAG complète
    python main.py rag --check           # Vérifier l'environnement RAG
"""

import sys
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Maritime Ontology & RAG — Pipeline Unifié",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python main.py ontology                 Lancer le pipeline ontologique
  python main.py ontology --validate      Valider l'ontologie OWL
  python main.py rag                      Lancer le pipeline RAG complet
  python main.py rag --check              Vérifier l'environnement
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commande à exécuter")

    # ── Sous-commande: ontology ──────────────────────────────────
    onto_parser = subparsers.add_parser(
        "ontology", help="Pipeline ontologique (LKIF-Core)"
    )
    onto_parser.add_argument(
        "--config", default="data/config/settings.yaml",
        help="Chemin vers le fichier de configuration"
    )
    onto_parser.add_argument(
        "--sparql-only", action="store_true",
        help="Questions SPARQL uniquement"
    )
    onto_parser.add_argument(
        "--neo4j-only", action="store_true",
        help="Export Neo4j uniquement"
    )
    onto_parser.add_argument(
        "--validate", action="store_true",
        help="Valider l'ontologie OWL"
    )
    onto_parser.add_argument(
        "--no-neo4j", action="store_true",
        help="Désactiver l'export Neo4j"
    )

    # ── Sous-commande: rag ───────────────────────────────────────
    rag_parser = subparsers.add_parser(
        "rag", help="Pipeline RAG hybride (Dense + Sparse + Graph)"
    )
    rag_parser.add_argument(
        "--check", action="store_true",
        help="Vérifier l'environnement RAG"
    )

    args = parser.parse_args()

    if args.command == "ontology":
        _run_ontology(args)
    elif args.command == "rag":
        _run_rag(args)
    else:
        parser.print_help()
        sys.exit(1)


def _run_ontology(args):
    """Exécute le pipeline ontologique."""
    # Passer les arguments au main de l'ontologie
    sys.argv = ["main.py"]
    if args.sparql_only:
        sys.argv.append("--sparql-only")
    if args.validate:
        sys.argv.append("--validate")
    if args.neo4j_only:
        sys.argv.append("--neo4j-only")
    if args.no_neo4j:
        sys.argv.append("--no-neo4j")
    sys.argv.extend(["--config", args.config])

    from ontologie.main import main as ontology_main
    ontology_main()


def _run_rag(args):
    """Exécute le pipeline RAG."""
    if args.check:
        from rag.check_environment import main as check_main
        success = check_main()
        sys.exit(0 if success else 1)
    else:
        from rag.run_pipeline import main as rag_main
        success = rag_main()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

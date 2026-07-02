#!/usr/bin/env python3
"""
main.py — Point d'entrée du pipeline d'ontologie maritime.

Usage :
    python ontologie/main.py                          # Pipeline complet
    python ontologie/main.py --sparql-only            # Questions de compétence uniquement
    python ontologie/main.py --neo4j-only             # Export Neo4j uniquement
    python ontologie/main.py --validate               # Validation OWL uniquement
    python ontologie/main.py --config path/to/settings.yaml
"""

import argparse
import logging
import sys
from pathlib import Path

# Forcer UTF-8 sur les sorties console pour eviter les UnicodeEncodeError sous Windows.
for _stream_name in ("stdout", "stderr"):
    _stream = getattr(sys, _stream_name, None)
    if _stream is not None and hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

# Configurer le logging avec Rich si disponible
try:
    from rich.logging import RichHandler
    from rich.console import Console
    from rich import print as rprint
    # Sur Windows avec cp1252, désactiver Rich pour éviter les erreurs d'encodage
    import sys
    HAS_RICH = sys.stdout.encoding != 'cp1252'
    if HAS_RICH:
        console = Console()
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[RichHandler(rich_tracebacks=True, console=console)]
        )
    else:
        console = None
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            stream=sys.stdout
        )
except ImportError:
    HAS_RICH = False
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        stream=sys.stdout
    )

logger = logging.getLogger(__name__)

# Ajouter le parent du package au path pour permettre `from ontologie...`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main():
    parser = argparse.ArgumentParser(
        description="Maritime Ontology Pipeline — LKIF-Core aligned"
    )
    parser.add_argument(
        "--config", default="data/config/settings.yaml",
        help="Chemin vers le fichier de configuration (défaut: data/config/settings.yaml)"
    )
    parser.add_argument(
        "--sparql-only", action="store_true",
        help="Exécuter uniquement les questions de compétence SPARQL"
    )
    parser.add_argument(
        "--neo4j-only", action="store_true",
        help="Générer uniquement le script Cypher Neo4j"
    )
    parser.add_argument(
        "--validate", action="store_true",
        help="Valider l'ontologie avec OWL-RL"
    )
    parser.add_argument(
        "--no-neo4j", action="store_true",
        help="Désactiver l'export Neo4j"
    )
    parser.add_argument(
        "--no-reason", action="store_true",
        help="Désactiver le raisonnement OWL-RL"
    )
    parser.add_argument(
        "--no-sparql", action="store_true",
        help="Désactiver les requêtes SPARQL (pour éviter les ralentissements)"
    )
    args = parser.parse_args()

    from ontologie.pipeline import MaritimeOntologyPipeline

    project_root = Path(__file__).resolve().parent.parent
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = project_root / config_path
    args.config = str(config_path)

    # ── Mode SPARQL seulement ─────────────────────────────────────
    if args.sparql_only:
        from ontologie.sparql_runner import run_all_competency_questions, format_results_report
        from ontologie.pipeline import MaritimeOntologyPipeline
        pipeline = MaritimeOntologyPipeline(config_path=args.config)
        # pipeline.step_import_lkif()  # Géré par step_build_schema
        pipeline.step_build_schema()
        data = pipeline.step_load_data()
        pipeline.step_populate(data)
        results = pipeline.step_sparql()
        print(format_results_report(results))
        return

    # ── Mode validation OWL ───────────────────────────────────────
    if args.validate:
        validate_ontology(args.config)
        return

    # ── Pipeline complet ──────────────────────────────────────────
    pipeline = MaritimeOntologyPipeline(config_path=args.config)
    result = pipeline.run(reason=not args.no_reason, run_sparql=not args.no_sparql)

    # Affichage résumé (sans caractères spéciaux pour compatibilité Windows)
    if result and 'stats' in result:
        print(f"\n[SUCCESS] Pipeline complete")
        print(f"  Total triplets : {result['stats']['total_triples']}")
        print(f"  Classes        : {result['stats']['classes']}")
        print(f"  Individuals    : {result['stats']['individuals']}")

    return result


def validate_ontology(config_path: str):
    """Valide l'ontologie avec owlrl (OWL-RL reasoner)."""
    try:
        import owlrl
        from pathlib import Path
        from ontologie.pipeline import MaritimeOntologyPipeline

        pipeline = MaritimeOntologyPipeline(config_path=config_path)
        # pipeline.step_import_lkif() # Géré par step_build_schema
        pipeline.step_build_schema()
        data = pipeline.step_load_data()
        pipeline.step_populate(data)

        g = pipeline.g
        logger.info("🔬 Lancement du raisonneur OWL-RL (owlrl)...")
        owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
        logger.info(f"  ✅ Inférence terminée — {len(g)} triplets après expansion")

        # Vérification de cohérence
        from rdflib import OWL
        conflicts = list(g.subjects(
            predicate=__import__('rdflib').RDF.type,
            object=OWL.Nothing
        ))
        if conflicts:
            logger.error(f"  ❌ {len(conflicts)} individus classifiés owl:Nothing (incohérence)")
            for c in conflicts[:5]:
                logger.error(f"     - {c}")
        else:
            logger.info("  ✅ Aucune incohérence détectée")

        # Export avec inférences
        inferred_path = Path(pipeline.out_dir) / "maritime_ontology_inferred.ttl"
        inferred_path.parent.mkdir(parents=True, exist_ok=True)
        g.serialize(str(inferred_path), format="turtle")
        logger.info(f"  ✅ Ontologie avec inférences → {inferred_path}")

    except ImportError:
        logger.warning("  ⚠️  owlrl non installé. Installer avec: pip install owlrl")


if __name__ == "__main__":
    main()

"""
check_environment.py — Validation de l'environnement pour le RAG Maritime.
"""
import sys
import importlib
from pathlib import Path

# Fix emojis sur le terminal Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


def check_python_version():
    """Vérifie la version Python."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} OK")
        return True
    else:
        print(f"❌ Python 3.9+ requis (actuellement {version.major}.{version.minor})")
        return False


def check_packages():
    """Vérifie les packages essentiels."""
    packages = {
        "fitz": "Extraction PDF ultra-rapide (PyMuPDF)",
        "sentence_transformers": "Embeddings (Dense Retriever)",
        "chromadb": "Base vectorielle (Dense Retriever)",
        "rank_bm25": "BM25 (Sparse Retriever)",
        "rdflib": "RDF/Ontologie (Graph Retriever)",
    }

    optional_packages = {
        "streamlit": "Interface Web",
        "langchain": "Orchestration LLM",
    }

    all_ok = True
    print("\n  Packages essentiels:")
    for package, description in packages.items():
        try:
            importlib.import_module(package)
            print(f"  ✅ {package:<25} ({description})")
        except ImportError:
            print(f"  ❌ {package:<25} ({description}) — À installer")
            all_ok = False

    print("\n  Packages optionnels:")
    for package, description in optional_packages.items():
        try:
            importlib.import_module(package)
            print(f"  ✅ {package:<25} ({description})")
        except ImportError:
            print(f"  ⚠️  {package:<25} ({description}) — Optionnel")

    return all_ok


def check_directories():
    """Vérifie la structure des répertoires."""
    base = Path(__file__).parent.parent

    dirs_to_check = {
        "RAG_data/Baleine": "PDFs Baleine",
        "RAG_data/Oiseaux marins": "PDFs Oiseaux marins",
        "RAG_data/Rejet hydrocarbure": "PDFs Rejet hydrocarbure",
        "data/output": "Ontologie OWL",
        "rag/output": "Dossier output RAG",
        "ontologie": "Package ontologie",
        "rag/core": "RAG Core (retrievers)",
        "rag/ingestion": "RAG Ingestion (PDF)",
        "rag/integration": "RAG Integration (ontologie)",
    }

    all_ok = True
    for rel_path, description in dirs_to_check.items():
        full_path = base / rel_path
        if full_path.exists():
            print(f"  ✅ {rel_path:<35} ({description})")
        else:
            print(f"  ❌ {rel_path:<35} ({description}) — Non trouvé")
            all_ok = False

    return all_ok


def check_ontology():
    """Vérifie que l'ontologie OWL est disponible."""
    base = Path(__file__).parent.parent
    owl_path = base / "data" / "output" / "maritime_ontology.owl"

    if owl_path.exists():
        size_mb = owl_path.stat().st_size / (1024 * 1024)
        print(f"  ✅ Ontologie OWL trouvée ({size_mb:.1f} MB)")
        return True
    else:
        print(f"  ⚠️  Ontologie OWL non trouvée — Graph Retriever désactivé")
        print(f"      Exécuter: python main.py ontology")
        return True  # Pas bloquant


def main():
    print("=" * 60)
    print("🔍 VÉRIFICATION ENVIRONNEMENT RAG MARITIME HYBRIDE")
    print("=" * 60)

    checks = [
        ("Python Version", check_python_version),
        ("Packages", check_packages),
        ("Répertoires", check_directories),
        ("Ontologie", check_ontology),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n📋 {name}:")
        print("-" * 40)
        results.append((name, check_func()))

    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)

    all_passed = all(result for _, result in results)

    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ENVIRONNEMENT PRÊT — Lancer: python -m rag.run_pipeline")
    else:
        print("❌ ERREURS DÉTECTÉES — pip install -r requirements.txt")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

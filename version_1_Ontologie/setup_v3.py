#!/usr/bin/env python3
"""
setup_v3.py — Script de setup pour Architecture V3.

Crée les répertoires, vérifie les dépendances, et configure le système.
"""

import os
import sys
import subprocess
from pathlib import Path

# Couleurs pour l'output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_header(text):
    print(f"\n{BLUE}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{RESET}\n")

def print_ok(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    print(f"{BLUE}ℹ️  {text}{RESET}")

def main():
    print_header("SETUP ARCHITECTURE V3 - RAG MARITIME")
    
    PROJECT_ROOT = Path(__file__).parent
    
    # ───────────────────────────────────────────────────────────────
    # 1. Vérifier les répertoires
    # ───────────────────────────────────────────────────────────────
    print_info("Vérification des répertoires...")
    
    dirs_to_create = [
        PROJECT_ROOT / "data" / "raw",
        PROJECT_ROOT / "data" / "processed" / "embeddings",
        PROJECT_ROOT / "data" / "processed" / "indexes",
        PROJECT_ROOT / "data" / "processed" / "chunks",
        PROJECT_ROOT / "results",
        PROJECT_ROOT / "rag" / "utils",
    ]
    
    for d in dirs_to_create:
        d.mkdir(parents=True, exist_ok=True)
        print_ok(f"Répertoire: {d.relative_to(PROJECT_ROOT)}")
    
    # ───────────────────────────────────────────────────────────────
    # 2. Vérifier .env.local
    # ───────────────────────────────────────────────────────────────
    print_header("Configuration .env")
    
    env_file = PROJECT_ROOT / ".env.local"
    env_example = PROJECT_ROOT / ".env.local.example"
    
    if env_file.exists():
        print_ok(f".env.local existe déjà")
    else:
        if env_example.exists():
            print_warning(f".env.local manquant. Copier .env.local.example?")
            print(f"  Créer manuellement: cp {env_example.name} .env.local")
            print_warning("Veuillez configurer .env.local avant de continuer")
        else:
            print_error(f".env.local.example non trouvé!")
    
    # ───────────────────────────────────────────────────────────────
    # 3. Vérifier les dépendances Python
    # ───────────────────────────────────────────────────────────────
    print_header("Vérification des dépendances")
    
    required_packages = [
        "python-dotenv",
        "chromadb",
        "sentence_transformers",
        "rank_bm25",
        "rdflib",
        "neo4j",
        "streamlit",
        "requests",
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_ok(f"{package}")
        except ImportError:
            print_error(f"{package}")
            missing.append(package)
    
    if missing:
        print_warning(f"\nPaquets manquants: {', '.join(missing)}")
        print_info("Installer avec: pip install -r rag/requirements.txt")
    else:
        print_ok("Toutes les dépendances OK")
    
    # ───────────────────────────────────────────────────────────────
    # 4. Tester la configuration
    # ───────────────────────────────────────────────────────────────
    print_header("Test de configuration")
    
    try:
        sys.path.insert(0, str(PROJECT_ROOT))
        from rag.config import PROJECT_ROOT as CONFIG_ROOT, NEO4J_CONFIG, OUTPUT_DIR
        print_ok(f"Config chargée: PROJECT_ROOT = {CONFIG_ROOT}")
        print_ok(f"Output dir: {OUTPUT_DIR}")
    except Exception as e:
        print_error(f"Erreur chargement config: {e}")
        return False
    
    # ───────────────────────────────────────────────────────────────
    # 5. Tester Health Check
    # ───────────────────────────────────────────────────────────────
    print_header("Test Health Check")
    
    try:
        from rag.utils.health_check import get_health_check
        health = get_health_check()
        health.full_check()
        
        status = health.get_status_dict()
        for component, is_ok in status.items():
            if is_ok:
                print_ok(f"{component}")
            else:
                print_warning(f"{component}")
        
    except Exception as e:
        print_error(f"Erreur health check: {e}")
    
    # ───────────────────────────────────────────────────────────────
    # 6. Summary
    # ───────────────────────────────────────────────────────────────
    print_header("SETUP TERMINÉ ✅")
    
    print_info("Prochaines étapes:")
    print("  1. Configurer .env.local (si pas encore fait)")
    print("     cp .env.local.example .env.local")
    print("     # Remplir vos credentials Neo4j et Ollama")
    print()
    print("  2. Lancer l'interface Streamlit:")
    print("     streamlit run rag/api/app_streamlit.py")
    print()
    print("  3. Consulter la documentation:")
    print("     - docs/ARCHITECTURE_V3.md (cette version)")
    print("     - docs/RAG_ARCHITECTURE_V2.md (architecture RAG)")
    print()
    print_ok("Setup V3 prêt! 🚀")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\nSetup annulé par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erreur fatal: {e}")
        sys.exit(1)

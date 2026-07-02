#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup - Initialiser la structure des dossiers pour le système d'audit

Crée les dossiers nécessaires s'ils n'existent pas
"""

import os
from pathlib import Path


def setup_directories():
    """Crée la structure des dossiers requise"""
    
    print("\n" + "="*70)
    print("🔧 INITIALISATION DE LA STRUCTURE DES DOSSIERS")
    print("="*70 + "\n")
    
    # Dossiers à créer
    directories = [
        "results/batch_queries",
        "results/batch_queries/exports",
        "data/output",
        "logs"
    ]
    
    created = []
    already_exist = []
    
    for dir_path in directories:
        full_path = Path(dir_path)
        if not full_path.exists():
            try:
                full_path.mkdir(parents=True, exist_ok=True)
                created.append(dir_path)
                print(f"✓ Créé: {dir_path}")
            except Exception as e:
                print(f"❌ Erreur lors de la création de {dir_path}: {e}")
        else:
            already_exist.append(dir_path)
            print(f"✓ Existe déjà: {dir_path}")
    
    print(f"\n{'='*70}")
    print(f"📊 Résumé:")
    print(f"   Dossiers créés: {len(created)}")
    print(f"   Dossiers existants: {len(already_exist)}")
    print(f"   Total: {len(created) + len(already_exist)} dossiers")
    print(f"{'='*70}\n")
    
    print("✅ Structure des dossiers prête!\n")


def create_sample_config():
    """Crée un fichier de configuration exemple"""
    
    config_template = """# Configuration - Système d'Audit Automatique

# Mode d'exécution
MODE = "production"  # ou "test"

# Nombre de questions à traiter
# Pour test rapide: 6
# Pour audit complet: 1056
QUESTIONS_LIMIT = None  # None = toutes les questions

# Timeout pour chaque question (en secondes)
QUESTION_TIMEOUT = 300

# Nombre de tentatives en cas d'erreur
MAX_RETRIES = 3

# Logs
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "batch_query.log"

# Export
AUTO_EXPORT = True
EXPORT_FORMATS = ["csv", "json", "excel", "pivot"]
"""
    
    config_file = Path("batch_query_config.py")
    if not config_file.exists():
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_template)
        print("✓ Fichier de configuration créé: batch_query_config.py")
    else:
        print("✓ Fichier de configuration existe déjà")


def main():
    print("\n" + "🎉 " * 18)
    print("\n✨ Bienvenue dans le système d'audit automatique!\n")
    print("🎉 " * 18 + "\n")
    
    # Créer la structure
    setup_directories()
    
    # Optionnel: créer un fichier de config
    # create_sample_config()
    
    print("📚 Prochaines étapes:")
    print("\n1. Lire le guide rapide:")
    print("   → QUICK_START_BATCH_QUERY.md\n")
    print("2. Vérifier que le système est prêt:")
    print("   → python rag/check_environment.py\n")
    print("3. Tester rapidement (6 questions):")
    print("   → python test_quick_query.py\n")
    print("4. Lancer le menu interactif:")
    print("   → python launcher_audit.py\n")
    print("5. Ou lancer l'audit complet directement:")
    print("   → python batch_query_system.py\n")
    
    print("="*70)
    print("✅ Setup complet! Vous êtes prêt à commencer.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

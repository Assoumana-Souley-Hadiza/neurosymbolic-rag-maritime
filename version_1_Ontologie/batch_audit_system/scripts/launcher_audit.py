#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAUNCHER - Interface interactive pour l'audit automatique du système RAG

Menu principal pour exécuter facilement les différentes étapes du batch query
"""

import sys
import subprocess
from pathlib import Path


def print_banner():
    """Affiche la bannière principale"""
    print("\n" + "="*70)
    print("🚀 SYSTÈME D'AUDIT AUTOMATIQUE - RAG MARITIME")
    print("="*70)
    print("\nInterrogation automatique par pays et interdictions")
    print("16 pays × 6 interdictions × 11 questions = 1 056 questions\n")


def print_menu():
    """Affiche le menu principal"""
    print("📋 MENU PRINCIPAL\n")
    print("1️⃣  Test rapide (6 questions de démonstration)")
    print("2️⃣  Générer les questions uniquement")
    print("3️⃣  Exécuter l'audit complet (générer + interroger)")
    print("4️⃣  Interroger les questions existantes (--query-only)")
    print("5️⃣  Analyser les résultats")
    print("6️⃣  Générer un rapport HTML")
    print("7️⃣  Afficher le guide d'utilisation")
    print("0️⃣  Quitter")
    print("\n" + "-"*70)


def execute_command(cmd: str, description: str) -> bool:
    """Exécute une commande et affiche le résultat"""
    print(f"\n{'='*70}")
    print(f"▶️  {description}")
    print(f"{'='*70}\n")
    
    try:
        result = subprocess.run(cmd, shell=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def print_guide():
    """Affiche un guide rapide"""
    guide = """
📚 GUIDE RAPIDE D'UTILISATION
════════════════════════════════════════════════════════════════════

1️⃣ PREMIÈRE FOIS ?
   👉 Commencez par: Test rapide (option 1)
      Cela teste si le système est correctement configuré

2️⃣ PRÊT À GÉNÉRER LES QUESTIONS ?
   👉 Utilisez: Générer les questions uniquement (option 2)
      Cela crée le fichier CSV avec toutes les questions
      Permet de vérifier avant de lancer l'audit complet

3️⃣ LANCER L'AUDIT COMPLET ?
   👉 Utilisez: Exécuter l'audit complet (option 3)
      ⏱️  Temps estimé: 1-3 heures (selon Ollama ou Groq)
      📁 Résultats stockés dans: results/batch_queries/

4️⃣ ANALYSER LES RÉSULTATS ?
   👉 Utilisez: Analyser les résultats (option 5)
      Affiche les statistiques par pays et interdiction
   
   👉 Utilisez: Générer un rapport HTML (option 6)
      Exporte les résultats en page HTML interactive

════════════════════════════════════════════════════════════════════

📊 FICHIERS GÉNÉRÉS

• questions_generees.csv
  └─ Toutes les questions par pays/interdiction

• resultats_audit_YYYYMMDD_HHMMSS.csv
  └─ Réponses complètes du système RAG

• resume_audit_YYYYMMDD_HHMMSS.json
  └─ Statistiques résumées (OUI/NON/ERREURS)

• rapport_audit_YYYYMMDD_HHMMSS.html
  └─ Rapport visuel interactif

════════════════════════════════════════════════════════════════════

⚙️ CONFIGURATION REQUISE

✓ Python 3.8+
✓ Neo4j (accessible et alimenté)
✓ Ollama (local) OU GROQ_API_KEY (cloud)
✓ Modèles d'embeddings chargés

Vérifier: python rag/check_environment.py

════════════════════════════════════════════════════════════════════

💡 CONSEILS

• Utilisez Groq API pour une exécution 5x plus rapide
• Lancez le test rapide avant le batch complet
• Consultez batch_query.log pour les détails d'exécution
• Les résultats sont stockés dans results/batch_queries/

════════════════════════════════════════════════════════════════════
    """
    print(guide)


def main():
    """Fonction principale"""
    print_banner()
    
    while True:
        print_menu()
        choice = input("👉 Sélectionnez une option (0-7): ").strip()
        
        if choice == "0":
            print("\n👋 Au revoir!\n")
            break
        
        elif choice == "1":
            execute_command(
                "python scripts/test_quick_query.py",
                "Test rapide du système RAG"
            )
        
        elif choice == "2":
            execute_command(
                "python scripts/batch_query_system.py --generate-only",
                "Génération des questions"
            )
        
        elif choice == "3":
            confirm = input("\n⚠️  Cela peut prendre 1-3 heures. Continuer? (oui/non): ").lower()
            if confirm in ("oui", "o", "yes", "y"):
                execute_command(
                    "python scripts/batch_query_system.py",
                    "Audit complet - Génération + Interrogation"
                )
            else:
                print("\n❌ Annulé")
        
        elif choice == "4":
            execute_command(
                "python scripts/batch_query_system.py --query-only",
                "Interrogation des questions existantes"
            )
        
        elif choice == "5":
            execute_command(
                "python scripts/analyze_batch_results.py",
                "Analyse des résultats"
            )
        
        elif choice == "6":
            execute_command(
                "python scripts/analyze_batch_results.py --export-html",
                "Génération du rapport HTML"
            )
        
        elif choice == "7":
            print_guide()
        
        else:
            print("❌ Option invalide. Veuillez entrer 0-7.")
        
        # Pause avant de revenir au menu
        input("\n💾 Appuyez sur Entrée pour revenir au menu...")


if __name__ == "__main__":
    main()

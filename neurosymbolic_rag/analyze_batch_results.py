#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour visualiser et analyser les résultats de l'audit batch

Usage:
    python analyze_batch_results.py                     # Affiche le dernier résumé
    python analyze_batch_results.py --file <path>       # Analyse un fichier spécifique
    python analyze_batch_results.py --export-html       # Génère un rapport HTML
"""

import csv
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from collections import defaultdict

class BatchResultsAnalyzer:
    """Analyse les résultats du batch query"""
    
    def __init__(self, results_file: str = None):
        self.results_dir = Path("results/batch_queries")
        self.results_file = Path(results_file) if results_file else self.find_latest_results()
        self.summary_file = self.find_latest_summary()
        self.data = []
        self.summary = {}
        
        if self.results_file and self.results_file.exists():
            self.load_results()
        if self.summary_file and self.summary_file.exists():
            self.load_summary()
    
    def find_latest_results(self) -> Path:
        """Trouve le fichier de résultats le plus récent"""
        if not self.results_dir.exists():
            return None
        results = list(self.results_dir.glob("resultats_audit_*.csv"))
        return max(results, key=lambda p: p.stat().st_mtime) if results else None
    
    def find_latest_summary(self) -> Path:
        """Trouve le fichier de résumé le plus récent"""
        if not self.results_dir.exists():
            return None
        summaries = list(self.results_dir.glob("resume_audit_*.json"))
        return max(summaries, key=lambda p: p.stat().st_mtime) if summaries else None
    
    def load_results(self):
        """Charge les résultats depuis le CSV"""
        with open(self.results_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.data = list(reader)
        print(f"✓ Résultats chargés: {len(self.data)} questions")
    
    def load_summary(self):
        """Charge le résumé depuis JSON"""
        with open(self.summary_file, 'r', encoding='utf-8') as f:
            self.summary = json.load(f)
        print(f"✓ Résumé chargé")
    
    def afficher_statistiques_generales(self):
        """Affiche les statistiques générales"""
        print("\n" + "="*70)
        print("📊 STATISTIQUES GÉNÉRALES")
        print("="*70)
        
        if self.summary:
            print(f"Date d'exécution: {self.summary['date_execution']}")
            print(f"Total de questions: {self.summary['total_questions']}")
            print(f"Total de pays: {self.summary['total_pays']}")
            print(f"Total d'interdictions: {self.summary['total_interdictions']}")
            print(f"\nRésultats:")
            print(f"  ✓ OUI: {self.summary['reponses_oui']}")
            print(f"  ✗ NON: {self.summary['reponses_non']}")
            print(f"  ⚠ ERREURS: {self.summary['erreurs_totales']}")
            
            # Pourcentages
            total = self.summary['total_questions']
            if total > 0:
                print(f"\nPourcentages:")
                print(f"  OUI: {self.summary['reponses_oui']/total*100:.1f}%")
                print(f"  NON: {self.summary['reponses_non']/total*100:.1f}%")
                print(f"  ERREURS: {self.summary['erreurs_totales']/total*100:.1f}%")
    
    def afficher_par_pays(self):
        """Affiche les statistiques par pays"""
        print("\n" + "="*70)
        print("🌍 RÉSULTATS PAR PAYS")
        print("="*70)
        
        if self.summary and 'par_pays' in self.summary:
            for pays, stats in sorted(self.summary['par_pays'].items()):
                oui_pct = stats['oui']/stats['total']*100 if stats['total'] > 0 else 0
                non_pct = stats['non']/stats['total']*100 if stats['total'] > 0 else 0
                err_pct = stats['erreurs']/stats['total']*100 if stats['total'] > 0 else 0
                
                print(f"\n{pays}:")
                print(f"  Total: {stats['total']} questions")
                print(f"  OUI: {stats['oui']} ({oui_pct:.1f}%)")
                print(f"  NON: {stats['non']} ({non_pct:.1f}%)")
                print(f"  ERREURS: {stats['erreurs']} ({err_pct:.1f}%)")
    
    def afficher_par_interdiction(self):
        """Affiche les statistiques par interdiction"""
        print("\n" + "="*70)
        print("⚖️ RÉSULTATS PAR INTERDICTION")
        print("="*70)
        
        if self.summary and 'par_interdiction' in self.summary:
            for interdiction, stats in sorted(self.summary['par_interdiction'].items()):
                oui_pct = stats['oui']/stats['total']*100 if stats['total'] > 0 else 0
                non_pct = stats['non']/stats['total']*100 if stats['total'] > 0 else 0
                err_pct = stats['erreurs']/stats['total']*100 if stats['total'] > 0 else 0
                
                print(f"\n{interdiction}:")
                print(f"  Total: {stats['total']} questions")
                print(f"  OUI: {stats['oui']} ({oui_pct:.1f}%)")
                print(f"  NON: {stats['non']} ({non_pct:.1f}%)")
                print(f"  ERREURS: {stats['erreurs']} ({err_pct:.1f}%)")
    
    def afficher_questions_non_repondues(self, limit: int = 20):
        """Affiche les questions sans réponses"""
        print("\n" + "="*70)
        print("❌ QUESTIONS AVEC ERREURS (limité à 20)")
        print("="*70)
        
        erreurs = [r for r in self.data if r.get('Reponse') == 'ERREUR']
        
        for row in erreurs[:limit]:
            print(f"\n[{row['Pays']} - {row['Interdiction']}]")
            print(f"Q{row['Numero_Question']}: {row['Question'][:100]}...")
            print(f"Erreur: {row['Erreur']}")
    
    def exporter_html(self, output_file: str = None):
        """Exporte un rapport HTML"""
        if output_file is None:
            output_file = self.results_dir / f"rapport_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        html = """
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #4CAF50; color: white; }
                tr:nth-child(even) { background-color: #f2f2f2; }
                .stats { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin: 20px 0; }
                .stat-box { padding: 20px; background: #f0f0f0; border-radius: 5px; }
                .oui { color: green; font-weight: bold; }
                .non { color: red; font-weight: bold; }
                .erreur { color: orange; font-weight: bold; }
            </style>
        </head>
        <body>
        """
        
        html += f"<h1>📊 Rapport d'Audit - {datetime.now().strftime('%d/%m/%Y %H:%M')}</h1>"
        
        # Statistiques générales
        if self.summary:
            html += f"""
            <div class="stats">
                <div class="stat-box">
                    <h3>Total Questions</h3>
                    <p style="font-size: 24px; color: blue;">{self.summary['total_questions']}</p>
                </div>
                <div class="stat-box">
                    <h3>Réponses OUI</h3>
                    <p class="oui" style="font-size: 24px;">{self.summary['reponses_oui']}</p>
                </div>
                <div class="stat-box">
                    <h3>Réponses NON</h3>
                    <p class="non" style="font-size: 24px;">{self.summary['reponses_non']}</p>
                </div>
            </div>
            """
            
            # Tableau par pays
            html += "<h2>Résultats par Pays</h2><table><tr><th>Pays</th><th>Total</th><th>OUI</th><th>NON</th><th>Erreurs</th></tr>"
            for pays, stats in sorted(self.summary['par_pays'].items()):
                html += f"<tr><td>{pays}</td><td>{stats['total']}</td><td class='oui'>{stats['oui']}</td><td class='non'>{stats['non']}</td><td class='erreur'>{stats['erreurs']}</td></tr>"
            html += "</table>"
            
            # Tableau par interdiction
            html += "<h2>Résultats par Interdiction</h2><table><tr><th>Interdiction</th><th>Total</th><th>OUI</th><th>NON</th><th>Erreurs</th></tr>"
            for interdiction, stats in sorted(self.summary['par_interdiction'].items()):
                html += f"<tr><td>{interdiction}</td><td>{stats['total']}</td><td class='oui'>{stats['oui']}</td><td class='non'>{stats['non']}</td><td class='erreur'>{stats['erreurs']}</td></tr>"
            html += "</table>"
        
        html += """
        </body>
        </html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✓ Rapport HTML généré: {output_file}")
    
    def run(self, action: str = "summary", export_html: bool = False):
        """Exécute l'analyse"""
        if not self.results_file:
            print("❌ Aucun fichier de résultats trouvé. Exécutez d'abord batch_query_system.py")
            return
        
        print(f"📂 Fichier analysé: {self.results_file}")
        
        if action == "summary":
            self.afficher_statistiques_generales()
            self.afficher_par_pays()
            self.afficher_par_interdiction()
            self.afficher_questions_non_repondues()
        
        if export_html:
            self.exporter_html()
        
        print("\n" + "="*70)


def main():
    parser = argparse.ArgumentParser(description="Analyse les résultats du batch query")
    parser.add_argument("--file", help="Fichier de résultats à analyser")
    parser.add_argument("--export-html", action="store_true", help="Exporter un rapport HTML")
    
    args = parser.parse_args()
    
    analyzer = BatchResultsAnalyzer(results_file=args.file)
    analyzer.run(export_html=args.export_html)


if __name__ == "__main__":
    main()

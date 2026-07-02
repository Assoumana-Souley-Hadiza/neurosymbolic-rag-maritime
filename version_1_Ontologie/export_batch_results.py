#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'export des résultats en différents formats

Usage:
    python export_batch_results.py --format excel
    python export_batch_results.py --format json
    python export_batch_results.py --format pivot
    python export_batch_results.py --all
"""

import csv
import json
import argparse
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("⚠️  pandas non installé. Certains formats ne seront pas disponibles.")


class BatchResultsExporter:
    """Exporte les résultats en différents formats"""
    
    def __init__(self, results_file: str = None):
        self.results_dir = Path("results/batch_queries")
        self.results_file = Path(results_file) if results_file else self.find_latest_results()
        self.export_dir = self.results_dir / "exports"
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        self.data = []
        if self.results_file and self.results_file.exists():
            self.load_results()
        else:
            print(f"❌ Fichier de résultats non trouvé: {self.results_file}")
    
    def find_latest_results(self) -> Path:
        """Trouve le fichier de résultats le plus récent"""
        if not self.results_dir.exists():
            return None
        results = list(self.results_dir.glob("resultats_audit_*.csv"))
        return max(results, key=lambda p: p.stat().st_mtime) if results else None
    
    def load_results(self):
        """Charge les résultats depuis le CSV"""
        with open(self.results_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.data = list(reader)
        print(f"✓ {len(self.data)} résultats chargés")
    
    def export_json_structured(self):
        """Exporte les résultats en JSON structuré par pays et interdiction"""
        structured = defaultdict(lambda: defaultdict(list))
        
        for row in self.data:
            pays = row['Pays']
            interdiction = row['Interdiction']
            
            structured[pays][interdiction].append({
                'question_num': row['Numero_Question'],
                'question': row['Question'],
                'reponse': row['Reponse'],
                'modele': row['Modele'],
                'timestamp': row['Timestamp']
            })
        
        output_file = self.export_dir / "resultats_structures.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dict(structured), f, ensure_ascii=False, indent=2)
        
        print(f"✓ JSON structuré: {output_file}")
    
    def export_by_country(self):
        """Exporte un fichier CSV par pays"""
        by_country = defaultdict(list)
        
        for row in self.data:
            by_country[row['Pays']].append(row)
        
        for pays, rows in by_country.items():
            filename = self.export_dir / f"resultats_{pays.replace(' ', '_').replace("'", '')}.csv"
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if rows:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)
            print(f"  ✓ {filename.name}")
    
    def export_by_prohibition(self):
        """Exporte un fichier CSV par interdiction"""
        by_prohibition = defaultdict(list)
        
        for row in self.data:
            by_prohibition[row['Interdiction']].append(row)
        
        for interdiction, rows in by_prohibition.items():
            filename = self.export_dir / f"resultats_{interdiction.replace(' ', '_')}.csv"
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if rows:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)
            print(f"  ✓ {filename.name}")
    
    def export_yes_only(self):
        """Exporte uniquement les réponses OUI"""
        yes_responses = [r for r in self.data if 'OUI' in r.get('Reponse', '').upper()]
        
        output_file = self.export_dir / "resultats_OUI_uniquement.csv"
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if yes_responses:
                writer = csv.DictWriter(f, fieldnames=yes_responses[0].keys())
                writer.writeheader()
                writer.writerows(yes_responses)
        
        print(f"✓ Réponses OUI: {output_file} ({len(yes_responses)} lignes)")
    
    def export_errors_only(self):
        """Exporte uniquement les erreurs"""
        errors = [r for r in self.data if r.get('Reponse') == 'ERREUR']
        
        output_file = self.export_dir / "resultats_ERREURS.csv"
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if errors:
                writer = csv.DictWriter(f, fieldnames=errors[0].keys())
                writer.writeheader()
                writer.writerows(errors)
        
        print(f"✓ Erreurs: {output_file} ({len(errors)} lignes)")
    
    def export_excel(self):
        """Exporte en Excel avec plusieurs feuilles"""
        if not HAS_PANDAS:
            print("❌ pandas est requis pour l'export Excel")
            return
        
        df = pd.read_csv(self.results_file)
        output_file = self.export_dir / "resultats_complets.xlsx"
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Feuille 1: Tous les résultats
            df.to_excel(writer, sheet_name='Tous les résultats', index=False)
            
            # Feuille 2: Résumé par pays
            by_country = df.groupby('Pays').agg({
                'Reponse': lambda x: (x == 'OUI').sum()
            }).rename(columns={'Reponse': 'Nombre_OUI'})
            by_country.to_excel(writer, sheet_name='Résumé par Pays')
            
            # Feuille 3: Résumé par interdiction
            by_prohibition = df.groupby('Interdiction').agg({
                'Reponse': lambda x: (x == 'OUI').sum()
            }).rename(columns={'Reponse': 'Nombre_OUI'})
            by_prohibition.to_excel(writer, sheet_name='Résumé par Interdiction')
        
        print(f"✓ Excel multi-feuilles: {output_file}")
    
    def export_pivot_table(self):
        """Exporte une table pivot Pays × Interdiction"""
        if not HAS_PANDAS:
            print("❌ pandas est requis pour la table pivot")
            return
        
        df = pd.read_csv(self.results_file)
        
        # Créer une colonne pour compter les OUI
        df['OUI'] = (df['Reponse'] == 'OUI').astype(int)
        df['NON'] = (df['Reponse'] == 'NON').astype(int)
        df['ERREUR'] = (df['Reponse'] == 'ERREUR').astype(int)
        
        # Pivot table
        pivot_oui = df.pivot_table(
            index='Pays',
            columns='Interdiction',
            values='OUI',
            aggfunc='sum',
            fill_value=0
        )
        
        output_file = self.export_dir / "tableau_pivot_OUI.csv"
        pivot_oui.to_csv(output_file)
        print(f"✓ Table pivot OUI: {output_file}")
        
        # Exporter aussi en Excel si possible
        try:
            excel_file = self.export_dir / "tableau_pivot_OUI.xlsx"
            pivot_oui.to_excel(excel_file)
            print(f"✓ Table pivot Excel: {excel_file}")
        except:
            pass
    
    def export_summary_stats(self):
        """Exporte les statistiques résumées"""
        stats = {
            "total_questions": len(self.data),
            "reponses_oui": sum(1 for r in self.data if 'OUI' in r.get('Reponse', '').upper()),
            "reponses_non": sum(1 for r in self.data if 'NON' in r.get('Reponse', '').upper()),
            "erreurs": sum(1 for r in self.data if r.get('Reponse') == 'ERREUR'),
            "par_pays": {},
            "par_interdiction": {}
        }
        
        # Par pays
        by_country = defaultdict(lambda: {'total': 0, 'oui': 0, 'non': 0, 'erreur': 0})
        for row in self.data:
            pays = row['Pays']
            by_country[pays]['total'] += 1
            if 'OUI' in row.get('Reponse', '').upper():
                by_country[pays]['oui'] += 1
            elif 'NON' in row.get('Reponse', '').upper():
                by_country[pays]['non'] += 1
            else:
                by_country[pays]['erreur'] += 1
        
        stats['par_pays'] = dict(by_country)
        
        # Par interdiction
        by_prohibition = defaultdict(lambda: {'total': 0, 'oui': 0, 'non': 0, 'erreur': 0})
        for row in self.data:
            interdiction = row['Interdiction']
            by_prohibition[interdiction]['total'] += 1
            if 'OUI' in row.get('Reponse', '').upper():
                by_prohibition[interdiction]['oui'] += 1
            elif 'NON' in row.get('Reponse', '').upper():
                by_prohibition[interdiction]['non'] += 1
            else:
                by_prohibition[interdiction]['erreur'] += 1
        
        stats['par_interdiction'] = dict(by_prohibition)
        
        output_file = self.export_dir / "statistiques_resumees.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Statistiques résumées: {output_file}")
    
    def export_all(self):
        """Exporte dans tous les formats disponibles"""
        print("\n📦 Export en tous les formats...\n")
        
        self.export_json_structured()
        
        print("\n📂 Fichiers CSV par pays:")
        self.export_by_country()
        
        print("\n📂 Fichiers CSV par interdiction:")
        self.export_by_prohibition()
        
        self.export_yes_only()
        self.export_errors_only()
        self.export_summary_stats()
        
        if HAS_PANDAS:
            print("\n📊 Formats Excel:")
            self.export_excel()
            self.export_pivot_table()
        
        print(f"\n✅ Tous les exports sont dans: {self.export_dir}")


def main():
    parser = argparse.ArgumentParser(description="Export des résultats en différents formats")
    parser.add_argument(
        "--format",
        choices=["json", "by-country", "by-prohibition", "yes-only", "errors", "excel", "pivot", "stats"],
        help="Format d'export spécifique"
    )
    parser.add_argument("--file", help="Fichier de résultats à exporter")
    parser.add_argument("--all", action="store_true", help="Exporter tous les formats")
    
    args = parser.parse_args()
    
    exporter = BatchResultsExporter(results_file=args.file)
    
    if not exporter.data:
        print("❌ Aucune donnée à exporter")
        return
    
    if args.all:
        exporter.export_all()
    elif args.format == "json":
        exporter.export_json_structured()
    elif args.format == "by-country":
        print("\n📂 Création de fichiers par pays:")
        exporter.export_by_country()
    elif args.format == "by-prohibition":
        print("\n📂 Création de fichiers par interdiction:")
        exporter.export_by_prohibition()
    elif args.format == "yes-only":
        exporter.export_yes_only()
    elif args.format == "errors":
        exporter.export_errors_only()
    elif args.format == "excel":
        exporter.export_excel()
    elif args.format == "pivot":
        exporter.export_pivot_table()
    elif args.format == "stats":
        exporter.export_summary_stats()
    else:
        exporter.export_all()


if __name__ == "__main__":
    main()

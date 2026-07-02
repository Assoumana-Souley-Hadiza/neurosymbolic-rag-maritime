# 📝 Exemples d'Utilisation

## Cas 1: Je veux tester rapidement

```bash
# Depuis la racine
python batch_audit_system/scripts/test_quick_query.py

# Ou depuis le dossier batch_audit_system
cd batch_audit_system
python scripts/test_quick_query.py
```

**Résultat:** 6 questions de test (1-2 minutes)

---

## Cas 2: Je veux vérifier les questions avant de lancer

```bash
# Générer les questions
python batch_audit_system/scripts/batch_query_system.py --generate-only

# Vérifier le fichier généré
cat results/batch_queries/questions_generees.csv

# Si OK, interroger le système
python batch_audit_system/scripts/batch_query_system.py --query-only
```

**Résultat:** 1 056 questions générées, puis interrogation du système

---

## Cas 3: Je veux lancer l'audit complet en une commande

```bash
# Option 1: Via le menu (RECOMMANDÉ)
python audit.py
# Puis choisir l'option 3

# Option 2: Directement
python batch_audit_system/scripts/batch_query_system.py
```

**Résultat:** 30-50 minutes (Groq) ou 1-3 heures (Ollama)

---

## Cas 4: Je veux analyser les résultats

```bash
# Afficher les statistiques
python batch_audit_system/scripts/analyze_batch_results.py

# Générer un rapport HTML
python batch_audit_system/scripts/analyze_batch_results.py --export-html

# Ouvrir le rapport dans un navigateur
start results/batch_queries/rapport_audit_*.html
```

**Résultat:** Statistiques affichées + rapport HTML généré

---

## Cas 5: Je veux exporter en différents formats

```bash
# Tous les formats
python batch_audit_system/scripts/export_batch_results.py --all

# JSON structuré
python batch_audit_system/scripts/export_batch_results.py --format json

# Excel multi-feuilles
python batch_audit_system/scripts/export_batch_results.py --format excel

# Table pivot
python batch_audit_system/scripts/export_batch_results.py --format pivot

# Par pays
python batch_audit_system/scripts/export_batch_results.py --format by-country

# Par interdiction
python batch_audit_system/scripts/export_batch_results.py --format by-prohibition
```

**Résultat:** Fichiers exportés dans `results/batch_queries/exports/`

---

## Cas 6: Je veux utiliser le menu interactif (PLUS FACILE)

```bash
# Lancer le menu
python audit.py

# Ou depuis le dossier batch_audit_system
cd batch_audit_system
python scripts/launcher_audit.py
```

**Menu:**
1. Test rapide
2. Générer questions
3. Audit complet
4. Interroger questions existantes
5. Analyser résultats
6. Générer rapport HTML
7. Afficher aide

---

## Cas 7: Je veux reprendre après une interruption

```bash
# Interroger les questions déjà générées
python batch_audit_system/scripts/batch_query_system.py --query-only

# Cela continue depuis où ça s'est arrêté
```

**Résultat:** Interrogation reprend sans régénérer les questions

---

## Cas 8: Workflow complet (étape par étape)

```bash
# 1. Vérifier que tout fonctionne
python rag/check_environment.py

# 2. Tester rapidement
python batch_audit_system/scripts/test_quick_query.py

# 3. Générer les questions
python batch_audit_system/scripts/batch_query_system.py --generate-only

# 4. Vérifier les questions générées
head -5 results/batch_queries/questions_generees.csv

# 5. Lancer l'audit complet
python batch_audit_system/scripts/batch_query_system.py

# 6. Analyser les résultats
python batch_audit_system/scripts/analyze_batch_results.py

# 7. Exporter en tous formats
python batch_audit_system/scripts/export_batch_results.py --all

# 8. Ouvrir le rapport HTML
start results/batch_queries/rapport_audit_*.html
```

**Durée totale:** ~2-4 heures

---

## Cas 9: Avec Groq API (plus rapide)

```bash
# D'abord, définir la clé API
set GROQ_API_KEY=votre_clé_api

# Puis lancer l'audit
python batch_audit_system/scripts/batch_query_system.py
```

**Durée:** 30-50 minutes au lieu de 1-3 heures

---

## Cas 10: Filtrer les résultats avec Python

```python
import pandas as pd

# Charger les résultats
df = pd.read_csv('results/batch_queries/resultats_audit_*.csv')

# Filtrer par pays
df_algerie = df[df['Pays'] == 'Algérie']

# Filtrer par interdiction
df_chalutage = df[df['Interdiction'] == 'Chalutage de fond']

# Filtrer par réponse OUI
df_oui = df[df['Reponse'].str.contains('OUI', na=False)]

# Sauvegarder le résultat filtré
df_oui.to_csv('resultats_oui.csv', index=False)
```

---

## Cas 11: Vérification rapide des erreurs

```bash
# Afficher les dernières lignes du log
tail -20 batch_query.log

# Rechercher les erreurs
grep ERROR batch_query.log

# Suivre l'exécution en temps réel
tail -f batch_query.log
```

---

## Cas 12: Créer un alias pour plus de facilité

```bash
# Créer un alias (Linux/Mac)
alias audit="python /path/to/audit.py"

# Utiliser l'alias
audit

# Ou directement depuis n'importe où
cd n'importe_quel_dossier
audit
```

---

## 💡 Conseils d'utilisation

1. **Toujours commencer par le test rapide** pour vérifier que le système fonctionne
2. **Utiliser le menu interactif** pour les utilisateurs non-techniques
3. **Utiliser Groq API** pour une exécution 5x plus rapide
4. **Consulter les logs** en cas de problème
5. **Exporter en Excel** pour partager facilement les résultats

---

## 📂 Fichiers générés

```
results/batch_queries/
├── questions_generees.csv              (1 056 questions)
├── resultats_audit_20240515_143022.csv (Réponses)
├── resume_audit_20240515_143022.json   (Statistiques)
├── rapport_audit_20240515_143022.html  (Rapport visuel)
└── exports/
    ├── resultats_structures.json
    ├── tableau_pivot_OUI.xlsx
    ├── resultats_complets.xlsx
    ├── resultats_par_pays.csv
    ├── statistiques_resumees.json
    └── ...autres formats
```

---

**✨ Prêt à commencer? Lancez `python audit.py`**

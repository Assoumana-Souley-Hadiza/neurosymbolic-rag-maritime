# 🚀 Guide Complet - Interrogation Automatique du Système RAG

## 📋 Vue d'ensemble

Ce guide vous explique comment utiliser les scripts pour interroger automatiquement le système RAG et générer un audit complet par pays et par type d'interdiction.

### Structure des fichiers

```
batch_query_system.py        → Script principal d'interrogation automatique
analyze_batch_results.py     → Script d'analyse des résultats
results/batch_queries/       → Répertoire des résultats
  ├── questions_generees.csv           → Questions générées pour tous les pays
  ├── resultats_audit_YYYYMMDD_HHMMSS.csv  → Réponses du système
  └── resume_audit_YYYYMMDD_HHMMSS.json    → Résumé statistique
```

---

## 🎯 Étape 1 : Générer les Questions

Les questions sont générées automatiquement pour **16 pays** et **6 types d'interdictions** :

### Pays couverts
🌍 **Afrique** (15 pays):
- Algérie, Bénin, Cameroun, Comores, Congo, Côte d'Ivoire
- Djibouti, Gabon, Guinée, Madagascar, Maroc, Mauritanie
- Sénégal, Togo, Tunisie

🇪🇺 **Europe**:
- France

### Interdictions couvertes
1. ⛓️ **Chalutage de fond** (11 questions)
2. 🐋 **Chasse à la baleine** (11 questions)
3. 🏗️ **Construction côtière** (11 questions)
4. 🏖️ **Extraction de sable** (11 questions)
5. 🦅 **Oiseaux Marins** (11 questions)
6. 🛢️ **Rejet d'hydrocarbures** (11 questions)

**Total: 16 pays × 6 interdictions × 11 questions = 1 056 questions**

---

## 🚀 Étape 2 : Interroger le Système RAG

### Option A : Exécution Complète (Génération + Interrogation)

```bash
python batch_query_system.py
```

**Cela va:**
1. ✓ Générer les 1 056 questions
2. ✓ Initialiser le système RAG (Neo4j + LLM)
3. ✓ Interroger le système pour chaque question
4. ✓ Stocker les réponses dans un CSV
5. ✓ Générer un résumé statistique

### Option B : Générer les Questions Uniquement

```bash
python batch_query_system.py --generate-only
```

Cela crée le fichier `questions_generees.csv` sans interroger le système.
Utile pour vérifier les questions avant le batch.

### Option C : Interroger les Questions Existantes

Si les questions sont déjà générées :

```bash
python batch_query_system.py --query-only
```

Cela charge les questions existantes et interroge le système.
Utile pour reprendre après une interruption.

---

## 📊 Étape 3 : Analyser les Résultats

### Visualiser le Résumé

```bash
python analyze_batch_results.py
```

Affiche les statistiques générales :
- ✓ Réponses OUI / NON
- ⚠️ Erreurs
- 📈 Statistiques par pays
- 📈 Statistiques par interdiction
- ❌ Questions avec erreurs

### Analyser un Fichier Spécifique

```bash
python analyze_batch_results.py --file results/batch_queries/resultats_audit_20240515_143022.csv
```

### Exporter en Rapport HTML

```bash
python analyze_batch_results.py --export-html
```

Génère un rapport HTML interactif et visualisable dans un navigateur.

---

## 📁 Structure des Fichiers de Résultat

### 1. `questions_generees.csv`

| Colonne | Description |
|---------|-------------|
| Pays | Nom du pays |
| Code_Pays | Code ISO du pays |
| Interdiction | Type d'interdiction |
| Numero_Question | Numéro séquentiel (1-11) |
| Question | Question formatée pour le pays |

**Exemple:**
```
Algérie,alg,Chalutage de fond,1,"Est-ce qu'il existe un article portant sur l'interdiction du chalutage de fond alg ?"
```

### 2. `resultats_audit_YYYYMMDD_HHMMSS.csv`

| Colonne | Description |
|---------|-------------|
| Pays | Nom du pays |
| Code_Pays | Code du pays |
| Interdiction | Type d'interdiction |
| Numero_Question | Numéro de la question |
| Question | Question posée |
| Reponse | Réponse du LLM (OUI/NON/ERREUR) |
| Modele | Modèle LLM utilisé |
| Erreur | Message d'erreur (si applicable) |
| Timestamp | Date/heure de traitement |

### 3. `resume_audit_YYYYMMDD_HHMMSS.json`

Structure JSON avec:
- **Statistiques globales**: total, erreurs, OUI, NON
- **Par pays**: détail pour chaque pays
- **Par interdiction**: détail pour chaque type d'interdiction

**Exemple:**
```json
{
  "date_execution": "2024-05-15T14:30:22",
  "total_questions": 1056,
  "total_pays": 16,
  "total_interdictions": 6,
  "erreurs_totales": 5,
  "reponses_oui": 450,
  "reponses_non": 601,
  "par_pays": {
    "Algérie": {
      "total": 66,
      "oui": 28,
      "non": 35,
      "erreurs": 3
    }
  }
}
```

---

## ⏱️ Temps d'Exécution Estimé

- **Génération des questions**: < 1 seconde
- **Interrogation du système**: 
  - Groq API (Cloud): ~2-3 secondes par question = **30-50 minutes**
  - Ollama (Local): ~5-10 secondes par question = **1.5-3 heures**

**Recommandation**: Utilisez Groq API pour une exécution plus rapide.

---

## ⚙️ Configuration

### Variables d'environnement

Pour utiliser Groq API (recommandé):
```bash
set GROQ_API_KEY=votre_cle_api_groq
```

### Fichiers de configuration

- `rag/config.py`: Configuration du LLM (modèle, température, etc.)
- `data/config/settings.yaml`: Configuration du système

---

## 🔍 Exemples d'Utilisation

### Exemple 1: Audit complet

```bash
# Lancer l'interrogation complète
python batch_query_system.py

# Une fois terminé, analyser les résultats
python analyze_batch_results.py
```

### Exemple 2: Vérifier d'abord les questions

```bash
# Générer et vérifier les questions
python batch_query_system.py --generate-only

# Consulter le fichier CSV généré
# ...vérifications...

# Ensuite interroger le système
python batch_query_system.py --query-only

# Analyser les résultats
python analyze_batch_results.py
```

### Exemple 3: Générer un rapport

```bash
# Interroger le système
python batch_query_system.py

# Générer un rapport HTML
python analyze_batch_results.py --export-html

# Ouvrir le rapport dans un navigateur
```

---

## 📝 Logs

### Fichier de log principal

`batch_query.log` - Contient tous les détails d'exécution

### Consultation des logs

```bash
# Afficher les dernières 50 lignes
tail -50 batch_query.log

# Rechercher les erreurs
grep "ERROR" batch_query.log

# Suivre l'exécution en temps réel
tail -f batch_query.log
```

---

## 🐛 Dépannage

### Le système RAG n'est pas disponible

```
❌ Erreur: LLM non disponible (Ollama/Groq not reachable)
```

**Solution:**
1. Vérifier que Ollama est lancé (local)
2. Vérifier la clé API Groq
3. Vérifier la connexion à Neo4j

### Questions non générées

Vérifier que le fichier `results/batch_queries/` existe:
```bash
mkdir -p results/batch_queries
```

### Résultats incomplets

Utiliser `--query-only` pour relancer l'interrogation:
```bash
python batch_query_system.py --query-only
```

---

## 💾 Stockage des Résultats

Tous les fichiers de résultats sont sauvegardés dans:
```
results/batch_queries/
```

Pour sauvegarder dans un autre emplacement:
```python
# Modifier dans batch_query_system.py
self.output_dir = Path("votre/chemin/personnalise")
```

---

## 📊 Filtrer les Résultats

Pour filtrer les résultats dans le CSV généré:

```python
import pandas as pd

# Charger les résultats
df = pd.read_csv('results/batch_queries/resultats_audit_latest.csv')

# Filtrer par pays
df_algerie = df[df['Pays'] == 'Algérie']

# Filtrer par interdiction
df_chalutage = df[df['Interdiction'] == 'Chalutage de fond']

# Filtrer par réponse
df_oui = df[df['Reponse'].str.contains('OUI', case=False, na=False)]

# Sauvegarder le résultat filtré
df_algerie.to_csv('resultats_algerie.csv', index=False)
```

---

## 🎓 Notes Importantes

1. **Conformité juridique**: Vérifier que les questions respectent le cadre légal de chaque pays
2. **Fraîcheur des données**: Les résultats dépendent des documents indexés dans le système RAG
3. **Qualité des réponses**: Les réponses du LLM peuvent nécessiter une vérification manuelle
4. **Performance**: Utiliser Groq API pour les interrogations longues

---

## 📞 Support

Pour les problèmes, consultez:
- `batch_query.log` pour les erreurs détaillées
- `rag/check_environment.py` pour vérifier l'environnement
- Documentation RAG dans `docs/`

---

**✨ Dernière mise à jour**: 2024-05-15
**Version**: 1.0

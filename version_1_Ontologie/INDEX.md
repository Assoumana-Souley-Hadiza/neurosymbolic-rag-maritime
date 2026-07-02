# 📑 INDEX - Tous les Scripts et Fichiers du Système

## 🎯 POINT D'ENTRÉE (COMMENCER ICI)

### 1. 🎮 Lanceur Interactif
📄 **`launcher_audit.py`**
- Menu guidé pour exécuter tous les scripts facilement
- Recommandé pour les utilisateurs qui ne veulent pas retenir les commandes
- **Commande:** `python launcher_audit.py`

---

## 🔧 SCRIPTS PRINCIPAUX

### 2. 🚀 Interrogation Automatique
📄 **`batch_query_system.py`**
- Génère les 1 056 questions (16 pays × 6 interdictions × 11 questions)
- Initialise le système RAG
- Interroge le système pour chaque question
- Sauvegarde les réponses et génère des statistiques

**Modes:**
```bash
python batch_query_system.py                    # Complet (générer + interroger)
python batch_query_system.py --generate-only    # Générer uniquement
python batch_query_system.py --query-only       # Interroger les questions existantes
```

**Sorties:**
- `results/batch_queries/questions_generees.csv`
- `results/batch_queries/resultats_audit_*.csv`
- `results/batch_queries/resume_audit_*.json`

---

### 3. 🧪 Test Rapide
📄 **`test_quick_query.py`**
- Lance 6 questions de test (une par interdiction)
- Vérifie que Neo4j, LLM et tous les composants fonctionnent
- Utile avant de lancer le batch complet

**Commande:**
```bash
python test_quick_query.py                  # Mode normal
python test_quick_query.py --verbose        # Mode verbose (plus de détails)
```

**Temps:** < 2 minutes

---

### 4. 📊 Analyse des Résultats
📄 **`analyze_batch_results.py`**
- Affiche les statistiques générales (OUI/NON/ERREURS)
- Affiche les résultats par pays
- Affiche les résultats par interdiction
- Génère un rapport HTML interactif

**Commandes:**
```bash
python analyze_batch_results.py                         # Mode normal
python analyze_batch_results.py --file <path>           # Analyser un fichier
python analyze_batch_results.py --export-html           # Générer rapport HTML
```

**Sorties:**
- Affichage console
- `results/batch_queries/rapport_audit_*.html`

---

### 5. 📦 Export Multi-Format
📄 **`export_batch_results.py`**
- Exporte les résultats en différents formats
- JSON structuré, Excel, CSV par pays/interdiction, tables pivot

**Commandes:**
```bash
python export_batch_results.py --all                    # Tous les formats
python export_batch_results.py --format json            # JSON structuré
python export_batch_results.py --format excel           # Excel multi-feuilles
python export_batch_results.py --format pivot           # Table pivot
python export_batch_results.py --format by-country      # CSV par pays
python export_batch_results.py --format by-prohibition  # CSV par interdiction
```

**Sorties:**
- `results/batch_queries/exports/*` (multiples formats)

---

## 📚 GUIDES DE DOCUMENTATION

### 📖 Guide de Démarrage Rapide
📄 **`QUICK_START_BATCH_QUERY.md`** ⭐ LIRE EN PREMIER
- Démarrage en 3 étapes
- 4 modes d'utilisation expliqués
- Temps d'exécution estimé
- Pays et interdictions couverts
- Dépannage rapide

---

### 📖 Guide Complet Détaillé
📄 **`BATCH_QUERY_GUIDE.md`**
- Vue d'ensemble complète
- Structure détaillée des fichiers de résultat
- Configuration avancée
- Exemples d'utilisation complets
- Filtrage avancé des résultats
- Dépannage approfondi

---

### 📖 README Principal
📄 **`README_BATCH_QUERY_SYSTEM.md`**
- Résumé de tout ce que vous avez reçu
- Guide de démarrage en 5 minutes
- Synthèse des 6 scripts créés
- Conseils d'utilisation
- Résumé des fichiers générés

---

### 📑 Ce fichier
📄 **`INDEX.md`**
- Index complet de tous les scripts
- Structure et organisation
- Commandes rapides

---

## 📂 STRUCTURE DES DOSSIERS

```
Version_1_Ontologie/
├── Scripts Principaux:
│   ├── launcher_audit.py              🎮 Menu interactif
│   ├── batch_query_system.py           🚀 Script principal
│   ├── test_quick_query.py             🧪 Test rapide
│   ├── analyze_batch_results.py        📊 Analyse
│   └── export_batch_results.py         📦 Export
│
├── Guides:
│   ├── INDEX.md                        📑 Ce fichier
│   ├── QUICK_START_BATCH_QUERY.md      📖 Guide rapide
│   ├── BATCH_QUERY_GUIDE.md            📖 Guide complet
│   └── README_BATCH_QUERY_SYSTEM.md    📖 README principal
│
├── Données Générées:
│   └── results/batch_queries/
│       ├── questions_generees.csv
│       ├── resultats_audit_*.csv
│       ├── resume_audit_*.json
│       ├── rapport_audit_*.html
│       └── exports/
│           ├── resultats_structures.json
│           ├── tableau_pivot_*.csv
│           ├── resultats_complets.xlsx
│           └── ...autres formats
│
└── Logs:
    └── batch_query.log                 📝 Log d'exécution

```

---

## 🚀 FLUX DE TRAVAIL TYPIQUE

### Scenario 1: Je veux tester rapidement
```bash
python test_quick_query.py              # 1-2 min
```

### Scenario 2: Je veux générer les questions et les vérifier
```bash
python batch_query_system.py --generate-only   # < 1 sec
# Vérifier resultats/batch_queries/questions_generees.csv
```

### Scenario 3: Je veux lancer l'audit complet (sans menu)
```bash
python batch_query_system.py            # 1-3h (selon Ollama/Groq)
python analyze_batch_results.py         # 1 min
python export_batch_results.py --all    # 2 min
```

### Scenario 4: Utiliser le menu interactif (RECOMMANDÉ)
```bash
python launcher_audit.py                # Menu guidé
```

### Scenario 5: Je veux reprendre après une interruption
```bash
python batch_query_system.py --query-only  # Continue depuis où ça s'est arrêté
```

---

## 📊 PAYS ET INTERDICTIONS COUVERTS

### 16 Pays
| Afrique (15) | Europe (1) |
|--------------|-----------|
| Algérie (alg) | France (fra) |
| Bénin (ben) | |
| Cameroun (cmr) | |
| Comores (com) | |
| Congo (cng) | |
| Côte d'Ivoire (ivc) | |
| Djibouti (dji) | |
| Gabon (gab) | |
| Guinée (gui) | |
| Madagascar (mad) | |
| Maroc (mor) | |
| Mauritanie (mau) | |
| Sénégal (sen) | |
| Togo (tog) | |
| Tunisie (tun) | |

### 6 Interdictions × 11 Questions
1. ⛓️ **Chalutage de fond** - 11 questions
2. 🐋 **Chasse à la baleine** - 11 questions
3. 🏗️ **Construction côtière** - 11 questions
4. 🏖️ **Extraction de sable** - 11 questions
5. 🦅 **Oiseaux Marins** - 11 questions
6. 🛢️ **Rejet d'hydrocarbures** - 11 questions

**Total: 1 056 questions**

---

## ⏱️ TEMPS D'EXÉCUTION

| Opération | Temps | Commande |
|-----------|-------|----------|
| Test rapide | 1-2 min | `python test_quick_query.py` |
| Génération des questions | < 1 sec | `python batch_query_system.py --generate-only` |
| Interrogation (Ollama) | 1.5-3h | `python batch_query_system.py` |
| Interrogation (Groq) | 30-50 min | `python batch_query_system.py` |
| Analyse des résultats | < 1 min | `python analyze_batch_results.py` |
| Export tous formats | 2 min | `python export_batch_results.py --all` |

---

## 🔍 FICHIERS DE RÉSULTATS

### Générés par `batch_query_system.py`
- ✅ `questions_generees.csv` - Toutes les 1 056 questions
- ✅ `resultats_audit_YYYYMMDD_HHMMSS.csv` - Réponses complètes
- ✅ `resume_audit_YYYYMMDD_HHMMSS.json` - Statistiques résumées

### Générés par `analyze_batch_results.py`
- ✅ `rapport_audit_YYYYMMDD_HHMMSS.html` - Rapport visuel

### Générés par `export_batch_results.py`
- ✅ `resultats_structures.json` - JSON par pays/interdiction
- ✅ `resultats_*.csv` - Un fichier par pays
- ✅ `tableau_pivot_*.xlsx` - Table pivot Excel
- ✅ `resultats_complets.xlsx` - Excel multi-feuilles
- ✅ `statistiques_resumees.json` - Stats résumées

---

## 💻 COMMANDES PRINCIPALES

```bash
# 1. Tester le système
python test_quick_query.py

# 2. Générer les questions
python batch_query_system.py --generate-only

# 3. Lancer l'audit complet
python batch_query_system.py

# 4. Analyser les résultats
python analyze_batch_results.py

# 5. Générer un rapport HTML
python analyze_batch_results.py --export-html

# 6. Exporter en tous les formats
python export_batch_results.py --all

# Ou utiliser le menu interactif
python launcher_audit.py
```

---

## 🎯 POUR LES UTILISATEURS IMPATIENTS

1. Ouvrez un terminal
2. Collez ceci:
```bash
python launcher_audit.py
```
3. Choisissez une option dans le menu
4. Laissez le système tourner
5. Consultez les résultats dans `results/batch_queries/`

**C'est tout!** ✨

---

## 🆘 BESOIN D'AIDE?

| Question | Réponse |
|----------|--------|
| Par où commencer? | Lire `QUICK_START_BATCH_QUERY.md` |
| Comment utiliser? | `python launcher_audit.py` |
| Détails techniques? | Lire `BATCH_QUERY_GUIDE.md` |
| Comment corriger une erreur? | Consulter `batch_query.log` |
| Tous les détails? | Lire `README_BATCH_QUERY_SYSTEM.md` |

---

## 📝 NOTES

- ✅ Tous les scripts sont en français
- ✅ Tous les scripts incluent la gestion d'erreurs
- ✅ Tous génèrent des logs détaillés
- ✅ Le menu interactif est le plus simple
- ✅ Les résultats sont sauvegardés automatiquement

---

**Version**: 1.0
**Dernière mise à jour**: 2024-05-15
**Créé pour**: Audit automatique du système RAG Maritime

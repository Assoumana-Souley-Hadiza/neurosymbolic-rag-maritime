# 📁 Structure Complète du Projet

```
version_1_Ontologie/
│
├── 🚀 POINTS D'ENTRÉE RAPIDES
│   ├── audit.py                    ← Lancer depuis racine (wrapper)
│   ├── START_AUDIT.bat             ← Double-clic sur Windows
│   └── setup_audit.py              ← Initialiser la structure
│
├── 📦 SYSTÈME D'AUDIT (DOSSIER PRINCIPAL)
│   └── batch_audit_system/
│       │
│       ├── 🎮 scripts/             (5 scripts Python)
│       │   ├── launcher_audit.py       Menu interactif
│       │   ├── batch_query_system.py   Script principal (1 056 Q)
│       │   ├── test_quick_query.py     Test rapide (6 Q)
│       │   ├── analyze_batch_results.py Analyser résultats
│       │   └── export_batch_results.py  Export multi-formats
│       │
│       ├── 📚 docs/                (5 guides + index)
│       │   ├── 00_START_HERE.md        ⭐ LIRE EN PREMIER
│       │   ├── QUICK_START.md          Guide rapide (5 min)
│       │   ├── README.md               Vue d'ensemble
│       │   ├── BATCH_QUERY_GUIDE.md    Guide complet
│       │   ├── INDEX.md                Index complet
│       │   └── COMPLETION.md           Résumé projet
│       │
│       ├── 📝 examples/            (Exemples & commandes)
│       │   ├── commands.sh              Commandes shell/bat
│       │   └── examples.md              Cas d'usage détaillés
│       │
│       └── README.md               Vue d'ensemble dossier
│
├── 📊 RÉSULTATS GÉNÉRÉS
│   └── results/batch_queries/
│       ├── questions_generees.csv
│       ├── resultats_audit_*.csv
│       ├── resume_audit_*.json
│       ├── rapport_audit_*.html
│       └── exports/
│           ├── resultats_structures.json
│           ├── tableau_pivot_*.xlsx
│           ├── resultats_complets.xlsx
│           └── ... (autres formats)
│
├── 📝 LOGS
│   └── batch_query.log
│
└── ... (autres dossiers du projet)
    ├── rag/
    ├── ontologie/
    ├── data/
    └── ...
```

---

## 🎯 UTILISATION RAPIDE

```bash
# DEPUIS LA RACINE
python audit.py
# → Menu interactif

# OU DIRECTEMENT
python batch_audit_system/scripts/test_quick_query.py
python batch_audit_system/scripts/batch_query_system.py
python batch_audit_system/scripts/analyze_batch_results.py

# OU SUR WINDOWS
START_AUDIT.bat
```

---

## 📋 FICHIERS CLÉS

### Points d'Entrée
- `audit.py` - Wrapper pour lancer depuis racine
- `START_AUDIT.bat` - Double-clic sur Windows
- `batch_audit_system/scripts/launcher_audit.py` - Menu

### Scripts
- `batch_query_system.py` - Cœur du système (génère + interroge)
- `test_quick_query.py` - Test avec 6 questions
- `analyze_batch_results.py` - Statistiques
- `export_batch_results.py` - Export multi-formats

### Documentation
- `batch_audit_system/docs/00_START_HERE.md` - Lire en premier!
- `batch_audit_system/docs/QUICK_START.md` - Guide rapide
- `batch_audit_system/docs/README.md` - Vue d'ensemble
- `batch_audit_system/examples/examples.md` - Cas d'usage

### Résultats
- `results/batch_queries/` - Tous les fichiers générés

---

## 📊 CE QUE VOUS ALLEZ OBTENIR

### Questions Générées
```
1 056 questions = 16 pays × 6 interdictions × 11 questions
```

### Pays (16)
🌍 Afrique: Algérie, Bénin, Cameroun, Comores, Congo, Côte d'Ivoire, Djibouti, Gabon, Guinée, Madagascar, Maroc, Mauritanie, Sénégal, Togo, Tunisie
🇪🇺 Europe: France

### Interdictions (6)
1. Chalutage de fond
2. Chasse à la baleine
3. Construction côtière
4. Extraction de sable
5. Oiseaux Marins
6. Rejet d'hydrocarbures

### Questions par Interdiction (11)
1. Existence article
2. Restrictions géographiques
3. Temporalité
4. Types d'activités
5. Exceptions
6. Exceptions hors domaines autorisés
7. Sanction financière
8. Peine de prison
9. Procédures de contrôle
10. Temporalité des contrôles
11. Localisation des contrôles

---

## ⏱️ TEMPS D'EXÉCUTION

| Opération | Durée |
|-----------|-------|
| Test rapide (6 Q) | 1-2 min |
| Génération questions | < 1 sec |
| Audit complet (Ollama) | 1.5-3 h |
| Audit complet (Groq) | 30-50 min |
| Analyse résultats | < 1 min |
| Export tous formats | 2 min |

---

## 🚀 WORKFLOW RECOMMANDÉ

```
1. Lancer: python audit.py
   ↓
2. Menu: Choisir une option
   ├─ Option 1: Test rapide (1-2 min)
   ├─ Option 2: Générer questions (1 sec)
   ├─ Option 3: Audit complet (30-50 min)
   ├─ Option 5: Analyser résultats (1 min)
   └─ Option 6: Rapport HTML (1 min)
   ↓
3. Résultats dans results/batch_queries/
```

---

## 📂 HIÉRARCHIE VISUELLE

```
DÉMARRER
  ↓
audit.py  ← Lancer d'ici
  ↓
batch_audit_system/
  ├─ scripts/
  │  ├─ launcher_audit.py ← Menu
  │  ├─ batch_query_system.py ← Principal
  │  ├─ test_quick_query.py ← Test
  │  ├─ analyze_batch_results.py ← Analyse
  │  └─ export_batch_results.py ← Export
  │
  ├─ docs/
  │  ├─ 00_START_HERE.md ⭐
  │  ├─ QUICK_START.md
  │  ├─ README.md
  │  ├─ BATCH_QUERY_GUIDE.md
  │  ├─ INDEX.md
  │  └─ COMPLETION.md
  │
  └─ examples/
     ├─ commands.sh
     └─ examples.md
```

---

## 🎓 POUR LES UTILISATEURS...

### Non-techniques
→ Double-cliquez sur `START_AUDIT.bat`
→ Choisissez une option dans le menu

### Expérimentés
→ Lancez directement les scripts Python que vous voulez
→ Consultez `examples/commands.sh` pour les commandes

### Développeurs
→ Modifiez les scripts Python selon vos besoins
→ Consultez `docs/BATCH_QUERY_GUIDE.md` pour les détails techniques

---

**✨ Prêt? Lancez `python audit.py` ou double-cliquez sur `START_AUDIT.bat`**

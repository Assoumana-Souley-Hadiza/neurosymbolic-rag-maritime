# 🚀 BATCH AUDIT SYSTEM - Structure Organisée

```
batch_audit_system/
├── scripts/                    ← Les 5 scripts Python
│   ├── launcher_audit.py       🎮 Menu interactif (DÉMARRER ICI)
│   ├── batch_query_system.py   🚀 Script principal
│   ├── test_quick_query.py     🧪 Test rapide
│   ├── analyze_batch_results.py 📊 Analyse
│   └── export_batch_results.py  📦 Export
│
├── docs/                       ← Les 5 guides de documentation
│   ├── QUICK_START.md          ⭐ LIRE EN PREMIER (5 min)
│   ├── BATCH_QUERY_GUIDE.md    📖 Guide complet
│   ├── README.md               📄 Vue d'ensemble
│   ├── INDEX.md                📑 Index complet
│   └── COMPLETION.md           ✅ Résumé création
│
├── examples/                   ← Exemples de commandes
│   ├── commands.sh             📝 Commandes shell
│   └── examples.md             📝 Exemples d'utilisation
│
└── README.md                   📄 Ce fichier
```

---

## ⚡ DÉMARRAGE RAPIDE

### 1️⃣ Depuis la racine du projet
```bash
cd c:\Users\HP\Desktop\stage_RAG\version_1_Ontologie
python batch_audit_system/scripts/launcher_audit.py
```

### 2️⃣ Ou depuis le dossier batch_audit_system
```bash
cd batch_audit_system
python scripts/launcher_audit.py
```

### 3️⃣ Menu interactif
Choisissez une option:
- 1️⃣ Test rapide
- 2️⃣ Générer questions
- 3️⃣ Audit complet
- 5️⃣ Analyser résultats
- 6️⃣ Rapport HTML

---

## 📂 Organisation

### `scripts/` - Les 5 scripts Python

| Script | Utilité | Temps |
|--------|---------|-------|
| `launcher_audit.py` | Menu interactif | 0 sec |
| `batch_query_system.py` | Génère + interroge 1 056 questions | 1-3h |
| `test_quick_query.py` | Test avec 6 questions | 1-2 min |
| `analyze_batch_results.py` | Affiche statistiques | < 1 min |
| `export_batch_results.py` | Export multi-formats | 2 min |

### `docs/` - Les 5 guides

| Guide | Contenu |
|-------|---------|
| `QUICK_START.md` | Démarrage 5 minutes ⭐ |
| `BATCH_QUERY_GUIDE.md` | Guide détaillé |
| `README.md` | Vue d'ensemble |
| `INDEX.md` | Index complet |
| `COMPLETION.md` | Résumé du projet |

### `examples/` - Exemples et commandes

| Fichier | Contenu |
|---------|---------|
| `commands.sh` | Commandes shell |
| `examples.md` | Exemples d'utilisation |

---

## 🎯 CAS D'USAGE

### Je veux tester rapidement
```bash
python scripts/test_quick_query.py
```

### Je veux générer les questions
```bash
python scripts/batch_query_system.py --generate-only
```

### Je veux lancer l'audit complet
```bash
python scripts/batch_query_system.py
```

### Je veux analyser les résultats
```bash
python scripts/analyze_batch_results.py
```

### Je veux exporter en différents formats
```bash
python scripts/export_batch_results.py --all
```

### Je veux utiliser le menu (RECOMMANDÉ)
```bash
python scripts/launcher_audit.py
```

---

## 📊 CE QUE VOUS ALLEZ OBTENIR

✅ **1 056 questions** générées automatiquement  
✅ **Réponses du système RAG** stockées en CSV  
✅ **Statistiques par pays** et par interdiction  
✅ **Rapport HTML** visualisable  
✅ **Export multi-formats** (JSON, Excel, CSV pivot)  
✅ **Logs complets** de traçabilité  

---

## ⏱️ TEMPS D'EXÉCUTION

- Test rapide: **1-2 minutes**
- Génération questions: **< 1 seconde**
- Audit complet (Ollama): **1.5-3 heures**
- Audit complet (Groq): **30-50 minutes**
- Analyse: **< 1 minute**

---

## 🔧 CONFIGURATION REQUISE

✓ Python 3.8+  
✓ Neo4j (accessible)  
✓ Ollama (local) OU GROQ_API_KEY (cloud)  
✓ Modèles d'embeddings chargés  

Vérifier: `python ../rag/check_environment.py`

---

## 📚 DOCUMENTATION

### Pour débuter
👉 Lire: `docs/QUICK_START.md`

### Pour comprendre le système
👉 Lire: `docs/README.md`

### Pour les détails techniques
👉 Lire: `docs/BATCH_QUERY_GUIDE.md`

### Pour tout découvrir
👉 Lire: `docs/INDEX.md`

---

## 💾 RÉSULTATS

Les résultats seront sauvegardés dans:
```
../results/batch_queries/
├── questions_generees.csv
├── resultats_audit_*.csv
├── resume_audit_*.json
├── rapport_audit_*.html
└── exports/
    ├── tableau_pivot_*.xlsx
    ├── resultats_structures.json
    └── ...
```

---

## 🚀 COMMANDE DE DÉMARRAGE

**La plus simple:**
```bash
python scripts/launcher_audit.py
```

**Puis choisissez une option dans le menu!**

---

## 🆘 AIDE RAPIDE

| Question | Réponse |
|----------|--------|
| Comment commencer? | Lancer `launcher_audit.py` |
| Combien de temps? | 30-50 min (Groq) ou 1-3h (Ollama) |
| Quels fichiers? | CSV, JSON, Excel, HTML |
| Où sont les résultats? | `../results/batch_queries/` |
| Erreur? | Vérifier `batch_query.log` |

---

**✨ Prêt! Lancez `python scripts/launcher_audit.py`**

# 🎯 AUDIT AUTOMATIQUE - GUIDE DE DÉMARRAGE RAPIDE

## ⚡ Démarrage en 3 étapes

### 1️⃣ Vérifier que le système est prêt
```bash
python rag/check_environment.py
```

### 2️⃣ Tester rapidement avec 6 questions
```bash
python test_quick_query.py
```

### 3️⃣ Lancer l'audit complet
```bash
python launcher_audit.py
```

**Ou directement:**
```bash
python batch_query_system.py
```

---

## 📊 Qu'est-ce que ce système fait?

Pose **1 056 questions** (16 pays × 6 interdictions × 11 questions chacune) au système RAG et récupère les réponses:

```
Exemple de question:
"Est-ce qu'il existe un article portant sur l'interdiction du chalutage de fond alg ?"
↓
Système RAG
↓
Réponse: "OUI" / "NON" / "ERREUR"
↓
Stockage dans CSV
```

---

## 📁 Fichiers créés

| Fichier | Description |
|---------|-------------|
| `launcher_audit.py` | 🎮 Menu interactif pour guider l'exécution |
| `batch_query_system.py` | 🚀 Script principal d'interrogation automatique |
| `test_quick_query.py` | 🧪 Test rapide (6 questions) |
| `analyze_batch_results.py` | 📊 Analyse des résultats |
| `BATCH_QUERY_GUIDE.md` | 📚 Guide complet détaillé |
| `QUICK_START.md` | ⚡ Ce fichier |

---

## 📍 Résultats

Tous les résultats sont sauvegardés dans:
```
results/batch_queries/
├── questions_generees.csv              (Questions générées)
├── resultats_audit_YYYYMMDD_HHMMSS.csv (Réponses du système)
├── resume_audit_YYYYMMDD_HHMMSS.json   (Résumé statistique)
└── rapport_audit_YYYYMMDD_HHMMSS.html  (Rapport HTML)
```

---

## 🚀 Les 4 modes d'utilisation

### Mode 1: Test rapide 🧪
```bash
python test_quick_query.py
```
- ✅ 6 questions de démonstration
- ✅ Vérifie que le système fonctionne
- ✅ < 1 minute

### Mode 2: Générer uniquement 📋
```bash
python batch_query_system.py --generate-only
```
- ✅ Crée le fichier CSV des questions
- ✅ Permet de les vérifier avant interrogation
- ✅ < 1 seconde

### Mode 3: Interroger uniquement 🔍
```bash
python batch_query_system.py --query-only
```
- ✅ Charge les questions existantes
- ✅ Interroge le système
- ✅ Pour reprendre après interruption
- ✅ 1-3 heures

### Mode 4: Complet 🎯
```bash
python batch_query_system.py
```
- ✅ Génère les questions
- ✅ Interroge le système
- ✅ Crée les fichiers de résultats
- ✅ 1-3 heures

---

## 📊 Analyser les résultats

### Voir les statistiques
```bash
python analyze_batch_results.py
```

### Générer un rapport HTML
```bash
python analyze_batch_results.py --export-html
```

---

## ⚙️ Configuration préalable

### Vérifier que Neo4j est accessible
```bash
python rag/check_environment.py
```

### Optionnel: Utiliser Groq API (5x plus rapide)
```bash
# Windows
set GROQ_API_KEY=votre_clé_api

# Linux/Mac
export GROQ_API_KEY=votre_clé_api
```

---

## ⏱️ Temps d'exécution estimé

| Étape | Ollama (Local) | Groq (Cloud) |
|-------|--|--|
| Test rapide (6 Q) | 1-2 min | 15-30 sec |
| Audit complet (1056 Q) | 1.5-3h | 30-50 min |

---

## 🎓 Pays couverts

🌍 **15 pays africains** : Algérie, Bénin, Cameroun, Comores, Congo, Côte d'Ivoire, Djibouti, Gabon, Guinée, Madagascar, Maroc, Mauritanie, Sénégal, Togo, Tunisie

🇪🇺 **1 pays européen** : France

---

## 📋 Interdictions couvertes

1. ⛓️ Chalutage de fond
2. 🐋 Chasse à la baleine
3. 🏗️ Construction côtière
4. 🏖️ Extraction de sable
5. 🦅 Oiseaux Marins
6. 🛢️ Rejet d'hydrocarbures

**Chaque interdiction = 11 questions par pays**

---

## 💾 Exemple de résultat

```csv
Pays,Code_Pays,Interdiction,Numero_Question,Question,Reponse,Modele,Timestamp
Algérie,alg,Chalutage de fond,1,Est-ce qu'il existe...,OUI,mistral,2024-05-15T14:30:22
Algérie,alg,Chalutage de fond,2,Est-ce qu'il existe...,NON,mistral,2024-05-15T14:30:45
...
```

---

## 🐛 Dépannage rapide

| Problème | Solution |
|----------|----------|
| "LLM non disponible" | Lancer Ollama ou définir GROQ_API_KEY |
| "Neo4j not reachable" | Vérifier que Neo4j est lancé |
| "Aucun fichier trouvé" | Créer `results/batch_queries/` |
| Résultat vide | Vérifier les logs: `batch_query.log` |

---

## 📞 Besoin d'aide?

- 📖 Guide complet: `BATCH_QUERY_GUIDE.md`
- 🔍 Logs: `batch_query.log`
- ⚙️ Vérifier l'env: `python rag/check_environment.py`

---

## 🎮 Interface interactive (RECOMMANDÉ)

Pour une meilleure expérience, utilisez le menu interactif:

```bash
python launcher_audit.py
```

Vous aurez un menu guidé pour chaque étape!

---

**✨ Vous êtes prêt! Lancez `python launcher_audit.py` pour commencer.**

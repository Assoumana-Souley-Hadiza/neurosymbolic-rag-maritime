# 📚 Documentation - Système d'Audit Automatique

## ⭐ PAR OÙ COMMENCER?

### 1️⃣ Nouveau utilisateur? (5 min)
**Lire:** [`QUICK_START.md`](QUICK_START.md)
- Démarrage en 3 étapes
- 4 modes d'utilisation
- Questions/réponses fréquentes

### 2️⃣ Besoin de plus de détails?
**Lire:** [`README.md`](README.md)
- Vue d'ensemble du système
- Guide de démarrage en 5 minutes
- Résumé des fichiers générés

### 3️⃣ Question technique spécifique?
**Lire:** [`BATCH_QUERY_GUIDE.md`](BATCH_QUERY_GUIDE.md)
- Guide technique complet
- Configuration avancée
- Dépannage détaillé

### 4️⃣ Tous les détails?
**Lire:** [`INDEX.md`](INDEX.md)
- Index complet de tous les fichiers
- Flux de travail typiques
- Commandes rapides

---

## 📋 Documents de Référence

| Document | Contenu | Public |
|----------|---------|--------|
| **QUICK_START.md** | Guide 5 min | Tous |
| **README.md** | Vue d'ensemble | Tous |
| **BATCH_QUERY_GUIDE.md** | Détails techniques | Avancé |
| **INDEX.md** | Index complet | Référence |
| **COMPLETION.md** | Résumé du projet | Tous |

---

## 🎯 Questions Fréquentes

### Q: Par où je commence?
**A:** Lancer `python audit.py` depuis la racine

### Q: Combien de temps ça prend?
**A:** 
- Test rapide: 1-2 minutes
- Audit complet (Groq): 30-50 minutes
- Audit complet (Ollama): 1-3 heures

### Q: Quels formats de résultats?
**A:** CSV, JSON, Excel, HTML, Pivot tables

### Q: Où sont les résultats?
**A:** `results/batch_queries/`

### Q: Ça regroupe quoi?
**A:** 
- 16 pays
- 6 interdictions
- 11 questions par interdiction
- **Total: 1 056 questions**

### Q: Comment je reprends après interruption?
**A:** `python batch_audit_system/scripts/batch_query_system.py --query-only`

---

## 🚀 Commandes Rapides

```bash
# Depuis la racine

# Menu interactif
python audit.py

# Test rapide
python batch_audit_system/scripts/test_quick_query.py

# Audit complet
python batch_audit_system/scripts/batch_query_system.py

# Analyser résultats
python batch_audit_system/scripts/analyze_batch_results.py

# Tous les exports
python batch_audit_system/scripts/export_batch_results.py --all
```

---

## 📊 Structure des Données

### 1 056 Questions = 16 pays × 6 interdictions × 11 questions

**Pays:** Algérie, Bénin, Cameroun, Comores, Congo, Côte d'Ivoire, Djibouti, Gabon, Guinée, Madagascar, Maroc, Mauritanie, Sénégal, Togo, Tunisie, France

**Interdictions:**
1. Chalutage de fond
2. Chasse à la baleine
3. Construction côtière
4. Extraction de sable
5. Oiseaux Marins
6. Rejet d'hydrocarbures

---

## ⚙️ Configuration Requise

✓ Python 3.8+
✓ Neo4j (accessible)
✓ Ollama (local) OU GROQ_API_KEY (cloud)
✓ Modèles d'embeddings chargés

**Vérifier:** `python ../rag/check_environment.py`

---

## 🔍 Besoin d'aide?

| Problème | Solution |
|----------|----------|
| Ne sais pas par où commencer | Lancer `python audit.py` |
| Erreur "LLM not available" | Définir GROQ_API_KEY ou lancer Ollama |
| Erreur "Neo4j not reachable" | Vérifier que Neo4j est lancé |
| Résultats vides | Consulter `batch_query.log` |
| Première utilisation | Lire `QUICK_START.md` |

---

## 📖 Lectures Recommandées

### Pour les impatients (5 min)
→ `QUICK_START.md`

### Pour comprendre (15 min)
→ `README.md`

### Pour l'utilisation avancée (30 min)
→ `BATCH_QUERY_GUIDE.md`

### Pour la référence complète
→ `INDEX.md`

---

**Vous êtes prêt! Lancez `python audit.py` 🚀**

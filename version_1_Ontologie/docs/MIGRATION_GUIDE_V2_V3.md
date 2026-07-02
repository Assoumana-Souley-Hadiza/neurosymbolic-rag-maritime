# 🔄 MIGRATION GUIDE - V2 → V3

## 📌 Vue d'ensemble

Passer de l'Architecture V2 à V3 est **facile et non-destructif**. V3 est rétro-compatible.

**Temps estimé** : 15-30 minutes

---

## ✅ Étape 1: Sauvegarder (optionnel mais recommandé)

```bash
# Sauvegarder l'état actuel
git add .
git commit -m "Backup before V3 migration"
```

---

## ✅ Étape 2: Installer les dépendances

```bash
# Mettre à jour requirements.txt
pip install python-dotenv requests

# Ou réinstaller complètement
pip install -r rag/requirements.txt
```

---

## ✅ Étape 3: Configurer les secrets

### 3a. Créer `.env.local`

```bash
# Option 1: Copier depuis example
cp .env.local.example .env.local

# Option 2: Créer manuellement
cat > .env.local << 'EOF'
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DB=neo4j
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
LOG_LEVEL=INFO
EMBEDDING_VERSION=bge-m3-v1
BM25_VERSION=bm25-v1
EOF
```

### 3b. Vérifier que .env.local est ignoré

```bash
# Vérifier
git status
# Output: .env.local devrait être dans "Ignored files"

# Si absent, le .gitignore a été mis à jour
```

---

## ✅ Étape 4: Créer la structure de répertoires

```bash
# Créer automatiquement
python setup_v3.py

# Ou manuellement
mkdir -p data/raw
mkdir -p data/processed/embeddings
mkdir -p data/processed/indexes
mkdir -p data/processed/chunks
mkdir -p results
```

---

## ✅ Étape 5: Tester la configuration

```bash
# Test 1: Charger config
python -c "from rag.config import *; print('✅ Config OK')"

# Test 2: Health check
python setup_v3.py

# Test 3: Lancer Streamlit
streamlit run rag/api/app_streamlit.py
```

---

## 📊 Tableau de Migration

| Composant | V2 | V3 | Migration |
|-----------|----|----|-----------|
| Secrets | En dur | .env.local | ✅ Auto |
| Logging | Basique | Structuré | ✅ Auto |
| Versioning | Non | Oui | ✅ Auto |
| Répertoires | Chaotique | Organisé | ✅ Manuel (simple) |
| Health Check | Non | Oui | ✅ Auto |
| API | Neo4jBridge | Neo4jBridgeSafe | ✅ Compatible |

---

## 🔄 Ce qui ne change PAS

- ✅ Code source `rag/core/` → inchangé
- ✅ Modèles (bge-m3, mistral) → inchangés
- ✅ Base de données Neo4j → inchangée
- ✅ API Streamlit → compatible
- ✅ Pipeline RAG → inchangé

---

## 🔄 Ce qui change

- ⚠️ Répertoires des outputs
- ⚠️ Configuration (maintenant externalisée)
- ⚠️ Logging (nouveau format)
- 🎯 API Neo4j (recommandée: safe wrapper)

---

## 🆘 Si vous avez des erreurs

### Erreur: "NEO4J_PASSWORD manquante"
```bash
# Solution: Créer .env.local
echo "NEO4J_PASSWORD=your_password" > .env.local
```

### Erreur: "No module named 'dotenv'"
```bash
# Solution: Installer python-dotenv
pip install python-dotenv
```

### Erreur: "ChromaDB/BM25 index not found"
```bash
# Solution: Les embeddings sont toujours dans rag/output/
# Ils seront migrés lors du prochain ingestion
# Ou copiez-les manuellement:
cp -r rag/output/chroma_db data/processed/embeddings/chroma_db_bge-m3-v1/
cp -r rag/output/bm25_index data/processed/indexes/bm25_bm25-v1/
```

### Erreur: "Neo4j connection failed"
```bash
# Solution: Health check utilisera RDF fallback automatiquement
# Vérifier que Neo4j est lancé:
docker ps | grep neo4j
```

---

## 📋 Checklist de Validation

- [ ] `.env.local` créé et configuré
- [ ] `pip install python-dotenv` ✅
- [ ] `python setup_v3.py` s'exécute sans erreur
- [ ] `streamlit run rag/api/app_streamlit.py` lance OK
- [ ] Sidebar affiche Health Check (pas ❌)
- [ ] Une requête teste → réponse générée

---

## 🎯 Après la migration

### Données existantes

**Ancien chemin** : `rag/output/chroma_db/` + `rag/output/bm25_index/`  
**Nouveau chemin** : `data/processed/embeddings/chroma_db_bge-m3-v1/`

Pour **continuer avec les données existantes** :
```bash
# Copier dans nouveau répertoire
cp -r rag/output/chroma_db data/processed/embeddings/chroma_db_bge-m3-v1
cp -r rag/output/bm25_index data/processed/indexes/bm25_bm25-v1
```

### Monitoring

**Nouveaux fichiers à vérifier** :
- `results/rag_system.log` → Logs structurés
- `results/metrics_*.json` → Métriques exportées
- `results/versions.json` → Versions des modèles

---

## 🚀 Cas d'Usage Courants

### 1. Ajouter un nouveau modèle d'embedding

```python
# Avant: Crash ou remplacement silencieux
# Après: Versioning clair

# .env.local
EMBEDDING_VERSION=bge-m3-v2  # Nouveau modèle

# V3 crée automatiquement: data/processed/embeddings/chroma_db_bge-m3-v2/
```

### 2. Analyser les performances

```bash
# V3 exporte les métriques
python -c "
from rag.utils.metrics import get_metrics_logger
from rag.config import OUTPUT_DIR

metrics = get_metrics_logger(OUTPUT_DIR)
# Les métriques collectées sont dans metrics.metrics
print(metrics.summary_stats())
"
```

### 3. Diagnostiquer un problème

```bash
# V3 offre diagnostic complet
python setup_v3.py
# Affiche quel composant ne fonctionne pas

# Ou programmatiquement
from rag.utils.health_check import get_health_check
health = get_health_check()
health.full_check()
print(health.get_errors())
```

---

## 📞 Support Migration

Si vous avez des problèmes:

1. **Vérifier les logs** : `cat results/rag_system.log`
2. **Exécuter health check** : `python setup_v3.py`
3. **Vérifier .env.local** : `cat .env.local` (secrets masqués bien sûr)
4. **Rollback** : `git checkout rag/api/app_streamlit.py` (si nécessaire)

---

## 🎉 Félicitations!

Vous êtes maintenant sur l'Architecture V3! 🚀

**Bénéfices gagnés**:
- ✅ Secrets sécurisés
- ✅ Observabilité complète
- ✅ Versioning des modèles
- ✅ Résilience (graceful degradation)
- ✅ Structure organisée

Consultez `docs/ARCHITECTURE_V3.md` pour plus de détails.

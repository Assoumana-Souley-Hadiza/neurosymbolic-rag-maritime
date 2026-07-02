# 📦 GUIDE D'INSTALLATION - RAG MARITIME

## Prérequis

- **Python 3.9+** (vérifié avec `python --version`)
- **pip** pour installer les packages
- **Git** (optionnel, pour versionner)
- **4 GB RAM minimum** (8 GB recommandé)
- **5 GB espace disque** (pour index + dépendances)

## ✅ Étape 1: Vérifier l'environnement

```powershell
# Dans PowerShell (Windows)
python --version
pip --version
```

Résultat attendu:
```
Python 3.9.x ou supérieur
pip 21.0 ou supérieur
```

## 📥 Étape 2: Installer les dépendances

```powershell
# Se placer dans le dossier rag_system
cd "C:\Users\HP\Downloads\version_1_Ontologie\rag_system"

# Installer les packages
pip install -r requirements.txt
```

**Durée estimée:** 10-20 minutes

### Dépendances alternatives (optionnel)

Si vous rencontrez des problèmes de compilations C++:

```powershell
# Installer pré-compilé avec index
pip install sentence-transformers --only-binary :all:

# Ou utiliser version plus légère
pip install sentence-transformers==2.2.0 --no-cache-dir
```

## 🔄 Étape 3: Vérifier l'installation

```powershell
# Tester les imports Python
python -c "import pdfplumber; import chromadb; import sentence_transformers; print('✅ Tous les modules importés')"
```

## 🚀 Étape 4: Exécuter la pipeline

### Option A: Pipeline complète (recommandé pour la première fois)

```powershell
# Depuis le dossier rag_system
python run_pipeline.py
```

**Durée estimée:**
- Extraction PDF: 5-10 minutes
- Embedding: 10-20 minutes
- Intégration ontologie: 2-5 minutes
- **Total: 20-40 minutes**

Vous verrez:
```
======================================================================
  🚀 SYSTÈME RAG MARITIME - DÉMARRAGE COMPLET
======================================================================

...logs détaillés...

======================================================================
✅ SYSTÈME RAG COMPLÈTEMENT INITIALISÉ
======================================================================
```

### Option B: Étapes individuelles

**Étape 4a: Extraction PDF**
```powershell
python pdf_extractor.py

# Résultat: output/chunks.json (contient tous les chunks)
```

**Étape 4b: Embedding et indexation**
```powershell
python embeddings_pipeline.py

# Résultat: output/chroma_db/ (index vectoriel)
```

**Étape 4c: Intégration ontologie**
```powershell
python ontology_integration.py

# Tests des requêtes combinées
```

## 🌐 Étape 5: Lancer l'interface Web (optionnel)

```powershell
# Installer Streamlit si pas déjà fait
pip install streamlit

# Lancer l'app
streamlit run app_streamlit.py
```

L'app s'ouvre automatiquement sur: `http://localhost:8501`

## 📊 Étape 6: Vérifier les résultats

### 1. Vérifier l'extraction PDF

```powershell
# Lister les fichiers créés
ls output/

# Consulter les chunks
# Ouvrir output/chunks.json dans VSCode
```

Vous devez voir:
- `chunks.json` - contient ~1200 chunks
- `chroma_db/` - dossier avec l'index vectoriel
- `rag_system.log` - logs détaillés

### 2. Vérifier l'indexation ChromaDB

```powershell
python -c "
from embeddings_pipeline import EmbeddingsPipeline
pipeline = EmbeddingsPipeline()
stats = pipeline.get_stats()
print(f'Documents indexés: {stats[\"total_documents\"]}')
"
```

Résultat attendu:
```
Documents indexés: 1200
```

### 3. Tester une requête

```powershell
python -c "
from embeddings_pipeline import EmbeddingsPipeline
pipeline = EmbeddingsPipeline()
results = pipeline.search('baleines', top_k=3)
for r in results:
    print(f'- {r[\"metadata\"][\"source\"]}: {r[\"text\"][:80]}...')
"
```

Résultat attendu:
```
- Ben162059.pdf: [texte relevant sur les baleines]
- gui158572.pdf: [texte relevant sur les baleines]
- Mau164733.pdf: [texte relevant sur les baleines]
```

## 🔧 Troubleshooting

### Problème 1: "ModuleNotFoundError: No module named..."

```powershell
# Réinstaller toutes les dépendances
pip install -r requirements.txt --force-reinstall --no-cache-dir
```

### Problème 2: "RuntimeError: CUDA out of memory"

Le GPU n'a pas assez de mémoire. Solution:

```powershell
# Éditer config.py
# Remplacer: device = "cuda"
# Par: device = "cpu"
```

Ou réduire la taille des batches:

```python
pipeline.index_chunks(chunks, batch_size=8)  # au lieu de 32
```

### Problème 3: "Extraction PDF très lente"

Réduire la taille des chunks dans `config.py`:

```python
PDF_CONFIG["chunk_size"] = 400  # au lieu de 800
```

### Problème 4: Erreur "pdfplumber" lors de l'extraction

```powershell
# Réinstaller pdfplumber
pip uninstall pdfplumber -y
pip install pdfplumber==0.9.0
```

### Problème 5: ChromaDB ne persiste pas

```powershell
# Supprimer l'index et recommencer
rm -r output/chroma_db/
python embeddings_pipeline.py
```

### Problème 6: "Permission denied" sur Windows

```powershell
# Exécuter PowerShell en tant qu'administrateur
# Puis réessayer les commandes pip
```

## 💾 Fichiers générés

Après une exécution complète:

```
rag_system/
├── output/
│   ├── chunks.json                 (~30 MB) - Tous les chunks
│   ├── chroma_db/                 (~200 MB) - Index vectoriel
│   │   ├── data.parquet
│   │   ├── metadata.parquet
│   │   └── *
│   └── rag_system.log             (~5 MB) - Logs d'exécution
└── ...
```

**Espace total utilisé:** ~250-300 MB

## ✨ Vérification finale

Pour confirmer que tout fonctionne:

```powershell
# Exécuter le test complet
python -c "
from embeddings_pipeline import EmbeddingsPipeline
from ontology_integration import OntologyIntegration, QueryRouter

print('✓ Loading...')
pipeline = EmbeddingsPipeline()
ontology = OntologyIntegration()
router = QueryRouter(pipeline, ontology)

print('✓ Testing query...')
result = router.route_query('protection baleines', top_k=3)
print(f'✓ Found {len(result[\"retrieved_documents\"])} documents')
print('✅ Système RAG opérationnel!')
"
```

Résultat attendu:
```
✓ Loading...
✓ Testing query...
✓ Found 5 documents
✅ Système RAG opérationnel!
```

## 📚 Prochaines étapes après l'installation

1. **Tester l'interface web**
   ```bash
   streamlit run app_streamlit.py
   ```

2. **Ajouter un LLM** (optionnel)
   - Installer Ollama: https://ollama.ai
   - Ou utiliser OpenAI API

3. **Intégrer avec l'ontologie complètement**
   - Vérifier que `maritime_ontology.owl` existe
   - Implémenter les requêtes SPARQL complètes

4. **Ajouter du feedback utilisateur**
   - Noter les réponses utiles
   - Améliorer les embeddings

## 🆘 Support

Si vous rencontrez un problème:

1. **Consulter les logs:**
   ```bash
   cat output/rag_system.log | tail -50
   ```

2. **Vérifier les prérequis:**
   ```bash
   python --version  # 3.9+
   pip --version     # 21+
   ```

3. **Réinstaller les packages:**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

---

**Dernier update:** Avril 2026
**Version:** Installation v0.1.0

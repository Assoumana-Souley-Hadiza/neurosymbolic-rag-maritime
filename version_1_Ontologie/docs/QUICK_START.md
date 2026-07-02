# ⚡ QUICK START - RAG MARITIME

**Démarrage en 5 minutes**

## 1️⃣ Vérifier l'environnement

```powershell
cd "C:\Users\HP\Downloads\version_1_Ontologie\rag_system"
python check_environment.py
```

Vous devez voir:
```
✅ Python 3.9.x OK
✅ pdfplumber
✅ sentence_transformers
✅ chromadb
... (tous en ✅)
```

## 2️⃣ Installer les dépendances (1ère fois seulement)

```powershell
pip install -r requirements.txt
```

**Durée:** 10-20 minutes

## 3️⃣ Lancer la pipeline complète

```powershell
python run_pipeline.py
```

**Durée:** 20-40 minutes (selon CPU)

Vous verrez:
```
======================================================================
  🚀 SYSTÈME RAG MARITIME - DÉMARRAGE COMPLET
======================================================================

PHASE 1: EXTRACTION PDF
  ✓ Ben162059.pdf: 45 chunks
  ✓ gui158572.pdf: 38 chunks
  ...

PHASE 2: EMBEDDING & INDEXATION
  ✓ Batch 1/38 - 32 chunks
  ✓ Batch 2/38 - 32 chunks
  ...

PHASE 3: INTÉGRATION ONTOLOGIE
  Requête: 'protection des baleines'
    1. [Ben162059.pdf] La protection des baleines...
    ...

✅ SYSTÈME RAG COMPLÈTEMENT INITIALISÉ
```

## 4️⃣ Tester une requête simple

```powershell
python -c "
from embeddings_pipeline import EmbeddingsPipeline
pipeline = EmbeddingsPipeline()
results = pipeline.search('baleines', top_k=3)
for r in results:
    print(f'✓ {r[\"metadata\"][\"source\"]}: {r[\"text\"][:100]}...')
"
```

## 5️⃣ Lancer l'interface web (optionnel)

```powershell
# Installer Streamlit
pip install streamlit

# Lancer l'app
streamlit run app_streamlit.py
```

Ouvrir: http://localhost:8501

---

## 📁 Fichiers créés après exécution

```
rag_system/output/
├── chunks.json              # ~1200 chunks extraits
├── chroma_db/               # Index vectoriel (persistant)
└── rag_system.log          # Logs détaillés
```

## 🎯 Prochaines étapes

1. **Tester l'interface web** → `streamlit run app_streamlit.py`
2. **Ajouter un LLM** → Installer Ollama ou utiliser OpenAI
3. **Intégrer avec l'ontologie** → Implémenter requêtes SPARQL complètes
4. **Déployer en production** → REST API + conteneur Docker

## 🆘 Problèmes courants

| Problème | Solution |
|----------|----------|
| "Module not found" | `pip install -r requirements.txt --upgrade` |
| Erreur extraction PDF | Vérifier `RAG_data/` a les PDFs |
| ChromaDB slow | Réduire chunk_size dans config.py |
| Erreur GPU/CUDA | Remplacer "cuda" → "cpu" dans config.py |

## 📊 Commandes utiles

```powershell
# Vérifier les chunks créés
python -c "import json; print(f'{len(json.load(open(\"output/chunks.json\")))} chunks')"

# Vérifier l'index
python -c "from embeddings_pipeline import EmbeddingsPipeline; p = EmbeddingsPipeline(); print(p.get_stats())"

# Voir les logs
tail -f output/rag_system.log

# Réinitialiser (si problème)
rm -r output/chunks.json output/chroma_db/
python run_pipeline.py
```

---

**✅ Vous êtes prêt!**

Lancez: `python run_pipeline.py`

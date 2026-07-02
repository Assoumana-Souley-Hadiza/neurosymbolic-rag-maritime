"""
INDEX - Navigation complète du système RAG Maritime
"""

# 📑 INDEX FICHIERS RAG_SYSTEM

## 🚀 DÉMARRER ICI

1. **QUICK_START.md** ← LIS CE FICHIER D'ABORD
   - Démarrage en 5 minutes
   - 5 étapes simples
   - Commandes pour tester

2. **check_environment.py** ← EXECUTE ENSUITE
   - Vérifie Python 3.9+
   - Vérifie les packages
   - Vérifie la structure

3. **run_pipeline.py** ← PUIS CECI
   - Lance Phase 1-3 d'un coup
   - Durée: 20-40 minutes
   - Crée tout automatiquement

---

## 📚 DOCUMENTATION (par ordre de profondeur)

### 1️⃣ Pour commencer rapidement
```
QUICK_START.md           5 min    Démarrage immédiat
check_environment.py     2 min    Vérifier l'environnement
```

### 2️⃣ Pour installer proprement
```
INSTALLATION.md          15 min   Guide étape par étape
requirements.txt         -        Dépendances Python
```

### 3️⃣ Pour comprendre l'architecture
```
ARCHITECTURE.md          20 min   Vue technique complète
README.md                15 min   Documentation API
```

### 4️⃣ Pour développer/étendre
```
config.py                5 min    Paramètres à ajuster
PROJECT_SUMMARY.md       10 min   Résumé exécutif
```

---

## 🔧 SCRIPTS & MODULES

### Scripts d'exécution (standalone)
```
run_pipeline.py          ⭐ PRINCIPAL: Lance tout (Phase 1-3)
  ├─ Appelle pdf_extractor.py
  ├─ Appelle embeddings_pipeline.py
  └─ Appelle ontology_integration.py

check_environment.py     Vérifier prérequis avant de lancer
```

### Phase 1: Extraction PDF
```
pdf_extractor.py         Extraction + chunking des PDFs
  - Classe: PDFExtractor
  - Méthode principale: process_all_pdfs()
  - Sortie: output/chunks.json (~30 MB)
  - Durée: 5-10 minutes
```

### Phase 2: Embedding & Indexation
```
embeddings_pipeline.py   Embedding + ChromaDB indexation
  - Classe: EmbeddingsPipeline
  - Méthode principale: index_chunks()
  - Sortie: output/chroma_db/ (~200 MB)
  - Durée: 10-20 minutes
```

### Phase 3: Intégration Ontologie
```
ontology_integration.py  Intégration RDF/Ontologie
  - Classe: OntologyIntegration, QueryRouter
  - Méthode principale: demonstrate_integration()
  - Entrée: ontology.owl + chunks indexés
  - Durée: 1-5 minutes
```

### Phase 4: Interface Web (TODO)
```
app_streamlit.py         Interface Streamlit interactive
  - Commande: streamlit run app_streamlit.py
  - Port: http://localhost:8501
  - Status: ✅ Complète, prête à l'emploi
```

### Phase 5: API REST (TODO)
```
app_flask_template.py    Template API REST (non implémenté)
  - Framework: Flask
  - Status: Template seulement
```

---

## ⚙️ CONFIGURATION

### Fichier principal de config
```
config.py
├─ RAG_DATA_DIR           Chemin vers RAG_data/
├─ PDF_CONFIG             chunk_size, overlap, etc.
├─ EMBEDDING_CONFIG       Modèle, dimensions, GPU
├─ CHROMA_CONFIG          Persistance, settings
└─ EXTRACTION_CONFIG      OCR, tables, images
```

### Paramètres à ajuster selon vos besoins
```
PDF_CONFIG["chunk_size"] = 800        (défaut: 800 tokens)
EMBEDDING_CONFIG["device"] = "cpu"    (cpu ou cuda)
EMBEDDING_CONFIG["model_name"]        (autre modèle ST?)
```

---

## 📊 DOSSIERS DE SORTIE (créés automatiquement)

```
rag_system/output/
├── chunks.json           ~30 MB      JSON avec tous les chunks
├── chroma_db/            ~200 MB     Index vectoriel ChromaDB
│   ├── data.parquet                  Embeddings
│   ├── metadata.parquet              Métadonnées
│   └── index.parquet                 Index HNSW
└── rag_system.log        ~5 MB       Logs détaillés d'exécution
```

---

## 🎯 CAS D'USAGE

### 1. Recherche simple
```python
from embeddings_pipeline import EmbeddingsPipeline

pipeline = EmbeddingsPipeline()
results = pipeline.search("baleines", top_k=5)

for doc in results:
    print(f"{doc['metadata']['source']}: {doc['text'][:100]}")
```

### 2. Recherche avec ontologie
```python
from ontology_integration import QueryRouter, OntologyIntegration
from embeddings_pipeline import EmbeddingsPipeline

pipeline = EmbeddingsPipeline()
ontology = OntologyIntegration()
router = QueryRouter(pipeline, ontology)

result = router.route_query("protection baleines")
print(f"Documents: {len(result['retrieved_documents'])}")
print(f"Contexte ontologie: {result['ontology_context']}")
```

### 3. Filtrer par catégorie
```python
pipeline = EmbeddingsPipeline()

# Requête + filtrage
results = pipeline.search("hydrocarbure", top_k=5)
rejet_docs = [r for r in results if r['metadata']['category'] == 'Rejet hydrocarbure']

print(f"Trouvé {len(rejet_docs)} documents sur rejets hydrocarbures")
```

### 4. Interface web
```bash
streamlit run app_streamlit.py
# Ouvre http://localhost:8501 automatiquement
```

---

## 🚨 TROUBLESHOOTING RAPIDE

| Problème | Fichier | Solution |
|----------|---------|----------|
| Module not found | INSTALLATION.md | pip install -r requirements.txt |
| Pas de PDFs | RAG_data/ | Vérifier que les PDFs existent |
| Extraction lente | config.py | Réduire chunk_size |
| Erreur CUDA | config.py | device = "cpu" |
| ChromaDB slow | config.py | batch_size = 16 |

---

## 📞 FLUX D'EXÉCUTION RECOMMANDÉ

```
1. cd rag_system
2. python check_environment.py              (2 min)
3. pip install -r requirements.txt          (10-20 min)
4. python run_pipeline.py                   (20-40 min)
5. python -c "from embeddings_pipeline import EmbeddingsPipeline; ..."  (test)
6. streamlit run app_streamlit.py           (optionnel)
```

**Durée totale:** ~1 heure

---

## 🔄 MISE À JOUR FUTURE

Si vous ajoutez des PDFs:

```powershell
# 1. Ajouter PDFs dans RAG_data/
# 2. Réinitialiser
rm -r output/chunks.json output/chroma_db/
# 3. Relancer
python run_pipeline.py
```

---

## 📦 STRUCTURE COMPLÈTE

```
rag_system/
├── 📄 QUICK_START.md              ⭐ Commencer ici
├── 📄 INSTALLATION.md
├── 📄 ARCHITECTURE.md
├── 📄 README.md
├── 📄 PROJECT_SUMMARY.md
├── 📄 INDEX.txt                   (ce fichier)
│
├── 🐍 EXÉCUTION
│   ├── run_pipeline.py            ⭐ Lancer ceci
│   ├── check_environment.py       ✅ Vérifier d'abord
│   ├── pdf_extractor.py
│   ├── embeddings_pipeline.py
│   ├── ontology_integration.py
│   └── config.py
│
├── 🌐 WEB
│   ├── app_streamlit.py           ✅ Complète
│   └── app_flask_template.py      (template seulement)
│
├── 📦 SETUP
│   ├── requirements.txt
│   └── __init__.py
│
└── 📁 output/ (créé automatiquement)
    ├── chunks.json
    ├── chroma_db/
    └── rag_system.log
```

---

## 🎓 CONCEPTS CLÉS

**Chunking:** Division des PDFs en petits morceaux (800 tokens)
**Embedding:** Conversion du texte en vecteurs (384 dimensions)
**Vector DB:** Base de données pour recherche rapide (ChromaDB)
**RAG:** Retrieval-Augmented Generation (recherche + génération)
**Ontologie:** Graphe de connaissances (RDF/OWL)

---

## 📈 PERFORMANCE ATTENDUE

| Opération | Durée |
|-----------|-------|
| Extraction 58 PDFs | 5-10 min |
| Embedding 1200 chunks | 10-20 min |
| Recherche vectorielle | <500ms |
| Generation LLM | 2-5 sec |
| Total (1ère exécution) | 20-40 min |

---

## 🆘 BESOIN D'AIDE?

1. **QUICK_START.md** - Pour démarrer vite
2. **INSTALLATION.md** - Pour l'installation détaillée
3. **ARCHITECTURE.md** - Pour comprendre comment ça marche
4. **Logs:** `output/rag_system.log` - Pour diagnostiquer les erreurs

---

**Dernière mise à jour:** Avril 2026
**Version:** 0.1.0
**Status:** ✅ Production Ready (Phase 1-3)

Bon courage! 🚀

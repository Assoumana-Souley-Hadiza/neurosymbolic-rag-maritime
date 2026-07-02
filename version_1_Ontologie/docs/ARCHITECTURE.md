# 🏗️ ARCHITECTURE TECHNIQUE - RAG MARITIME

## 📐 Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION UTILISATEUR                      │
│  (Streamlit Web UI / REST API / CLI)                            │
└───────────────────────┬─────────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼────────────┐        ┌────────▼────────────┐
│   QUERY ROUTER     │        │   LLMS (optionnel)  │
│  (Orchestration)   │        │  Ollama / OpenAI    │
└───────┬────────────┘        └────────┬────────────┘
        │                              │
        ├──────────────┬───────────────┤
        │              │               │
┌───────▼──────┐  ┌────▼─────────┐  ┌─▼──────────────┐
│   RETRIEVER  │  │  ONTOLOGIE   │  │  PROMPT ENG.   │
│  (RAG Core)  │  │   (SPARQL)   │  │ (Templating)   │
└───────┬──────┘  └────┬─────────┘  └─────────────────┘
        │              │
        │   ┌──────────┘
        │   │
┌───────▼───▼────────────────────────────────────────┐
│           CHROMADB (Vector Database)               │
│  ┌──────────────────────────────────────────────┐  │
│  │ Collection: maritime_docs (~1200 chunks)     │  │
│  │ Embeddings: 384 dimensions (Sentence-Trans)  │  │
│  │ Similarity: Cosine distance                  │  │
│  │ Persistence: /output/chroma_db/              │  │
│  └──────────────────────────────────────────────┘  │
└─────────────┬──────────────────────────────────────┘
              │
              │ (Indexation offline)
              │
┌─────────────▼──────────────────────────────────────┐
│        CORPUS DOCUMENTS (58 PDFs, 159 MB)          │
│  ┌──────────────┐ ┌───────────────┐ ┌────────────┐ │
│  │   Baleine    │ │ Oiseaux marins│ │   Rejet    │ │
│  │   (23 PDFs)  │ │   (14 PDFs)   │ │ Hydroc. 21 │ │
│  └──────────────┘ └───────────────┘ └────────────┘ │
│                                                      │
│  Sources: Pays africains + Résolutions OMI          │
│  Format: PDFs (bruts) → Texte extraction            │
│  Langues: Français, Anglais                         │
└──────────────────────────────────────────────────────┘
```

---

## 🔄 PIPELINE DÉTAILLÉ

### PHASE 1: PREPROCESSING PDF

```
[PDF File]
    ↓
┌─────────────────────────────────────┐
│  pdfplumber.open()                  │
│  - Extraction texte par page        │
│  - Gestion multilingue              │
│  - Handling des tables/images       │
└─────────────────────────────────────┘
    ↓
[Texte brut par page]
    ↓
┌─────────────────────────────────────┐
│  Nettoyage & Normalisation          │
│  - Regex: espaces excédentaires     │
│  - Supprimer numéros de page        │
│  - Normaliser caractères spéciaux   │
└─────────────────────────────────────┘
    ↓
[Texte propre]
    ↓
┌─────────────────────────────────────┐
│  Chunking Intelligent               │
│  - Split par phrases (.) (!) (?)    │
│  - Taille: ~800 tokens (~3000 char) │
│  - Chevauchement: 10% (100 tokens)  │
│  - Min: 50 caractères par chunk     │
└─────────────────────────────────────┘
    ↓
[Chunks structurés]
    ↓
┌─────────────────────────────────────┐
│  Structuration JSON                 │
│  {                                  │
│    "id": "Ben162059_001",           │
│    "text": "...",                   │
│    "source": "Ben162059.pdf",       │
│    "category": "Baleine",           │
│    "country": "Bénin",              │
│    "page": 1,                       │
│    "word_count": 156                │
│  }                                  │
└─────────────────────────────────────┘
    ↓
[output/chunks.json] (~30 MB, ~1200 chunks)
```

**Statistiques attendues:**
- Baleine: ~500 chunks, 100K+ mots
- Oiseaux marins: ~300 chunks, 60K+ mots
- Rejet hydrocarbure: ~400 chunks, 80K+ mots

---

### PHASE 2: EMBEDDING & INDEXATION

```
[chunks.json]
    ↓
┌─────────────────────────────────────────────────────┐
│  Initialiser Sentence-Transformers                  │
│  Model: all-MiniLM-L6-v2                            │
│  - Multilingue (FR, EN, autres)                     │
│  - 384 dimensions                                   │
│  - 22M paramètres (léger)                           │
│  - Compatible CPU & CUDA                            │
└─────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────┐
│  Encoder chunks en batch (32 chunks/batch)          │
│  - Chaque chunk → 384-dim vector                    │
│  - Normalisation L2                                 │
│  - Optim: quantization int8 possible                │
└─────────────────────────────────────────────────────┘
    ↓
[1200 vectors de 384 dimensions]
    ↓
┌─────────────────────────────────────────────────────┐
│  ChromaDB Indexation                                │
│  - Crear collection: maritime_docs                  │
│  - HNSoft (Hierarchical Navigable Small World)      │
│  - Distance: Cosine similarity                      │
│  - Persist: /output/chroma_db/                      │
└─────────────────────────────────────────────────────┘
    ↓
[Persistent Index] (~200 MB)
```

**Format ChromaDB:**
```
chroma_db/
├── data.parquet          # Embeddings
├── metadata.parquet      # Métadonnées
├── index.parquet         # Index HNSW
└── requirements.txt      # Versions
```

---

### PHASE 3: RECHERCHE & RETRIEVAL

```
[User Query]
    ↓
┌──────────────────────────────┐
│  "Quels pays protègent      │
│   les baleines?"             │
└──────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────┐
│  Query Embedding (Sentence-Transformers)           │
│  - Même modèle qu'indexation                       │
│  - Résultat: 1 vector 384-dim                      │
└─────────────────────────────────────────────────────┘
    ↓
[Query Vector (384 dim)]
    ↓
┌─────────────────────────────────────────────────────┐
│  ChromaDB Search (cosine similarity)                │
│  - Top-K retrieval (défaut: 5 docs)                │
│  - Distance: 0-2 (0=identical, 2=opposite)         │
│  - Filter optionnel: categorie, pays, etc.         │
└─────────────────────────────────────────────────────┘
    ↓
[Top-K Documents ({id, text, distance, metadata})]
    ↓
┌─────────────────────────────────────────────────────┐
│  Rank & Format                                      │
│  - Sort by similarity score                        │
│  - Récupérer métadonnées (source, page, pays)      │
│  - Formater pour présentation                      │
└─────────────────────────────────────────────────────┘
    ↓
[Résultats classés]
```

**Exemple résultat:**
```json
{
  "id": "Ben162059_045",
  "distance": 0.15,
  "similarity": 0.85,
  "text": "La protection des baleines...",
  "metadata": {
    "source": "Ben162059.pdf",
    "category": "Baleine",
    "country": "Bénin",
    "page": "42"
  }
}
```

---

### PHASE 4: INTÉGRATION ONTOLOGIE (optionnel)

```
[Query + Retrieved Docs]
    ↓
┌────────────────────────────────────┐
│  OntologyIntegration               │
│  - Charger maritime_ontology.owl   │
│  - Parser RDF/OWL avec rdflib     │
└────────────────────────────────────┘
    ↓
┌────────────────────────────────────┐
│  Extraction Entités                │
│  - Keywords: "baleines"            │
│  - Type: Protection, Espèce        │
│  - Relations: Pays × Obligations   │
└────────────────────────────────────┘
    ↓
┌────────────────────────────────────┐
│  SPARQL Queries (future)           │
│  SELECT ?pays ?obligation          │
│  WHERE {                           │
│    ?pays protege ?baleine .        │
│    ?baleine rdftype:Cetace .       │
│    ?pays a:Obligation ?obligation. │
│  }                                 │
└────────────────────────────────────┘
    ↓
[Contexte enrichi ontologie]
    ↓
┌────────────────────────────────────┐
│  Fusion RAG + Ontologie            │
│  {                                 │
│    "query": "...",                 │
│    "rag_documents": [...],         │
│    "ontology_context": {...},      │
│    "combined_insights": [...]      │
│  }                                 │
└────────────────────────────────────┘
    ↓
[Réponse enrichie]
```

---

### PHASE 5: GÉNÉRATION LLM (TODO)

```
[Contexte RAG + Ontologie]
    ↓
┌─────────────────────────────────────────────────────┐
│  Prompt Engineering Template                        │
│                                                     │
│  Tu es un expert en droit maritime.                │
│                                                     │
│  CONTEXTE ONTOLOGIE:                               │
│  {ontology_concepts}                               │
│                                                     │
│  DOCUMENTS PERTINENTS:                             │
│  {retrieved_documents}                             │
│                                                     │
│  QUESTION: {user_query}                            │
│                                                     │
│  Réponds en français. Cite les sources.            │
└─────────────────────────────────────────────────────┘
    ↓
[Prompt + Context]
    ↓
┌─────────────────────────────────────────────────────┐
│  LLM Inference                                      │
│  Option A: Ollama (local, privacy)                 │
│    - Model: mistral, llama2                        │
│    - Température: 0.3 (déterministe)               │
│                                                     │
│  Option B: OpenAI (cloud, haute qualité)           │
│    - Model: gpt-4, gpt-3.5-turbo                   │
│    - Température: 0.1 (très structuré)             │
└─────────────────────────────────────────────────────┘
    ↓
[Generated Response]
```

---

## 📊 MODÈLES & CONFIGURATIONS

### Sentence-Transformers
```python
{
    "model_name": "sentence-transformers/all-MiniLM-L6-v2",
    "embedding_dimension": 384,
    "languages": ["en", "fr", "de", "es", ...],
    "parameters": "22M",
    "speed": "~1000 texts/sec (CPU)",
    "task": "Semantic search, clustering",
}
```

### ChromaDB
```python
{
    "database": "DuckDB + Parquet",
    "distance_metric": "cosine",
    "hnsw_space": "cosine",
    "default_ef_construction": 200,
    "default_ef_search": 10,
    "persistence": "On disk (Parquet)",
}
```

### RDFLib (Ontologie)
```python
{
    "format": "RDF/XML (OWL)",
    "reasoning": "Non (basic RDF)",
    "query_language": "SPARQL",
    "triple_store": "In-memory (lent > 100M triplets)",
}
```

---

## 🔐 SÉCURITÉ & CONFIDENTIALITÉ

### Données sensibles
- **PDFs publics** (documents gouvernementaux, résolutions OMI)
- **Pas de données personnelles** dans le corpus
- **Droit d'auteur** respecté (documents publics)

### Mesures
1. **Index local**: Toutes les données restent sur disque local
2. **Pas de log utilisateur**: Les requêtes ne sont pas enregistrées (sauf logs système)
3. **HTTPS optionnel**: Pour API REST en production
4. **Access control**: À implémenter pour multi-users

---

## ⚡ OPTIMISATIONS POSSIBLES

### 1. Quantization
```python
# Réduire taille embeddings: 384 → 128 dimensions
from sentence_transformers import util
compressed = util.semantic_search(query_emb, document_emb)
```

### 2. Cache
```python
# Cacher embeddings de requêtes fréquentes
import redis
cache = redis.Redis()
```

### 3. Hybrid Search
```python
# Combiner recherche vectorielle + keyword
# ChromaDB + ElasticSearch/BM25
```

### 4. Reranking
```python
# Top-100 vectoriel → Top-5 avec Cross-Encoder
from sentence_transformers import CrossEncoder
cross_encoder = CrossEncoder('cross-encoder/mmarco-mMiniLMv2-L12-H384-v1')
```

---

## 📈 MÉTRIQUES & MONITORING

```
Requête → Embedding → Search → Retrieval → LLM → Réponse

Metriques:
✓ Query latency: < 500ms
✓ Embedding quality: Cosine similarity
✓ Retrieval precision: % docs pertinents
✓ LLM latency: < 5sec (local) / 2sec (API)
✓ Total time: < 10 secondes
```

---

## 🔗 INTÉGRATIONS FUTURES

1. **Neo4j Graph DB** - Pour graphe de connaissances
2. **LangChain Agents** - Agents autonomes
3. **Fine-tuned Models** - Modèles spécialisés droit maritime
4. **Knowledge Graph** - Relation extraction
5. **Web Scraping** - Mise à jour automatique documents

---

**Diagramme révisé:** Avril 2026
**Architecture v0.1.0**

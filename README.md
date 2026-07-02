# 🌊 Neuro-Symbolic RAG — Droit International de la Mer

> **Projet de Fin d'Études (PFE)**  
> Système neuro-symbolique combinant une ontologie juridique maritime (OWL/LKIF-Core) et un RAG hybride (Dense + Sparse + Graph) pour l'interrogation intelligente de textes juridiques maritimes francophones.

---

## 📋 Table des Matières

1. [Aperçu du Projet](#-aperçu-du-projet)
2. [Architecture](#-architecture)
3. [Structure du Dépôt](#-structure-du-dépôt)
4. [Prérequis](#-prérequis)
5. [Installation Pas-à-Pas](#-installation-pas-à-pas)
6. [Obtenir les Données (PDFs)](#-obtenir-les-données-pdfs)
7. [Lancement — Pipeline Ontologie](#-lancement--pipeline-ontologie)
8. [Lancement — Pipeline RAG](#-lancement--pipeline-rag)
9. [Interface Web (Streamlit)](#-interface-web-streamlit)
10. [Évaluation et Benchmarks](#-évaluation-et-benchmarks)
11. [Configuration](#-configuration)
12. [Tests](#-tests)
13. [Troubleshooting](#-troubleshooting)
14. [Références Scientifiques](#-références-scientifiques)

---

## 🎯 Aperçu du Projet

Ce projet traite **6 interdictions maritimes** du droit international :

| Code | Interdiction |
|------|-------------|
| I001 | Chalutage de fond |
| I002 | Chasse à la baleine |
| I003 | Extraction de sable |
| I004 | Chasse des oiseaux marins |
| I005 | Construction sur le littoral |
| I006 | Rejet d'hydrocarbures |

### Deux pipelines complémentaires :

1. **Pipeline Ontologie** : Construction automatique d'une ontologie OWL/RDF alignée sur LKIF-Core à partir de triplets extraits par LLM, avec export Neo4j et questions de compétence SPARQL.

2. **Pipeline RAG Hybride** : Système de Question-Answering combinant :
   - 🔵 **Dense Retriever** — ChromaDB + embeddings BGE-M3 (1024 dims, multilingue)
   - 🟡 **Sparse Retriever** — BM25 avec expansion de requêtes
   - 🟢 **Graph Retriever** — Neo4j + Cypher (traversée de l'ontologie)
   - 🔴 **Fusion RRF** — Reciprocal Rank Fusion avec boost sémantique via synonymes ontologiques
   - 🤖 **LLM** — Ollama (Mistral/Llama3.2) pour la génération de réponses

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    PIPELINE ONTOLOGIE                             │
│                                                                  │
│  Textes Juridiques (PDFs)                                        │
│       │                                                          │
│       ▼ Extraction LLM (Ministral/Qwen/Gemma)                   │
│  Triplets JSON (sujet, prédicat, objet)                          │
│       │                                                          │
│       ▼ ontologie/pipeline.py                                    │
│  ┌─────────┐   ┌───────────┐   ┌──────────────┐                 │
│  │ schema  │──▶│ populator │──▶│ neo4j_export │                  │
│  │  .py    │   │   .py     │   │     .py      │                  │
│  └─────────┘   └───────────┘   └──────────────┘                 │
│       │              │               │                           │
│       ▼              ▼               ▼                           │
│  OWL/TTL/JSON-LD   RDF Graph    Neo4j + Cypher                   │
│                      │                                           │
│                      ▼                                           │
│              SPARQL (10 CQs)                                     │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    PIPELINE RAG HYBRIDE                           │
│                                                                  │
│  PDFs Juridiques (6 catégories × N pays)                         │
│       │                                                          │
│       ▼ rag/ingestion/pdf_extractor.py                           │
│  Chunks (800 tokens, overlap 100)                                │
│       │                                                          │
│       ├──▶ ChromaDB (Dense, BGE-M3)                              │
│       └──▶ BM25 Index (Sparse)                                   │
│                                                                  │
│  Requête Utilisateur                                             │
│       │                                                          │
│       ▼ rag/core/query_analyzer.py                               │
│  Intention + Poids + Filtres (pays, catégorie)                   │
│       │                                                          │
│       ├──▶ Dense Retriever ──┐                                   │
│       ├──▶ Sparse Retriever ─┤──▶ Fusion RRF ──▶ LLM ──▶ Réponse│
│       └──▶ Graph Retriever ──┘    (+ boost synonymes Neo4j)      │
│                                                                  │
│  Interface: Streamlit (rag/api/app_streamlit.py)                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 Structure du Dépôt

```
neurosymbolic-rag-maritime/
│
├── README.md                          # ← Ce fichier (guide complet)
├── .gitignore
├── Rapport_De_PFE.pdf                 # Rapport de PFE complet
├── Rapport_De_PFE.docx
├── *.xlsx                             # Grilles d'évaluation manuelles
│
├── phase1/                            # Données brutes de la Phase 1
│   ├── extraction-entité-triplet/     # Triplets extraits par modèle LLM
│   ├── extraction_definitions/        # Définitions extraites par modèle
│   ├── Synonyme et hyperonymes/       # Synonymes/hyperonymes par interdiction
│   └── *.xlsx                         # Grilles d'évaluation
│
└── neurosymbolic_rag/                 # ★ CODE SOURCE PRINCIPAL ★
    ├── README.md                      # Documentation technique
    ├── main.py                        # Point d'entrée CLI unifié
    ├── requirements.txt               # Dépendances Python
    ├── pyproject.toml                 # Packaging Python
    ├── docker-compose.yml             # Neo4j containerisé
    ├── .env.local.example             # Template de configuration secrète
    │
    ├── ontologie/                     # Module ontologie (OWL/RDF)
    │   ├── schema.py                  # Classes OWL, propriétés, alignement LKIF
    │   ├── populator.py               # Population des individus
    │   ├── pipeline.py                # Orchestrateur ontologie
    │   ├── loader.py                  # Chargement des données JSON
    │   ├── neo4j_export.py            # Export graphe vers Neo4j
    │   ├── sparql_runner.py           # Questions de compétence SPARQL
    │   ├── corrections.py             # Corrections post-population
    │   ├── entity_resolution.py       # Résolution d'entités
    │   └── triple_injector.py         # Injection de triplets
    │
    ├── rag/                           # Module RAG hybride
    │   ├── config.py                  # Configuration centralisée
    │   ├── run_pipeline.py            # Orchestrateur RAG (3 phases)
    │   ├── llm_generator.py           # Génération LLM (Ollama)
    │   ├── check_environment.py       # Diagnostic environnement
    │   ├── core/                      # Moteur de recherche
    │   │   ├── retrievers.py          # Dense (ChromaDB) + Sparse (BM25)
    │   │   ├── fusion.py              # Fusion RRF + boost sémantique
    │   │   ├── query_analyzer.py      # Analyse d'intention
    │   │   └── neo4j_graph_retriever.py
    │   ├── ingestion/                 # Extraction et indexation
    │   │   ├── pdf_extractor.py       # Extraction PDF (PyMuPDF)
    │   │   └── embeddings_pipeline.py # Indexation BGE-M3 + BM25
    │   ├── integration/               # Pont ontologie ↔ RAG
    │   │   ├── neo4j_bridge.py        # Bridge Neo4j complet
    │   │   └── neo4j_bridge_safe.py   # Bridge Neo4j sécurisé
    │   └── api/
    │       └── app_streamlit.py       # Interface web Streamlit
    │
    ├── data/                          # Données structurées
    │   ├── config/settings.yaml       # Configuration ontologie
    │   ├── input/lkif_stub.ttl        # Stub LKIF-Core (alignement)
    │   ├── queries/competency_questions.sparql
    │   ├── raw/                       # Données brutes (triplets JSON)
    │   └── output/                    # Ontologie générée (TTL/OWL/JSON-LD)
    │
    ├── tests/                         # Tests automatisés
    │   ├── test_ontology.py
    │   ├── test_rag_unit.py
    │   ├── test_rag_integration.py
    │   └── test_rag_robustness.py
    │
    ├── scripts/                       # Scripts utilitaires
    ├── benchmark_queries.py           # Requêtes de benchmark
    ├── run_benchmark.py               # Exécution des benchmarks
    ├── test_ablation.py               # Étude d'ablation
    └── test_ablation_article.py       # Ablation pour l'article
```

---

## 📌 Prérequis

| Logiciel | Version | Obligatoire | Usage |
|----------|---------|:-----------:|-------|
| **Python** | ≥ 3.9 | ✅ | Langage principal |
| **pip** | ≥ 21.0 | ✅ | Gestionnaire de paquets |
| **Git** | ≥ 2.30 | ✅ | Versionning |
| **Ollama** | ≥ 0.1 | ✅ (pour RAG) | LLM local (Mistral/Llama) |
| **Docker** | ≥ 20.0 | ⚠️ Optionnel | Neo4j containerisé |
| **Neo4j** | ≥ 5.0 | ⚠️ Optionnel | Graph Retriever + Export ontologie |

---

## 🚀 Installation Pas-à-Pas

### Étape 1 : Cloner le dépôt

```bash
git clone https://github.com/Assoumana-Souley-Hadiza/neurosymbolic-rag-maritime.git
cd neurosymbolic-rag-maritime
```

### Étape 2 : Créer l'environnement virtuel

```bash
cd neurosymbolic_rag

# Créer l'environnement
python -m venv .venv

# Activer l'environnement
# Windows (PowerShell) :
.venv\Scripts\Activate.ps1

# Windows (CMD) :
.venv\Scripts\activate.bat

# Linux / macOS :
source .venv/bin/activate
```

### Étape 3 : Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Étape 4 : Configurer les secrets

```bash
# Copier le template
cp .env.local.example .env.local

# Éditer avec vos valeurs réelles
# (mot de passe Neo4j, URL Ollama, modèle LLM, etc.)
```

Contenu à personnaliser dans `.env.local` :
```env
NEO4J_PASSWORD=votre_mot_de_passe
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
LLM_TEMPERATURE=0.1
```

### Étape 5 : Installer Ollama et les modèles

```bash
# Installer Ollama : https://ollama.com/download

# Télécharger les modèles nécessaires
ollama pull mistral           # Modèle principal (génération)
ollama pull llama3.2:3b       # Alternative plus légère

# Vérifier qu'Ollama tourne
ollama list
```

### Étape 6 (optionnel) : Lancer Neo4j

```bash
# Via Docker (recommandé)
docker-compose up -d

# Vérifier : http://localhost:7474
# Login : neo4j / <votre_mot_de_passe>
```

### Étape 7 : Vérifier l'installation

```bash
python main.py rag --check
```

---

## 📂 Obtenir les Données (PDFs)

Les PDFs juridiques sont des **textes officiels publics** trop volumineux pour GitHub. Ils doivent être placés manuellement dans les sous-dossiers de `rag/RAG_data/`.

### Structure attendue

```
rag/RAG_data/
├── Baleine/           # Lois sur la chasse à la baleine
│   ├── alg46008.pdf   # Algérie
│   ├── sen155049.pdf  # Sénégal
│   └── ...
├── Chalutage de fond/ # Lois sur le chalutage
├── Construction/      # Lois sur la construction littorale
├── Oiseaux marins/    # Lois sur la chasse aux oiseaux
├── Rejet hydrocarbure/# Lois sur les rejets en mer
└── Sable/             # Lois sur l'extraction de sable
```

> **Source des PDFs** : Les textes sont issus de la base [FAOLEX](https://www.fao.org/faolex/) (FAO) et de législations nationales africaines francophones. Consultez le rapport de PFE (`Rapport_De_PFE.pdf`) pour la liste complète des sources et références.

### Si vous n'avez pas les PDFs

Le système peut fonctionner en mode **ontologie seule** (sans RAG) :
```bash
python main.py ontology    # Ne nécessite pas de PDFs
```

---

## ⚙️ Lancement — Pipeline Ontologie

### Pipeline complet

```bash
python main.py ontology
```

Cela génère dans `data/output/` :
- `maritime_ontology.ttl` — Format Turtle
- `maritime_ontology.owl` — Format OWL/RDF-XML
- `maritime_ontology.jsonld` — Format JSON-LD
- `neo4j_import.cypher` — Script d'import Neo4j
- `sparql_results.json` — Résultats des 10 questions de compétence

### Options

```bash
python main.py ontology --sparql-only    # Questions SPARQL uniquement
python main.py ontology --neo4j-only     # Export Neo4j uniquement
python main.py ontology --validate       # Validation OWL-RL
python main.py ontology --no-neo4j       # Sans Neo4j
```

---

## 🔍 Lancement — Pipeline RAG

### Pipeline complet (3 phases)

```bash
python main.py rag
```

| Phase | Description |
|-------|-------------|
| **Phase 1** | Extraction PDF → découpe en chunks (800 tokens, overlap 100) |
| **Phase 2** | Indexation Dense (ChromaDB + BGE-M3) + Sparse (BM25) |
| **Phase 3** | Vérification avec 4 requêtes de test |

### Options

```bash
python main.py rag -- --skip-extraction   # Sauter la Phase 1
python main.py rag -- --skip-indexing     # Sauter la Phase 2
```

---

## 💻 Interface Web (Streamlit)

```bash
streamlit run rag/api/app_streamlit.py
```

L'interface s'ouvre à `http://localhost:8501` et permet :
- Poser des questions en langage naturel (français)
- Visualiser les sources et scores de pertinence
- Voir la décomposition Dense / Sparse / Graph
- Filtrer par pays et catégorie d'interdiction

---

## 📊 Évaluation et Benchmarks

```bash
# Étude d'ablation (Dense seul, Sparse seul, Hybride, Hybride+Graph)
python test_ablation.py

# Version article LATELL2026
python test_ablation_article.py

# Benchmark de requêtes
python run_benchmark.py
```

---

## 🔧 Configuration

### Ontologie — `data/config/settings.yaml`

```yaml
metadata:
  title: "Ontologie Maritime — Droit International de la Mer"
  version: "1.0.0"

namespaces:
  mar:  "http://www.maritime-ontology.org/mar#"
  lkif: "http://www.estrellaproject.org/lkif-core/lkif-core.owl#"

output:
  dir: "data/output"
  formats: [turtle, xml, json-ld]
```

### RAG — Variables d'environnement (`.env.local`)

| Variable | Défaut | Description |
|----------|--------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL d'Ollama |
| `OLLAMA_MODEL` | `mistral` | Modèle LLM |
| `LLM_TEMPERATURE` | `0.1` | Température (0 = déterministe) |
| `NEO4J_PASSWORD` | — | Mot de passe Neo4j (**obligatoire**) |
| `NEO4J_URI` | `bolt://localhost:7687` | URI Neo4j |
| `EMBEDDING_VERSION` | `bge-m3-v1` | Version des embeddings |
| `LOG_LEVEL` | `INFO` | Niveau de log |

---

## 🧪 Tests

```bash
pytest tests/ -v                              # Tous les tests
pytest tests/ -v -m unit                      # Tests unitaires
pytest tests/ -v -m integration               # Tests d'intégration (Neo4j + Ollama)
pytest tests/ --cov=ontologie --cov=rag       # Avec couverture
```

---

## 🐛 Troubleshooting

| Erreur | Solution |
|--------|----------|
| `NEO4J_PASSWORD manquante` | Copier `.env.local.example` → `.env.local` et remplir |
| `Module not found: ontologie` | Être dans `neurosymbolic_rag/` et `set PYTHONPATH=.;%PYTHONPATH%` |
| `Neo4j Connection refused` | `docker-compose up -d` puis vérifier `http://localhost:7474` |
| `Ollama Connection refused` | Lancer `ollama serve` puis `ollama list` |
| `No PDF files found` | Placer les PDFs dans `rag/RAG_data/<catégorie>/` |
| Premier lancement lent | Normal : téléchargement du modèle BGE-M3 (~1.2 Go) |

---

## 📚 Références Scientifiques

- **LKIF-Core** — Hoekstra et al., "The LKIF Core Ontology of Basic Legal Concepts" (2007)
- **RAG** — Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (2020)
- **BGE-M3** — Chen et al., "BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity" (2024)
- **BM25** — Robertson & Zaragoza, "The Probabilistic Relevance Framework: BM25 and Beyond" (2009)
- **RRF** — Cormack et al., "Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods" (2009)

---

## 📝 Licence

Projet académique — Licence à spécifier.

---

**Dernière mise à jour :** Juillet 2026

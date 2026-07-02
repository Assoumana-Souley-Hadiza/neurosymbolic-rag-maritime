# 🌊 Ontologie Maritime & RAG Hybride — Droit International de la Mer

> **Projet de Fin d'Études (PFE)**  
> Construction d'une ontologie juridique maritime alignée sur LKIF-Core et d'un système RAG hybride (Dense + Sparse + Graph) pour l'interrogation intelligente de textes juridiques maritimes francophones.

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
14. [Arborescence Complète](#-arborescence-complète)
15. [Références Scientifiques](#-références-scientifiques)

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
stage_RAG/
│
├── README.md                          # ← Ce fichier (guide complet)
├── .gitignore
├── Rapport_De_PFE.pdf                 # Rapport de PFE complet
├── Rapport_De_PFE.docx
│
├── articles_et_présentations/         # Articles de référence et données d'évaluation
│   ├── article1.pdf ... article_ontologie3.pdf
│   ├── chasse_a_la_baleine.xlsx       # Grille d'évaluation manuelle
│   └── rejet_dhydrocarbures.xlsx
│
├── fichiers/                          # Notebooks Kaggle d'extraction (Phase 1)
│   ├── Notebook 1 — Ministral-8B-Instruct-2410.ipynb
│   ├── Notebook 2 — Qwen3-8B.ipynb
│   ├── Notebook 3 — gemma-4-E4B-it.ipynb
│   └── *.json                         # Résultats d'extraction bruts
│
├── phase1/                            # Données brutes de la Phase 1
│   ├── extraction-entité-triplet/     # Triplets extraits par modèle
│   ├── extraction_definitions/        # Définitions extraites par modèle
│   ├── Synonyme et hyperonymes/       # Synonymes/hyperonymes par interdiction
│   └── *.xlsx                         # Grilles d'évaluation
│
└── version_1_Ontologie/               # ★ CODE SOURCE PRINCIPAL ★
    ├── README.md                      # Documentation technique détaillée
    ├── main.py                        # Point d'entrée CLI unifié
    ├── requirements.txt               # Dépendances Python
    ├── pyproject.toml                 # Packaging Python (pip install -e .)
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
    │   ├── triple_injector.py         # Injection de triplets
    │   ├── ontology_cleaner.py        # Nettoyage ontologie
    │   ├── refactor_ontology.py       # Refactoring structurel
    │   └── visualize_ontology.py      # Visualisation du graphe
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
    │   │   └── neo4j_graph_retriever.py  # Retriever graphe Neo4j
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
    │   ├── config/
    │   │   └── settings.yaml          # Configuration ontologie
    │   ├── input/
    │   │   └── lkif_stub.ttl          # Stub LKIF-Core (alignement)
    │   ├── queries/
    │   │   └── competency_questions.sparql  # 10 questions de compétence
    │   ├── raw/                       # Données brutes (triplets JSON)
    │   │   ├── extraction_merged/     # Triplets fusionnés par interdiction
    │   │   ├── definitions_retenues_propres/  # Définitions validées
    │   │   └── Synonyme et hyperonymes/       # Lexique
    │   └── output/                    # Fichiers générés (ontologie)
    │
    ├── tests/                         # Tests automatisés
    │   ├── test_ontology.py
    │   ├── test_rag_unit.py
    │   ├── test_rag_integration.py
    │   └── test_rag_robustness.py
    │
    ├── scripts/                       # Scripts utilitaires
    ├── docs/                          # Documentation étendue
    │   ├── ARCHITECTURE.md
    │   ├── INSTALLATION.md
    │   ├── QUICK_START.md
    │   └── ...
    │
    ├── benchmark_queries.py           # Requêtes de benchmark
    ├── batch_query_system.py          # Système de requêtes batch
    ├── test_ablation.py               # Étude d'ablation
    ├── test_ablation_article.py       # Ablation pour l'article
    └── run_benchmark.py              # Exécution des benchmarks
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
cd version_1_Ontologie

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
# Login : neo4j / maritime2024 (ou votre mot de passe .env.local)
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

Pour le RAG, l'extraction et l'indexation seront vides mais le code fonctionnera sans erreur.

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
# Questions SPARQL uniquement
python main.py ontology --sparql-only

# Export Neo4j uniquement
python main.py ontology --neo4j-only

# Validation OWL-RL
python main.py ontology --validate

# Sans Neo4j
python main.py ontology --no-neo4j
```

---

## 🔍 Lancement — Pipeline RAG

### Pipeline complet (3 phases)

```bash
python main.py rag
```

**Phase 1 — Extraction PDF** : Lit tous les PDFs de `rag/RAG_data/`, les découpe en chunks (800 tokens, overlap 100).

**Phase 2 — Indexation Hybride** : Crée les index Dense (ChromaDB + BGE-M3) et Sparse (BM25).

**Phase 3 — Vérification** : Exécute 4 requêtes de test pour valider le système.

### Options

```bash
# Sauter l'extraction PDF (si déjà fait)
python main.py rag -- --skip-extraction

# Sauter l'indexation (si déjà fait)
python main.py rag -- --skip-indexing
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

### Étude d'ablation

```bash
# Ablation complète (Dense seul, Sparse seul, Hybride, Hybride+Graph)
python test_ablation.py

# Version article LATELL2026
python test_ablation_article.py
```

### Benchmark de requêtes

```bash
python run_benchmark.py
```

### Requêtes batch

```bash
python batch_query_system.py
```

Les résultats sont sauvegardés dans `results/`.

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

neo4j:
  uri: "bolt://localhost:7687"
  user: "neo4j"
  password: "maritime2024"    # ⚠️ Changer en production
```

### RAG — `rag/config.py`

Les paramètres clés sont configurables via `.env.local` :

| Variable | Défaut | Description |
|----------|--------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL d'Ollama |
| `OLLAMA_MODEL` | `mistral` | Modèle LLM |
| `LLM_TEMPERATURE` | `0.1` | Température (0 = déterministe) |
| `NEO4J_PASSWORD` | — | Mot de passe Neo4j (obligatoire) |
| `NEO4J_URI` | `bolt://localhost:7687` | URI Neo4j |
| `EMBEDDING_VERSION` | `bge-m3-v1` | Version des embeddings |
| `LOG_LEVEL` | `INFO` | Niveau de log |

---

## 🧪 Tests

```bash
# Tous les tests
pytest tests/ -v

# Tests unitaires uniquement
pytest tests/ -v -m unit

# Tests d'intégration (nécessite Neo4j + Ollama)
pytest tests/ -v -m integration

# Avec couverture
pytest tests/ --cov=ontologie --cov=rag
```

---

## 🐛 Troubleshooting

### ❌ `NEO4J_PASSWORD manquante dans .env.local`
```bash
cp .env.local.example .env.local
# Éditez .env.local avec votre mot de passe Neo4j
```

### ❌ `Module not found: ontologie` ou `rag`
```bash
# Assurez-vous d'être dans version_1_Ontologie/
cd version_1_Ontologie

# Windows :
set PYTHONPATH=.;%PYTHONPATH%

# Linux/macOS :
export PYTHONPATH=.:$PYTHONPATH
```

### ❌ Neo4j `Connection refused`
```bash
docker-compose up -d
docker-compose ps    # Vérifier que le conteneur tourne
# Browser : http://localhost:7474
```

### ❌ Ollama `Connection refused`
```bash
ollama serve         # Lancer le serveur
ollama list          # Vérifier les modèles installés
```

### ❌ `No PDF files found` (RAG)
Vérifiez que les PDFs sont dans `rag/RAG_data/<catégorie>/`. Voir la section [Obtenir les Données](#-obtenir-les-données-pdfs).

### ⚠️ Premier lancement très lent
Le premier lancement télécharge le modèle d'embedding BGE-M3 (~1.2 Go). Les lancements suivants sont instantanés.

---

## 📐 Arborescence Complète

<details>
<summary>Cliquez pour voir l'arborescence détaillée</summary>

```
stage_RAG/
├── .gitignore
├── README.md
├── Rapport_De_PFE.pdf
├── Rapport_De_PFE.docx
├── Listes_synonymes_hyperonymes.docx
├── plan_Rapport.docx
├── ontologie_comparaison.html
├── chasse_a_la_baleine.xlsx
├── rejet_dhydrocarbures.xlsx
├── rejet_hydrocarbure_bertscore.xlsx
├── ablation_chasse_a_la_baleine_run1.xlsx
│
├── articles_et_présentations/
│   ├── article1.pdf
│   ├── article2.pdf
│   ├── article_ontologie.pdf
│   ├── article_ontologie2.pdf
│   ├── article_ontologie3.pdf
│   ├── chasse_a_la_baleine.xlsx
│   └── rejet_dhydrocarbures.xlsx
│
├── fichiers/
│   ├── Notebook 1 — Ministral-8B-Instruct-2410.ipynb
│   ├── Notebook 2 — Qwen3-8B.ipynb
│   ├── Notebook 3 — gemma-4-E4B-it.ipynb
│   └── *.json (résultats d'extraction)
│
├── phase1/
│   ├── extraction-entité-triplet/
│   ├── extraction_definitions/
│   ├── Synonyme et hyperonymes/
│   └── *.xlsx (grilles d'évaluation)
│
└── version_1_Ontologie/
    ├── main.py
    ├── requirements.txt
    ├── pyproject.toml
    ├── docker-compose.yml
    ├── .env.local.example
    ├── .gitignore
    ├── README.md
    ├── ontologie/ (15 fichiers Python)
    ├── rag/ (18 fichiers Python)
    ├── data/ (config, input, queries, raw, output)
    ├── tests/ (5 fichiers)
    ├── scripts/ (4 fichiers)
    ├── docs/ (22 fichiers)
    ├── benchmark_queries.py
    ├── batch_query_system.py
    ├── test_ablation.py
    └── run_benchmark.py
```

</details>

---

## 📚 Références Scientifiques

- **LKIF-Core** — Hoekstra et al., "The LKIF Core Ontology of Basic Legal Concepts" (2007)
- **RAG** — Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (2020)
- **BGE-M3** — Chen et al., "BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity" (2024)
- **BM25** — Robertson & Zaragoza, "The Probabilistic Relevance Framework: BM25 and Beyond" (2009)
- **RRF** — Cormack et al., "Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods" (2009)

---

## 📝 Licence

Projet académique — 

---

**Dernière mise à jour :** Juillet 2026

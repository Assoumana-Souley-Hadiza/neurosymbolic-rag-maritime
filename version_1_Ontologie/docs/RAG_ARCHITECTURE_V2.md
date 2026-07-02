# 🏗️ ARCHITECTURE TECHNIQUE - RAG MARITIME HYBRIDE

## 📐 Vue d'ensemble

L'architecture v2 de ce projet utilise une approche novatrice appelée **Ontology-Augmented Hybrid RAG**. Au lieu d'utiliser un simple pipeline linéaire et uniquement sémantique, le système combine 3 méthodes de retrieval exécutées en parallèle et orientées par l'analyse automatique de l'intention de l'utilisateur.

```text
                    ┌─────────────────────┐
                    │    User Query       │
                    └─────────┬───────────┘
                              │
                    ┌─────────▼───────────┐
                    │   Query Analyzer    │
                    │ (Intent + Entities) │
                    └─────────┬───────────┘
                              │ Poids dynamiques
              ┌───────────────┼───────────────┐
              │               │               │
    ┌─────────▼────┐  ┌──────▼──────┐  ┌─────▼──────────┐
    │  Dense       │  │  Sparse     │  │  Graph         │
    │  Retriever   │  │  Retriever  │  │  Retriever     │
    │ (ChromaDB +  │  │ (BM25 +     │  │ (SPARQL sur    │
    │  bge-m3)     │  │  RegexFR)   │  │  Ontologie OWL)│
    └──────┬───────┘  └──────┬──────┘  └──────┬─────────┘
           │                 │                │
    ┌──────▼─────────────────▼────────────────▼──────┐
    │           Reciprocal Rank Fusion (RRF)         │
    │         + Ontology-Aware Score Boost           │
    └─────────────────────┬──────────────────────────┘
                          │ (Top K Résultats)
               ┌──────────▼──────────┐
               │   Context Builder   │
               │ (Chunks textuels +  │
               │  Contexte Graphe)   │
               └──────────┬──────────┘
                          │
               ┌──────────▼──────────┐
               │   LLM Generation    │
               │   (Ollama / OpenAI) │
               └─────────────────────┘
```

---

## 🔄 COMPOSANTS DU PIPELINE

### 🎯 1. Query Analyzer (`rag/core/query_analyzer.py`)

Ce module analyse la requête entrante via des patterns d'expressions régulières (RegEx) pour déterminer son intention principale :
- **Factuelle** (*"Quels sont", "Combien"*) → Privilégie le Graph Retriever (SPARQL)
- **Juridique** (*"Interdiction", "Loi", "Sanction"*) → Privilégie un équilibre entre BM25 et le Graphe (termes exacts).
- **Exploratoire** (*"Comment", "Pourquoi"* ) → Privilégie le Dense Retriever (compréhension sémantique).

### 🔍 2. Les 3 Voies de Retrieval (`rag/core/retrievers.py`)

#### A. Dense Retriever (La sémantique)
- **Outil** : ChromaDB + SentenceTransformers (`BAAI/bge-m3`)
- **Rôle** : Trouve les documents dont le sens est similaire à la question, même si les mots exacts ne sont pas employés (ex: "sauver" -> "protection").
- **Stockage** : Vecteurs de 1024 dimensions stockés localement.

#### B. Sparse Retriever (Le lexicale)
- **Outil** : BM25Okapi + Tokenizer Regex Français
- **Rôle** : Essentiel pour le domaine juridique où la recherche par mots-clés exacts (ex: *Résolution 61/105*) est indispensable. Supporte la typographie française (tirets, apostrophes).

#### C. Graph Retriever (Le structuré)
- **Outil** : RDFLib sur l'ontologie maritime (`maritime_ontology.owl`).
- **Rôle** : Détecte dynamiquement les entités (espèces, zones, activités) dans la question utilisateur, puis génère une requête SPARQL à la volée. 
- **Sortie** : Retourne des sous-graphes sous forme de texte synthétique (ex: *"Baleine protège par I002"*). C'est un **Knowledge Graph** injecté dans le contexte.

### 🧬 3. Fusion et Ranking (`rag/core/fusion.py`)

Les trois listes de résultats doivent être fusionnées de manière mathématique et intelligente :
- **RRF (Reciprocal Rank Fusion)** : Combine les rangs `(1 / (k + rank))` pondérés par les scores de l'intention détectée.
- **Ontology-Aware Boost** : *(Innovation)* Le système scanne le texte issu des PDF (Dense/Sparse) pour voir s'il mentionne les entités de l'ontologie présentes dans la boucle Graph. Si oui, le chunk PDF gagne un "bonus de confiance" !

### 📄 4. Ingestion Parallèle (`rag/ingestion/`)

La mise à jour de la base de documentation :
1. Extraction PDF multilingue, filtrage des en-têtes et numéros de page (`pdf_extractor.py`).
2. Chunking intelligent (respect des limites de phrases) avec un très bon recouvrement.
3. Distribution en parallèle dans ChromaDB (vectors) et Pickle (BM25 index) via `embeddings_pipeline.py`.

---

## 🛡️ 5. SÉCURITÉ, SOUVERAINETÉ ET ANTI-HALLUCINATION (Nouvelles Mises à Jour)

Afin d'assurer la viabilité légale des réponses générées, plusieurs verrous architecturaux ont été ajoutés :

#### A. Filtrage Géographique Strict (Souveraineté des données)
- **Logique** : Le `QueryAnalyzer` (via expressions régulières insensibles aux accents) capte formellement le pays (parmi les 16 disponibles, ex : Bénin, Côte d'Ivoire).
- **Verrou** : `HybridFusion` détruit mathématiquement la pertinence de **tous** les documents dont la métadonnée `country` ne correspond pas strictement, éliminant tout risque qu'une loi algérienne justifie une réponse sur le Maroc.

#### B. Prompting "Zero-Hallucination" & Citations In-Extenso
- L'agent "Générateur LLM" est désormais configuré pour traiter le contexte documentaire comme une **Source Unique de Vérité**.
- Toute information absente du texte des chunks résulte en un refus formel de répondre : *"NON. L'information n'est pas présente dans les documents."*
- Obligation de **Citation Verbatim** : L'IA doit recopier entre guillemets l'article exact trouvé dans les PDFs.

#### C. L'Ontologie Invisible (Silence des Lacunes)
- L'`OntologyAgent` continue d'enrichir le réseau en calculant secrètement les synonymes (ex: *Rorqual* = *Baleine*). 
- Cependant, les calculs agressifs de "Lacunes Documentaires" ont été masqués du prompt LLM. Ainsi, l'outil se concentre formellement sur ce qui *est* dans la loi, limitant les discours inférentiels sur les espèces non mentionnées. L'ontologie reste le cerveau sémantique invisible.

#### D. Traçabilité d'Audit (Logging)
- Implémentation d'un enregistreur JsonLines (`qa_history.jsonl`).
- Chaque appel via Streamlit enregistre : l'horodatage, la question, la longueur du contexte, le prompt système complet caché sous le capot, et la réponse du LLM, garantissant l'auditabilité absolue du RAG.

---

## 🛠️ STRUCTURE DU NOUVEAU PACKAGE `rag/`

```text
rag/
├── __init__.py
├── config.py                      # Configurations centralisées, poids RRF, chemins
├── core/                          # Le "cerveau" du RAG
│   ├── fusion.py                  # Module mathématique RRF
│   ├── query_analyzer.py          # Détection d'intentions
│   └── retrievers.py              # Classes Dense, Sparse, et GraphRetrievers
├── ingestion/                     # Création des index
│   ├── embeddings_pipeline.py     # Orchestrateur d'indexation hybride
│   └── pdf_extractor.py           # Parsing PDF robuste
├── integration/                   # Le pont avec RDF/OWL
│   └── ontology_bridge.py         # Charge le graph et extrait les labels pour le boost
├── api/                           
│   └── app_streamlit.py           # IHM
├── run_pipeline.py                # Point d'entrée script
└── check_environment.py           # Audit des dépendances
```

---

## 📈 AVANTAGES PAR RAPPORT A LA V1

1. **Suppression des angles morts structurés** : La v1 utilisait un Agent "Text-To-SPARQL" LLM lent et propice aux hallucinations. La v2 indexe les entités OWL en dur via le *Graph Retriever* puis pondère sémantiquement.
2. **SRP et Modularité** : Séparation totale de l'Ingestion (Offline) et du Retrieval (Online). Les imports sont *lazy* (les dépendances lourdes type Transformers/Chroma s'allument à la demande).
3. **Pondération Intelligente** : Un RAG statique est limité. Le `Query Analyzer` adapte le comportement de recherche (sparse vs dense) selon le type de formulation utilisateur.

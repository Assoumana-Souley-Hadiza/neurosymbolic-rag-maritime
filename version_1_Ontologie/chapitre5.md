# Chapitre 5 : Architecture RAG Neuro-Symbolique

Ce chapitre présente l'architecture complète du système de Retrieval-Augmented Generation (RAG) développé pour l'audit juridique maritime. Il décrit le pipeline de bout en bout, depuis l'ingestion des documents PDF jusqu'à la génération de réponses juridiquement fondées, en passant par le couplage neuro-symbolique entre recherche vectorielle et raisonnement sur graphe de connaissances.

## 5.1 Motivation de l'approche hybride

### 5.1.1 Limites du RAG vectoriel seul

Un système RAG purement vectoriel, fondé sur la similarité cosinus entre la question de l'utilisateur et les passages du corpus, présente trois défaillances critiques sur un corpus juridique maritime :

- **Le problème du vocabulaire contrôlé** : une question portant sur les « cétacés » ne retrouve pas les passages parlant de « baleines » ou de « rorquals », car les embeddings de ces termes spécialisés sont souvent éloignés dans l'espace vectoriel. La similarité sémantique des modèles généralistes échoue face à la terminologie juridique technique.

- **L'absence de raisonnement multi-sauts** : la question « Quelles sanctions s'appliquent à un navire pétrolier en Méditerranée ? » nécessite de traverser trois relations (Acteur → Interdiction → Zone → Sanction). Un retriever vectoriel ne peut que retrouver des passages contenant les mots de la question, sans naviguer dans la structure normative.

- **La confusion des juridictions** : le corpus contient des textes de 16 pays différents portant sur les mêmes thématiques. Un retriever vectoriel peut retourner un article sénégalais pour une question sur le Maroc, car le contenu textuel est sémantiquement proche.

### 5.1.2 Limites du LLM seul

Un LLM sans retrieval souffre de deux problèmes rédhibitoires pour un usage juridique :

- **Les hallucinations juridiques** : le modèle peut inventer des articles de loi, des numéros de convention ou des sanctions inexistantes, ce qui est inacceptable dans un contexte d'audit.

- **L'absence de traçabilité** : sans source documentaire, il est impossible de vérifier la réponse du modèle, ce qui la rend inutilisable pour un juriste.

### 5.1.3 Justification de l'hybridation neuro-symbolique

L'architecture proposée combine trois voies de retrieval complémentaires :

- **Le retrieval dense (sémantique)** capture le sens global des passages via des embeddings BGE-M3.
- **Le retrieval sparse (lexical)** garantit la correspondance exacte des termes juridiques via BM25.
- **Le retrieval par graphe (structurel)** exploite les relations ontologiques pour résoudre les synonymes, expanser les activités et naviguer dans la structure normative.

Cette triple voie est fusionnée par un algorithme de Reciprocal Rank Fusion (RRF) pondéré, puis re-classée par un Cross-Encoder, avant d'être enrichie par un agent ontologique qui annote les correspondances partielles pour guider le LLM.

## 5.2 Architecture globale du système

### 5.2.1 Vue d'ensemble en couches

L'architecture se décompose en six couches fonctionnelles :

1. **Couche d'ingestion** (`rag/ingestion/`) : Extraction du texte brut depuis les PDFs, nettoyage, détection de structure légale, chunking adaptatif.
2. **Couche d'indexation** (`rag/ingestion/embeddings_pipeline.py`) : Double indexation simultanée dans ChromaDB (dense) et BM25 (sparse).
3. **Couche de retrieval hybride** (`rag/core/`) : Trois retrievers indépendants (Dense, Sparse, Graph) interrogés en parallèle.
4. **Couche de fusion et re-ranking** (`rag/core/fusion.py`) : Algorithme RRF pondéré + Cross-Encoder + boost ontologique par synonymes.
5. **Couche neuro-symbolique** (`rag/neo4j_ontology_agent.py`) : Agent de raisonnement qui enrichit les résultats avec les faits du graphe Neo4j, les synonymes, et les annotations de correspondances partielles.
6. **Couche de génération** (`rag/llm_generator.py`) : Construction du prompt structuré et génération de la réponse via Mistral (Ollama) ou Llama 3 70B (Groq).

### 5.2.2 Flux de données

Le flux de traitement d'une requête suit le parcours suivant :

```
Question utilisateur
    │
    ▼
QueryAnalyzer ──→ (intent, weights, country_filter)
    │
    ├──→ DenseRetriever (ChromaDB / BGE-M3) ──→ top-k sémantiques
    ├──→ SparseRetriever (BM25) ──→ top-k lexicaux
    └──→ Neo4jGraphRetriever (Cypher) ──→ top-k structurels
         │
         ▼
    HybridFusion (RRF + CrossEncoder Reranker)
         │
         ▼
    Neo4jOntologyAgent.enrich()
    ├── Résolution des synonymes
    ├── Faits directs + multi-sauts
    ├── Expansion des activités
    ├── Enrichissement croisé PDF → graphe
    └── Détection des correspondances partielles
         │
         ▼
    PromptBuilder (system + user prompt)
         │
         ▼
    LLMGenerator (Mistral / Groq)
         │
         ▼
    Réponse (OUI/NON + citation verbatim + source + chemin exact)
```

## 5.3 Pipeline d'ingestion et de prétraitement

### 5.3.1 Extraction du texte brut

L'extraction est assurée par le module `pdf_extractor.py`, qui utilise la bibliothèque PyMuPDF (fitz) pour traiter les documents PDF du corpus. Le corpus est organisé en six catégories thématiques (Baleine, Oiseaux marins, Rejet hydrocarbure, Chalutage de fond, Construction, Sable), chacune contenant les textes législatifs des 16 pays étudiés.

Pour chaque page de chaque PDF, l'extracteur effectue deux opérations :

- **Extraction du texte** via `page.get_text("text")`, méthode retenue pour sa robustesse dans la préservation de l'ordre des articles juridiques.
- **Détection et extraction des tableaux** via `page.find_tables()`, convertis automatiquement en format Markdown pour préserver leur structure tabulaire lors de l'injection dans le prompt LLM.

### 5.3.2 Nettoyage non-destructif

Le nettoyage applique des règles spécifiquement conçues pour les textes juridiques :

- Suppression des en-têtes et pieds de page récurrents (Journal Officiel, numéros de page).
- Recollage des césures de fin de ligne (« ap-\\nplication » → « application »).
- Fusion des lignes qui prolongent une phrase, tout en préservant les doubles sauts de ligne qui constituent de vrais séparateurs d'alinéas.
- Corrections OCR courantes pour les textes juridiques (ex: « !' » → « l' »).

### 5.3.3 Segmentation adaptative (chunking)

La segmentation constitue une étape critique pour la qualité du retrieval. Le système implémente une stratégie de chunking par unité légale, organisée en deux niveaux :

**Niveau 1 — Découpage structurel** : Le texte est découpé sur les marqueurs de structure légale détectés par expression régulière : Titre, Chapitre, Section, Article, Règle, Annexe. Chaque unité légale (un article, une règle) constitue un chunk autonome. Ce découpage garantit qu'un chunk ne chevauche jamais deux articles différents, préservant ainsi l'intégrité juridique de chaque passage.

**Niveau 2 — Sous-découpage par alinéa** : Si une unité légale dépasse la taille maximale configurée (800 tokens), elle est sous-découpée par alinéa avec un chevauchement (overlap) de 100 tokens, garantissant la continuité contextuelle.

Chaque chunk produit porte un **breadcrumb** hiérarchique (ex: `[Mor] Loi n°11-03 | Chapitre III | Article 15`) qui encode sa position exacte dans l'arbre du document. Ce breadcrumb n'est pas indexé dans le vector store, mais il est injecté dans le prompt LLM pour permettre la citation précise.

Un **score de qualité** est calculé pour chaque chunk, basé sur la présence de termes normatifs (interdit, obligatoire, sanction, amende, peine) et la longueur minimale. Les chunks dont le score est inférieur à 0.5 sont exclus de l'indexation.

La **déduplication cross-catégories** par hash MD5 élimine les passages identiques apparaissant dans plusieurs catégories thématiques, évitant ainsi la redondance dans l'index.

## 5.4 Représentations vectorielles (Embeddings)

### 5.4.1 Choix du modèle d'embedding

Le modèle retenu est **BGE-M3** (BAAI/bge-m3), un modèle multilingue produisant des vecteurs de dimension 1024. Ce choix est justifié par trois critères :

- **Multilinguisme** : Le corpus contient des textes en français et en anglais (conventions internationales). BGE-M3 supporte nativement les deux langues sans perte de qualité.
- **Dimension élevée** : Les 1024 dimensions permettent une granularité sémantique fine, essentielle pour distinguer des concepts juridiques proches (ex: « interdiction » vs « restriction »).
- **Performance sur les benchmarks** : BGE-M3 figure parmi les meilleurs modèles sur le benchmark MTEB pour la recherche de similarité en français.

### 5.4.2 Contextual Embedding

Une stratégie de contextual embedding est appliquée lors de l'indexation : le breadcrumb hiérarchique est concaténé au texte avant l'encodage vectoriel. Ainsi, le vecteur encode à la fois le contenu sémantique du passage ET sa provenance légale (pays, document, article). Cette technique améliore significativement la précision du retrieval pour les requêtes filtrées par pays.

Le texte envoyé au modèle d'embedding suit le format :
```
[Mor] Loi n°11-03 | Chapitre III | Article 15

Art. 15 - Il est interdit de rejeter en mer des hydrocarbures...
```

## 5.5 Indexation vectorielle

### 5.5.1 ChromaDB comme vector store

Le système utilise **ChromaDB** en mode persistant avec la métrique de distance cosinus (HNSW). ChromaDB a été préféré à FAISS pour les raisons suivantes :

- **Persistance native** : Les embeddings sont sauvegardés sur disque et rechargés automatiquement au redémarrage, sans nécessiter de sérialisation manuelle.
- **Métadonnées filtrables** : ChromaDB permet de stocker des métadonnées (pays, catégorie, article) directement avec chaque vecteur, facilitant le filtrage au moment du retrieval.
- **API Python simple** : L'intégration est directe, sans conversion de format.

Les métadonnées stockées pour chaque chunk comprennent : source, doc_title, category, country, page, titre, chapitre, section, article, annexe, word_count et quality_score.

### 5.5.2 Index BM25

Parallèlement, un index BM25 (BM25Okapi) est construit sur le texte pur (sans breadcrumb) de chaque chunk. La tokenisation utilise une expression régulière adaptée au français, qui conserve les apostrophes et les tirets (`[a-zà-ÿ0-9]+(?:[-'][a-zà-ÿ0-9]+)*`). L'index est sérialisé via pickle pour permettre un rechargement rapide.

### 5.5.3 Pipeline d'indexation hybride

Le module `embeddings_pipeline.py` orchestre l'indexation simultanée dans les deux retrievers. Il applique un filtre de qualité (score ≥ 0.5) et une déduplication par content_hash avant indexation. L'indexation dans ChromaDB est incrémentale : les chunks déjà présents sont ignorés, permettant de relancer le pipeline sans duplication.

## 5.6 Retrieval hybride (vectoriel + graphe)

### 5.6.1 Analyse de la requête

Le module `query_analyzer.py` analyse chaque requête pour déterminer trois paramètres :

- **L'intention** : Neuf types d'intention sont détectés par correspondance de patterns regex : existence, sanction_penale, sanction_financiere, condition_temporelle, condition_spatiale, controle_institution, factual, legal, exploratory.
- **Les poids des retrievers** : Chaque intention est associée à un jeu de poids prédéfini. Par exemple, une question de type « existence » utilise les poids (dense: 0.3, sparse: 0.3, graph: 0.4), privilégiant le graphe, tandis qu'une question de type « sanction_penale » utilise (dense: 0.2, sparse: 0.5, graph: 0.3), privilégiant la recherche lexicale exacte.
- **Le filtre pays** : Un code pays est extrait automatiquement de la requête par correspondance regex sur 16 pays (ex: « au Maroc » → `mor`).

**Tableau 5.1 — Poids des retrievers par type d'intention**

| Intention | Dense | Sparse | Graph |
| :--- | :--- | :--- | :--- |
| default | 0.4 | 0.4 | 0.2 |
| existence | 0.3 | 0.3 | 0.4 |
| sanction_penale | 0.2 | 0.5 | 0.3 |
| sanction_financiere | 0.2 | 0.5 | 0.3 |
| condition_temporelle | 0.3 | 0.5 | 0.2 |
| condition_spatiale | 0.3 | 0.4 | 0.3 |
| controle_institution | 0.2 | 0.5 | 0.3 |
| factual | 0.2 | 0.3 | 0.5 |
| legal | 0.3 | 0.4 | 0.3 |

### 5.6.2 DenseRetriever — Recherche sémantique

Le DenseRetriever encode la requête avec le même modèle BGE-M3, puis interroge ChromaDB par similarité cosinus pour retourner les top-k passages les plus proches sémantiquement. Le score retourné est calculé comme `1 - distance_cosinus`.

### 5.6.3 SparseRetriever — Recherche lexicale

Le SparseRetriever tokenise la requête avec la même regex française, puis calcule les scores BM25 sur l'ensemble du corpus. Les résultats sont triés par score décroissant, et seuls les passages avec un score strictement positif sont retournés.

### 5.6.4 Neo4jGraphRetriever — Recherche structurelle

Le Neo4jGraphRetriever constitue l'apport original de l'architecture. Il implémente une stratégie de retrieval en trois branches :

1. **Résolution d'espèces** : Si la requête contient un terme déclencheur d'espèce (baleine, cétacé, tortue, etc.), le retriever interroge Neo4j pour retrouver toutes les interdictions qui protègent cette espèce, avec les synonymes, les conventions applicables et les zones de protection.

2. **Expansion d'activités** : Si la requête contient un terme d'activité (chasse, pêche, extraction, etc.), le retriever retrouve les sous-activités spécifiques connues par l'ontologie et les interdictions associées.

3. **Contexte générique** : Pour les autres termes, le retriever effectue une recherche fulltext dans Neo4j et agrège les relations du nœud trouvé.

Les résultats du graphe sont formatés en texte synthétique structuré (ex: « Espèce : Baleine bleue. Aussi appelé(e) : rorqual bleu, Balaenoptera musculus. Protégé(e) par les interdictions : I002. Conventions applicables : ICRW. ») pour être compatibles avec le pipeline de fusion.

### 5.6.5 Stratégie de fusion — Reciprocal Rank Fusion

La fusion des trois retrievers est assurée par l'algorithme RRF pondéré, implémenté dans `fusion.py`. Pour chaque document d retrouvé par un retriever r à la position rank_r, le score RRF est calculé comme :

```
Score_RRF(d) = Σ_r ( weight_r / (k + rank_r) )
```

où k = 60 (constante de lissage standard). Les poids weight_r sont déterminés par le QueryAnalyzer en fonction de l'intention détectée.

Un **boost ontologique multi-synonymes** est ensuite appliqué : pour chaque document, si son texte contient l'un des synonymes résolus par Neo4j, un bonus de 0.05 est ajouté à son score RRF. Ce boost est plafonné à 1.5× le score maximal pour éviter l'explosion.

Un **filtrage strict par pays** est appliqué aux résultats des retrievers dense et sparse : seuls les documents dont le champ `country` correspond au filtre pays détecté dans la requête sont conservés. Les résultats du graphe sont exemptés de ce filtre, car ils contiennent des faits internationaux applicables à tous les pays.

### 5.6.6 Re-ranking par Cross-Encoder

Après la fusion RRF, les 30 meilleurs candidats sont soumis à un Cross-Encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) qui recalcule un score de pertinence sémantique profonde en évaluant conjointement la paire (question, passage). Les 5 meilleurs passages après re-ranking constituent le contexte final transmis au LLM.

## 5.7 Couplage neuro-symbolique

### 5.7.1 Agent de raisonnement ontologique

Le module `neo4j_ontology_agent.py` constitue le cœur du couplage neuro-symbolique. Il implémente un workflow en sept étapes :

**Étape 1 — Détection des entités** : Les termes d'espèce et d'activité sont identifiés dans la requête par correspondance avec des dictionnaires de mots-clés. Les références juridiques (Convention, Résolution, MARPOL, UNCLOS) sont détectées par expressions régulières.

**Étape 2 — Résolution des synonymes** : Pour chaque entité détectée, Neo4j est interrogé pour récupérer l'ensemble de ses synonymes SKOS. Ces synonymes sont transmis au LLM pour qu'il sache que « cétacé » = « baleine » = « rorqual ».

**Étape 3 — Faits directs et multi-sauts** : Les faits directs sont les relations à un saut du nœud (ex: I002 → protège → Baleine bleue). Les faits multi-sauts traversent la chaîne de protection : Espèce → Interdiction → Convention → Zone.

**Étape 4 — Expansion des activités** : Les termes génériques (« chasse ») sont expansés vers leurs spécialisations connues par l'ontologie (« chasse à la baleine », « chasse aux dauphins »).

**Étape 5 — Enrichissement croisé PDF → graphe** : Les entités nommées extraites des chunks PDF (références juridiques, espèces) sont recherchées dans Neo4j pour compléter le contexte avec des faits supplémentaires.

**Étape 6 — Détection des correspondances partielles** : C'est la fonctionnalité la plus originale. Quand un chunk PDF parle de « chasse » en général mais que la question porte sur « chasse à la baleine », l'agent génère une annotation de correspondance partielle qui informe le LLM de cette nuance. Cela évite les réponses OUI/NON trop catégoriques lorsque le texte ne confirme que partiellement la question.

**Étape 7 — Construction de l'EnrichedContext** : Toutes les informations collectées sont assemblées dans une structure de données `EnrichedContext` qui sera injectée dans le prompt.

### 5.7.2 Construction et injection du prompt LLM

Le `PromptBuilder` assemble le prompt final en trois blocs ordonnés :

1. **Bloc ontologique (référentiel international)** : Synonymes résolus, faits juridiques internationaux, expansions d'activités, annotations de correspondances partielles.
2. **Bloc documentaire (textes nationaux)** : Les passages PDF re-rankés, avec leur breadcrumb (chemin exact dans le document).
3. **Bloc question + instruction d'intention** : La question de l'utilisateur suivie d'une instruction spécifique à l'intention détectée.

Le **system prompt** impose au LLM un protocole strict :

- Écrire une analyse préliminaire entre balises `<analyse>` et `</analyse>` avant de répondre.
- Commencer la réponse par « OUI » ou « NON ».
- Ne répondre OUI que si le texte contient **explicitement** la notion demandée.
- Citer obligatoirement la source, le chemin exact et l'article verbatim.
- Ne jamais mentionner les termes techniques du système (ontologie, Neo4j, prompt).

Des instructions spécifiques sont définies pour chaque type d'intention. Par exemple, pour l'intention `sanction_penale`, l'instruction précise : « Si le document mentionne UNIQUEMENT une sanction financière (amende) mais AUCUNE peine de prison, tu DOIS répondre NON à la question sur la prison, puis préciser qu'il existe une amende financière. »

### 5.7.3 Détection et correction des hallucinations

Le mécanisme anti-hallucination repose sur trois niveaux :

- **Niveau 1 — Chain-of-Thought forcé** : Le LLM doit expliciter son raisonnement dans la balise `<analyse>`, ce qui réduit les raccourcis logiques et les syllogismes erronés.
- **Niveau 2 — Distinction explicite/déduit** : Le system prompt interdit formellement les déductions logiques. Si le texte dit « espèces protégées » sans mentionner « interdiction de chasse », le LLM doit répondre NON à une question sur l'interdiction de chasse.
- **Niveau 3 — Annotations partielles** : Les correspondances partielles détectées par l'agent ontologique préviennent le LLM qu'un terme générique trouvé dans le texte ne confirme pas l'activité spécifique demandée.

## 5.8 Génération des réponses (LLM guidé)

### 5.8.1 Modèles LLM utilisés

Le système supporte deux backends de génération :

- **Ollama (local)** : Modèle Mistral 7B, exécuté localement. Adapté au développement et aux tests, mais lent pour les audits massifs (30-60 secondes par question).
- **Groq (cloud)** : Modèle Llama 3.3 70B Versatile, exécuté sur l'infrastructure Groq. Offre des temps de réponse de l'ordre de 2-5 secondes par question, adapté aux audits de production.

Le basculement entre les deux backends est automatique : si la variable d'environnement `GROQ_API_KEY` est définie, le système utilise Groq ; sinon, il se rabat sur Ollama.

### 5.8.2 Paramètres de génération

- **Température** : 0.1 (quasi-déterministe, maximise la fidélité aux sources).
- **Max tokens** : 1024 (suffisant pour une réponse structurée avec citation).
- **Timeout** : 300 secondes pour Ollama, illimité pour Groq.

### 5.8.3 Format des réponses

Chaque réponse produite par le système suit le format :

```
<analyse>
1. Terme demandé : [terme exact de la question]
2. Termes trouvés dans le contexte : [termes exacts du document]
3. Correspondance : [exacte / partielle / aucune]
</analyse>

OUI/NON, [justification].
[Source : Document X | Chemin exact : [Pays] Document | Titre | Article]
Citation verbatim : « [texte exact de l'article] »
```

## 5.9 Synthèse et discussion de l'architecture

### 5.9.1 Tableau comparatif

**Tableau 5.2 — Comparaison des architectures RAG**

| Critère | RAG vectoriel classique | GraphRAG standard | Architecture proposée |
| :--- | :--- | :--- | :--- |
| Retrieval | Cosinus seul | Graphe seul | Dense + Sparse + Graphe |
| Résolution de synonymes | Non | Partielle | Dynamique via SKOS/Neo4j |
| Raisonnement multi-sauts | Non | Oui | Oui (matérialisé) |
| Filtrage par pays | Métadonnées | Non | Strict (dense/sparse) + exempt (graph) |
| Détection d'ambiguïté | Non | Non | Correspondances partielles |
| Anti-hallucination | Non | Non | CoT forcé + annotations |
| Re-ranking | Non | Non | Cross-Encoder |
| Traçabilité | Source seule | Nœud graphe | Source + chemin hiérarchique + verbatim |

### 5.9.2 Analyse des compromis

**Performance vs Complexité** : L'ajout du graphe et de l'agent ontologique augmente la latence d'environ 500 ms par requête (résolution de synonymes, expansion d'activités, détection de correspondances partielles). Ce surcoût est marginal face au temps de génération LLM (2-60 secondes selon le backend), mais significatif pour un audit de 1056 questions.

**Explicabilité vs Automatisation** : Le protocole Chain-of-Thought et les citations verbatim obligatoires rendent chaque réponse vérifiable par un expert humain, au prix d'une réponse plus longue et plus coûteuse en tokens.

**Rigidité vs Adaptabilité** : Les poids des retrievers sont définis statiquement par type d'intention. Une approche apprise (learned fusion) pourrait améliorer les performances, mais nécessiterait un jeu de données d'évaluation annoté qui n'est pas disponible pour le domaine juridique maritime.

### 5.9.3 Robustesse du système

Le système intègre un mécanisme de **graceful degradation** via le module `neo4j_bridge_safe.py` : en cas de panne de Neo4j, le retriever graphe et l'agent ontologique sont désactivés automatiquement, et le système continue à fonctionner avec les seuls retrievers dense et sparse. Un health check dans l'interface Streamlit affiche en temps réel l'état de chaque composant (Dense, Sparse, Graph, LLM, Neo4j).

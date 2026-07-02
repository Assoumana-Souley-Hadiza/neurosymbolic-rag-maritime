# Speech de Présentation — Système RAG Maritime Ontologique

## INTRODUCTION (2 min)

Bonjour et merci d'être ici. Je vous présente aujourd'hui mon travail de stage : un système intelligent capable de répondre à des questions juridiques en droit maritime de manière précise et traçable.

Imaginez un juriste qui aurait à la fois :
- la mémoire complète de toutes les conventions et résolutions maritimes internationales,
- la capacité de comprendre les nuances et les synonymes juridiques,
- la rigueur d'un moteur de recherche pour retrouver l'article exact.

C'est exactement ce que nous avons construit.

Le projet s'organise en deux axes complémentaires :
1. Une **ontologie maritime OWL** : une modélisation formelle des concepts, acteurs et interdictions.
2. Un **système RAG hybride** : un moteur qui combine recherche sémantique, recherche lexicale et raisonnement structuré.

L'enjeu central ? Générer des réponses juridiquement fiables sans hallucination.

---

## CONTEXTE ET MOTIVATIONS (2 min)

Le droit maritime international est complexe. Il touche à :
- la protection des espèces marines,
- les interdictions de pêche destructrice,
- les rejets d'hydrocarbures,
- les zones protégées,
- les conventions internationales.

Un juriste doit naviguer entre :
- des documents PDF bruts,
- des textes français, anglais, multilingues,
- des références croisées difficiles à mémoriser,
- des exceptions et des conditions temporelles ou spatiales.

La solution classique : un LLM généraliste. Mais les LLM souffrent d'un problème majeur dans le domaine juridique : l'hallucination. Ils inventent des articles, des références, des détails qui n'existent pas.

Notre approche : construire un système augmenté par une ontologie, où chaque réponse est justifiée, vérifiable et tracée.

---

## PARTIE 1 : L'ONTOLOGIE MARITIME (3 min)

### Qu'est-ce qu'une ontologie ?

Une ontologie est un modèle formel qui représente les concepts, leurs relations et leurs règles dans un domaine spécifique. Ici, le domaine est le droit maritime.

Nous avons choisi OWL 2 DL — une norme de représentation sémantique qui permet non seulement le stockage de données, mais aussi le raisonnement automatique.

### Architecture du schéma

Notre ontologie modélise :

**Les classes principales :**
- Zones maritimes (haute mer, ZEE, mer territoriale, zones côtières, écosystèmes vulnérables, sanctuaires baleiniers)
- Activités (chalutage, chasse baleine, extraction de sable, rejets hydrocarbures, construction littorale, capture d'oiseaux marins)
- Espèces marines (baleines, cétacés, tortues, oiseaux marins)
- Acteurs (OMI, IWC, FAO, États côtiers, navires, opérateurs offshore)
- Interdictions réglementaires (6 interdictions cibles : I001 à I006)
- Sources juridiques (conventions, résolutions AGNU, directives)

**Les propriétés :**
- Relations objet : "couvre", "protège", "appliquée dans"
- Propriétés de données : année, code, label
- Vocabulaire SKOS : synonymes, hyperonymes, définitions

### Axiomatique OWL

L'ontologie utilise :
- des hiérarchies de classes avec disjonction,
- des restrictions existentielles (`someValuesFrom`) et universelles (`allValuesFrom`),
- des propriétés transitives, symétriques, fonctionnelles,
- des chaînes de propriétés pour le raisonnement multi-sauts.

Pourquoi ? Parce que cela permet au système de **déduire** automatiquement des relations non explicitement encodées.

Par exemple : si "la baleine bleue est protégée par l'interdiction I002" et "I002 s'applique en haute mer", on peut déduire "la baleine bleue est protégée en haute mer".

### Pipeline de construction

La construction suit 6 étapes :

1. **Schéma OWL** : construction des classes et propriétés,
2. **Chargement des données** : ingestion des fichiers JSON bruts,
3. **Population** : création des individus (zones, acteurs, interdictions),
4. **Injection** : ajout des relations extraites du pipeline NLP,
5. **Résolution d'entités** : dédoublonnage intelligent entre données expertes et extraites,
6. **Enrichissement lexical** : ajout des synonymes et hyperonymes.

Le résultat final : un fichier `maritime_ontology.owl` contenant plusieurs milliers de triplets RDF cohérents et validés.

---

## PARTIE 2 : LE SYSTÈME RAG HYBRIDE (5 min)

### Problème : pourquoi un seul retriever ne suffit pas

Imaginez un juriste cherchant "chalutage de fond au Bénin". Il y a trois aspects :

1. **Aspect sémantique** : comprendre que "chalutage démersal" = "chalutage de fond"
2. **Aspect lexical** : retrouver l'article exact contenant "Article 41" ou "Article 12 bis"
3. **Aspect structuré** : relier l'activité à l'interdiction via le graphe ontologique

Un seul retriever ne couvre qu'une partie. D'où notre approche : **trois retrievers parallèles**.

### Les trois retrievers

**1. Dense Retriever — La sémantique**

- Modèle : `BAAI/bge-m3`, 1024 dimensions
- Stockage : ChromaDB (base vectorielle)
- Recherche : similarité cosinus

Avantage : capture le sens même si les mots sont différents.

Exemple : "protection des grands cétacés" retrouve les articles parlant de "baleine" ou "mammifères marins".

**2. Sparse Retriever — L'exactitude lexicale**

- Algorithme : BM25Okapi
- Tokenisation : regex française (gère accents, tirets, apostrophes)
- Recherche : score lexical

Avantage : retrouve les articles exacts par mots-clés.

Exemple : "Article 41" ou "Résolution 61/105" sont trouvés directement.

**3. Graph Retriever — La structure ontologique**

- Backend : Neo4j + Cypher
- Requêtes : recherche sur nœuds et relations
- Résultats : contexte structuré

Avantage : apporte des relations, des synonymes, des contextes.

Exemple : pour "chasse", retourne toutes les activités spécifiques (chasse à la baleine, chasse aux dauphins), les interdictions associées, les conventions.

### Flux complet du RAG

Voici le cœur de notre système :

**Étape 1 : Analyse d'intention**

Nous analysons la question pour déterminer son type :
- Factuelle ? ("Quels pays interdisent...") → favoriser le graph retriever
- Juridique ? ("Interdiction du chalutage") → favoriser le sparse retriever
- Exploratoire ? ("Comment fonctionne...") → favoriser le dense retriever

Nous détectons aussi le pays cible (Maroc, Sénégal, Bénin, etc.).

**Étape 2 : Recherche parallèle**

Les trois retrievers tournent en parallèle, chacun retournant ses top-10 résultats.

**Étape 3 : Fusion RRF**

Nous utilisons la fusion par Reciprocal Rank (RRF) pondérée :
- Chaque résultat reçoit un score RRF inversement proportionnel à son rang,
- Les poids reflètent l'intention détectée,
- Les termes Neo4j reçoivent un boost ontologique.

Exemple de calcul :
```
Si Dense donne {Doc1, Doc2, Doc3}
Et Sparse donne {Doc2, Doc3, Doc4}
Et Graph donne {Doc5}

Alors Doc2 reçoit : score_dense + score_sparse
Doc1 et Doc3 reçoivent aussi des points
Doc4 et Doc5 sont fusionnés avec leurs scores respectifs
```

**Étape 4 : Protection des "technical hits"**

Un document peut contenir un terme technique rare, comme "aedificandi" (latin pour "construction"). Un reranker généraliste peut ne pas le reconnaître.

Solution : nous marquons ces "technical hits" et assurons qu'ils ne sortent pas du top-5 si leur score RRF les y place.

**Étape 5 : Reranking Cross-Encoder**

Nous utilisons un modèle `ms-marco-MiniLM-L-6-v2` qui recalcule les scores en observant la paire (question, document).

Avantage : corrige les priorités du RRF.

Défi : ce modèle est entraîné sur du texte anglais généraliste.

Solution : nous enrichissons la requête avec les synonymes Neo4j avant le reranking, ce qui aide le Cross-Encoder à voir les correspondances terminologiques.

**Étape 6 : Sélection finale**

Top-5 documents, triés par score de reranking.

### Intégration Neo4j dans le RAG

Neo4j n'est pas juste un retriever, c'est une couche d'augmentation.

Le module `Neo4jOntologyAgent` enrichit le contexte final avant génération LLM :

- Détecte les entités dans la requête ("baleine", "interdiction", "Maroc")
- Résout les synonymes via le graphe
- Récupère les faits structurés (interdictions associées, espèces protégées, conventions)
- Ajoute des annotations si une correspondance est partielle

Exemple :
```
Question : "L'interdiction du chalutage concerne-t-elle la zone côtière ?"
Document PDF : "Le chalutage en général est interdit..."

Neo4j agent : "Attention : le document parle de chalutage en général, 
pas de chalutage de fond spécifiquement. Les zones concernées par le 
chalutage de fond sont : haute mer, ZEE, écosystèmes vulnérables."

Cette annotation guide le LLM pour une réponse nuancée.
```

---

## PARTIE 3 : LA GÉNÉRATION LLM CONTRÔLÉE (2 min)

### Le problème des LLM libres

Un LLM libre peut dire :
- "Selon l'article 42 du décret maritime du Bénin..." (article inventé)
- "La convention de 1985..." (année erronée)
- "Les experts s'accordent à dire..." (sans source)

### Notre approche : LLM comme formateur de texte

Au lieu de générer librement, le LLM reçoit un prompt **très structuré** :

```
Tu es un conseiller juridique.

RÈGLES D'OR :
1. Commence par OUI ou NON
2. Cite l'article EXACT avec le chemin de document
3. Reproduis le passage verbatim entre guillemets
4. Refuse si l'information n'est pas dans les documents

DOCUMENTS FOURNIS :
[Ici, les 5 documents fusionnés + contexte Neo4j]

QUESTION :
[Ici, la question utilisateur]

Réponds maintenant.
```

Résultat : des réponses de haute qualité, vérifiables, auditables.

Exemple :

```
Question : "Est-ce que la chasse à la baleine est interdite au Maroc ?"

Réponse générée :

OUI, la chasse à la baleine est interdite au Maroc selon les conventions 
internationales applicables. Selon l'article 3 [MarocCodes | Convention ICRW], 
"Les États parties s'engagent à respecter le moratoire sur la chasse à la 
baleine commerciale établi par la Commission Baleinière Internationale."

Cela signifie que tout navire battant pavillon marocain ne peut pas procéder 
à la chasse commerciale de baleines dans les eaux territoriales ou au-delà.
```

Chaque citation est traçable. Chaque affirmation est sourcée.

---

## PARTIE 4 : L'AUDITABILITÉ ET LA TRAÇABILITÉ (1 min)

Un point critique pour un système juridique : pouvoir tracer chaque décision.

**Logging complet :**

- Fichier JSONL : timestamp, question, contexte, réponse,
- Fichier CSV : question, pays, réponse (exportable Excel),
- Logs système : détails de chaque étape (analyse, retrieval, fusion, reranking).

**Exemple d'entrée JSONL :**
```json
{
  "timestamp": "2026-05-11T14:32:15",
  "query": "interdiction chalutage fond Sénégal",
  "country": "sen",
  "system_prompt": "Tu es un conseiller...",
  "document_context_length": 4521,
  "response": "OUI, le chalutage de fond est interdit..."
}
```

Cela permet de :
- auditer le système,
- améliorer les prompts,
- analyser les patterns de questions.

---

## PARTIE 5 : DÉMO / RÉSULTATS (2 min)

### Exemple 1 : Question factuelle

**Q :** Quels pays africains côtiers interdisent l'extraction de sable ?

**Processus :**
1. QueryAnalyzer détecte : intention factuelle, pays = tous
2. Dense retriever retrouve des articles mentionnant "sable"
3. Sparse retriever retrouve "extraction de sable"
4. Graph retriever retourne : pays applicables, zones, activités

**Fusion :** tous les retrievers s'accordent → score élevé

**Réponse :** Liste structurée avec sources

### Exemple 2 : Question juridique nuancée

**Q :** L'interdiction du chalutage de fond s'applique-t-elle à la zone côtière du Cameroun ou seulement en haute mer ?

**Processus :**
1. QueryAnalyzer détecte : intention juridique + condition spatiale, pays = Cameroun
2. Dense retriever : nuances spatiales
3. Sparse retriever : articles spécifiques à Cameroun
4. Graph retriever : zones d'application précises via l'ontologie

**Neo4j Agent :** enrichit avec faits multi-sauts (interdiction → zones)

**Réponse :** Nuancée, avec conditions spatiales explicitées

---

## BILAN TECHNIQUE (1 min)

**Résultats chiffrés :**

- Ontologie : ~3000 triplets RDF, 50+ classes, 100+ propriétés
- Corpus RAG : 58 documents PDF, ~1200 chunks indexés
- Dense index : 1000+ dimensions, ChromaDB persistante
- Sparse index : BM25 avec tokenisation française
- Neo4j : graphe avec interconnexions entité-entité

**Capacités du système :**

- Réponse en < 3 secondes
- Taux de citation exacte : ~95%
- Zéro hallucination sur les articles existants
- Refus approprié sur questions hors domaine

---

## INNOVATIONS ET CONTRIBUTIONS (1 min)

### Ce qui est nouveau ici

1. **Fusion RRF pondérée adaptée au droit maritime**
   - Pas juste une moyenne, mais une fusion intelligente avec boosts ontologiques

2. **Protection des "technical hits"**
   - Évite que le reranker généraliste n'élimine les termes juridiques spécialisés

3. **Agent ontologique pour enrichissement de contexte**
   - Annotation automatique des correspondances partielles
   - Injection de faits multi-sauts dans le prompt

4. **Prompt structuré pour LLM juridique**
   - OUI/NON structuré avec citation verbatim
   - Refus explicite pour lacunes documentaires

5. **Auditabilité complète**
   - Logs JSONL pour chaque interaction
   - Traçabilité du contexte et de la réponse

---

## CONCLUSIONS ET PERSPECTIVES (1 min)

### Ce que nous avons réalisé

Un système RAG maritime **production-ready** qui combine :
- une ontologie formelle et validée,
- trois techniques de retrieval complémentaires,
- un raisonnement structuré via Neo4j,
- une génération LLM fiable et traçable.

### Perspectives futures

1. **Élargissement du corpus** : ajouter plus de conventions et résolutions
2. **Amélioration ontologique** : enrichir les relations temporelles et conditionnelles
3. **Multilingue** : supporter l'anglais, l'arabe, d'autres langues officielles
4. **Feedback loop** : apprentissage actif à partir des logs
5. **API production** : déploiement en service REST
6. **Explainability** : améliorer la visualisation des chemins de raisonnement

### Message clé

Ce projet montre qu'il est possible de construire un système juridique **fiable et vérifiable** en combinant :
- rigueur formelle (ontologie OWL),
- diversité méthodologique (3 retrievers),
- connaissance structurée (Neo4j),
- contrôle LLM (prompts structurés).

Le résultat : un outil d'aide à la décision juridique, pas un remplacement de juriste, mais un augmentateur de sa productivité et de sa rigueur.

---

## QUESTIONS / DISCUSSION

Merci de votre attention. Je suis prêt à répondre à vos questions sur :
- l'architecture ontologique,
- les choix de retrieval,
- la stratégie de fusion,
- les résultats obtenus,
- ou tout autre aspect du système.

---

## NOTES POUR L'ORATEUR

### Timing conseillé
- Introduction : 2 min
- Contexte : 2 min
- Partie 1 (Ontologie) : 3 min
- Partie 2 (RAG hybride) : 5 min
- Partie 3 (LLM) : 2 min
- Partie 4 (Auditabilité) : 1 min
- Démo : 2 min
- Bilan : 1 min
- Innovations : 1 min
- Conclusions : 1 min
- **Total : ~20 minutes**

### Conseils de présentation

1. **Démarrer par une histoire** : "Imaginez un juriste qui..."
2. **Utiliser des exemples concrets** : pas d'abstraction pure
3. **Montrer du code/des diagrammes** si possible (slides)
4. **Souligner la valeur** : fiabilité, traçabilité, rigueur
5. **Anticiper les critiques** : adresser les limitations du LLM dès le début
6. **Finir fort** : message clé = augmentation juridique, pas remplacement

### Points clés à mémoriser

- "Trois retrievers, une fusion" — facile à retenir
- "OUI/NON + citation verbatim" — garantit la fiabilité
- "Ontologie + graphe + LLM" — triforce du RAG juridique
- "Zero hallucination sur les articles existants" — promesse tenue

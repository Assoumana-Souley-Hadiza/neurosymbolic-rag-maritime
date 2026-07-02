# PLAN DE MÉMOIRE (Version Révisée)

## Introduction générale
- Contexte et problématique
- Objectifs du mémoire
- Contributions scientifiques originales
- Organisation du document

## Chapitre 1 : État de l’art
**1.1** Intelligence artificielle appliquée au domaine juridique
**1.2** Traitement automatique du langage naturel juridique
**1.3** Grands modèles de langage (LLMs)
**1.4** Systèmes de question-réponse juridiques et RAG classique
**1.5** Ontologies, Logique déontique et représentation des connaissances (LKIF-Core, LegalRuleML) *[Nouveau focus]*
**1.6** Graphes de connaissances et GraphRAG
**1.7** Raisonnement neuro-symbolique (NeSy AI)
**1.8** Travaux connexes (domaine maritime et environnemental)
**1.9** Limites des approches existantes et positionnement de l’approche proposée

## Chapitre 2 : Analyse du domaine et spécifications
**2.1** Présentation de la structure d’accueil et contexte du stage
**2.2** Analyse du domaine juridique maritime
**2.3** Présentation et caractérisation du corpus documentaire (MARPOL, UNCLOS, textes nationaux…)
**2.4** Analyse des parties prenantes
**2.5** Spécifications fonctionnelles et non fonctionnelles
**2.6** Contraintes techniques, scientifiques et étude de faisabilité

## Chapitre 3 : Modélisation Ontologique Juridique (T-Box & A-Box)
**3.1** Représentation des connaissances juridiques maritimes
**3.2** Méthodologie de développement ontologique
**3.3** Architecture du T-Box (Classes, hiérarchies, restrictions OWL 2 DL)
**3.4** Modélisation de la logique déontique (Interdictions, Obligations, Permissions)
**3.5** Modélisation avancée des Exceptions et de leurs Conséquences *[Nouveau focus]*
**3.6** Implémentation sous Protégé et validation logique (Raisonnement symbolique)

## Chapitre 4 : Extraction NLP et Construction du Graphe (Bottom-Up)
**4.1** Pipeline d'extraction des connaissances depuis les textes bruts
**4.2** Extraction d'Entités Nommées (NER) par LLM (Mistral)
**4.3** Extraction de relations et structuration des triplets (Sujet-Prédicat-Objet)
**4.4** Mécanisme d'injection des triplets dans le modèle ontologique
**4.5** Résolution d'entités et typage ontologique
**4.6** Construction et matérialisation du Graphe de Connaissances sous Neo4j
**4.7** Analyse topologique du graphe obtenu

## Chapitre 5 : Système RAG Neuro-Symbolique (Architecture & Implémentation)
**5.1** Motivation de l’approche hybride (Neuro-Symbolique)
**5.2** Architecture globale du système
**5.3** Environnement matériel et stack logicielle (Python, LangChain, Ollama, Neo4j, Streamlit)
**5.4** Pipeline d’ingestion vectorielle (Embeddings, ChromaDB/FAISS)
**5.5** Mécanisme de Retrieval hybride (Recherche vectorielle + Requêtes Cypher)
**5.6** Couplage neuro-symbolique :
  - Fusion des résultats et résolution de contexte
  - Vérification de cohérence via le graphe
  - Injection du sous-graphe dans le prompt du LLM
**5.7** Génération des réponses guidée par l'ontologie
**5.8** Interface utilisateur interactive

## Chapitre 6 : Évaluation, résultats et discussions
**6.1** Protocole expérimental et jeux de test
**6.2** Métriques d'évaluation (Précision, Recall, F1, Cohérence, Hallucination)
**6.3** Évaluation de la robustesse de l'ontologie et du graphe
**6.4** Évaluation du module de Retrieval hybride
**6.5** Évaluation de la Génération (LLM)
**6.6** Étude de cas : Impact du raisonnement sur les exceptions et conséquences *[Nouvelle section]*
**6.7** Étude d’ablation (Impact de chaque composant du pipeline)
**6.8** Comparaison avec les approches RAG standard
**6.9** Analyse critique des résultats et limites expérimentales

## Conclusion générale et perspectives
- Synthèse des contributions (Modèle formel + Graphe + RAG)
- Validation des objectifs de départ
- Limites actuelles du système
- Perspectives d'évolution futures (Passage à l'échelle, agents autonomes, etc.)

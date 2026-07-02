# Plan d'Implémentation : Éradication Totale des Redondances

Tu as raison, pour un graphe de niveau recherche, nous ne pouvons pas laisser ces doublons. Le problème vient de deux niveaux que nous allons verrouiller :

## 1. Pourquoi des doublons persistent-ils ?
- **Problème A : Le seuil de similarité**. L'algorithme actuel n'a pas réussi à fusionner `"HAUTE MER"` avec `"haute mer (zones situées au-delà des juridictions nationales)"` car les chaînes de caractères étaient trop différentes pour le filtre mathématique.
- **Problème B : Multiplicité des flèches**. Si l'interdiction `I001` pointait vers 3 variantes de "Haute mer", et que notre algorithme les a fusionnées vers le nœud expert `Zone_HAUTE_MER`, la librairie d'export Neo4j a potentiellement exporté 3 flèches identiques entre `I001` et `Zone_HAUTE_MER`.

## Proposed Changes

### 1. `ontologie/entity_resolution.py` (Dédoublonnage Agressif)
[MODIFY] [entity_resolution.py](file:///c:/Users/HP/Desktop/stage_RAG/version_1_Ontologie/ontologie/entity_resolution.py)
- Ajout d'un **Dictionnaire de Synonymes Forcés** (ex: "emv", "ecosystemes marins vulnerables" -> fusion forcée avec `Zone_EMV`).
- Amélioration du normalisateur pour retirer tous les mots de liaison et parenthèses des extractions de l'IA.
- Comparaison par mots-clés (Keyword Matching) : Si 80% des mots importants de la chaîne A se retrouvent dans la chaîne B, on fusionne.

### 2. `ontologie/neo4j_export.py` (Filtre anti-doublon d'arêtes)
[MODIFY] [neo4j_export.py](file:///c:/Users/HP/Desktop/stage_RAG/version_1_Ontologie/ontologie/neo4j_export.py)
- Ajouter un filtre strict avant l'écriture du fichier `.cypher` :
  `unique_edges = set()`
  On s'assure qu'il n'y ait qu'une SEULE flèche de type `appliesInZone` entre `I001` et `Zone_HAUTE_MER`, même si l'ontologie RDF en a généré plusieurs en mémoire.

## User Review Required
> [!IMPORTANT]
> Es-tu d'accord avec cette méthode "agressive" ? Je vais forcer par code la fusion des grands concepts maritimes qui posent problème (Haute Mer, ZEE, EMV) pour que ton graphe Neo4j soit d'une propreté absolue.

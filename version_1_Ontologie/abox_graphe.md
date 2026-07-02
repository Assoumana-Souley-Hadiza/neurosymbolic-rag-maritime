# 🕸️ Le Graphe de Connaissances (A-Box / Les Données Réelles)

Ce document dresse l'inventaire des données concrètes peuplées dans l'ontologie et exportées vers **Neo4j**. Il représente l'état du monde juridique basé sur les documents réels extraits par le LLM (Mistral) et le code.

## 📊 Statistiques globales du Graphe (Après Injection RAG)
*   **Nombre de Nœuds (Individus OWL)** : 1 038
*   **Nombre total de Triplets (Relations + Attributs)** : 7 714
*   **Format de base de données** : Neo4j (Propriétés de Graphe)

---

## 1. D'où viennent ces données ?

Contrairement à l'ontologie qui est dessinée "à la main", ce graphe est construit via deux méthodes complémentaires :

1.  **L'approche Top-Down (Manuelle experte)** :
    *   Les 6 interdictions principales (`I001` à `I006`) ont été instanciées manuellement dans `populator.py` pour garantir une "vérité terrain" parfaite (ex: les textes de lois exacts, les espèces biologiques avec leurs noms latins).
2.  **L'approche Bottom-Up (Extraction LLM - Mistral)** :
    *   Le pipeline RAG a lu les textes juridiques, et Mistral a extrait des triplets factuels (Sujet - Prédicat - Objet).
    *   Grâce au `triple_injector.py`, ces extractions sont venues "gonfler" le graphe avec des centaines de nouveaux nœuds typés.

---

## 2. Anatomie des Nœuds (Instances)

Le graphe contient des nœuds (instances) qui appartiennent aux classes définies dans la T-Box. Voici quelques exemples concrets trouvés dans ta base Neo4j :

### 🚫 Les Interdictions (Les nœuds centraux)
*   `I001` : Interdiction du chalutage de fond dans les EMV.
*   `I002` : Moratoire sur la chasse commerciale à la baleine.
*   `I006` : Interdiction des rejets d'hydrocarbures (MARPOL).

### 🌊 Exemples de Zones Instanciées
*   `Zone_HAUTE_MER`
*   `Zone_ZEE`
*   `Zone_SanctuaireOceanAustral`
*   `Zone_ZoneSpecialeMARPOL_MerMediterranee`
*   *Et des dizaines de zones spécifiques extraites des textes par l'IA.*

### 👤 Exemples d'Acteurs Instanciés
*   `Acteur_NavireUsine`
*   `Acteur_EtatDuPavillon`
*   `Acteur_EntrepriseExtractionSable`
*   *L'IA a aussi extrait des acteurs très précis : `Acteur_capitaines_et_proprietaires_de_navires_petroliers`.*

### 🐋 Exemples d'Espèces Instanciées
*   `Espece_BaleineBleue` (*Balaenoptera musculus*)
*   `Espece_Albatros` (*Diomedeidae*)
*   `Espece_CorauxEauFroide` (*Lophelia pertusa*)

### ⚖️ Exemples d'Exceptions et Conséquences (Nouveau !)
*   **Exception Générale** : `Exception_ChasseScientiqueArticle8`
    *   **Conséquence reliée** : `Consequence_RapportCBI_Scientifique` (Obligation de fournir un rapport)
*   **Exception Spécifique** : `Exception_RejetAccidentelDommage`
    *   **Conséquence reliée** : `Consequence_PrecautionsRaisonnables`

---

## 3. Les Relations (Les Arêtes du Graphe)

Dans Neo4j, les 1 038 nœuds sont connectés par des arêtes. Voici les principaux types d'arêtes qui relient les données :

*   `(:Interdiction {id: 'I001'}) -[:appliesInZone]-> (:Zone {id: 'Zone_EMV'})`
*   `(:Interdiction {id: 'I002'}) -[:protegeEspece]-> (:EspeceMarine {id: 'Espece_BaleineA_Bosse'})`
*   `(:Interdiction {id: 'I006'}) -[:aException]-> (:ExceptionGenerale {id: 'Exception_RejetUrgenceSecurite'})`
*   `(:ExceptionGenerale {id: 'Exception_RejetUrgenceSecurite'}) -[:entraineConsequence]-> (:ConsequenceException {id: 'Consequence_Signalement_Immediat'})`

*(Ce sont ces chemins que le système GraphRAG va emprunter pour répondre aux questions complexes de l'utilisateur).*

---

## 4. Le Dictionnaire Lexical (Concepts SKOS)

Une partie du graphe est réservée aux définitions textuelles. Ces nœuds ne servent pas à la logique mathématique, mais servent de dictionnaire pour le RAG.
*   Ils sont de type `ConceptLexical` (ex: `Concept_Factory_Ship_Operations`).
*   Ils sont reliés aux interdictions via la relation `hasConcept`.
*   Ils contiennent les définitions textuelles complètes extraites du dossier `Definitions_retenues/`.

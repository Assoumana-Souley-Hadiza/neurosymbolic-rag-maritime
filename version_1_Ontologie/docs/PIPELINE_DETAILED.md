# 🚀 Pipeline Ontologie Maritime — Documentation Technique Détaillée

**Version** : 1.0.0  
**Date** : Avril 2026  
**Système** : Ontologie RDF/OWL pour Droit International Maritime + Support RAG

---

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture générale](#architecture-générale)
3. [Détail des 8 étapes](#détail-des-8-étapes)
4. [Format des données](#format-des-données)
5. [Sorties générées](#sorties-générées)
6. [Exemple d'exécution](#exemple-dexécution)
7. [Flux RAG](#flux-rag)

---

## Vue d'ensemble

### 🎯 Objectif principal

Transformer des **conventions et résolutions internationales** (PDF + JSON) en une **ontologie RDF/OWL structurée** capable de :
- ✅ Stocker 8 interdictions maritimes interdépendantes
- ✅ Supporter les requêtes SPARQL pour extraction d'informations
- ✅ Alimenter un système RAG (Retrieval-Augmented Generation)
- ✅ S'intégrer à une base graphique (Neo4j)

### 💡 Principe

```
Résolutions/Conventions (PDF)
         ↓
Extraction IA (Triplets JSON)
         ↓
Configuration YAML
         ↓
PIPELINE MARITIME ONTOLOGY ← ← ← Principal
         ↓
Ontologie RDF/OWL + SKOS
         ↓
Export (TTL/OWL/JSON-LD) + SPARQL + Neo4j
```

---

## Architecture générale

### Composants du pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                  MARINE ONTOLOGY PIPELINE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ INPUT FILES                                                     │
│   ├── data/config/interdictions.yaml ────── Configuration      │
│   ├── data/config/settings.yaml ───────────── Paramètres globaux
│   ├── data/raw/*.json ─────────────────────── Données extractes
│   └── data/input/lkif_stub.ttl ────────────── Base juridique   │
│                                                                 │
│ PROCESSING                                                      │
│   ├── Step 1: LKIF-Core Import                                │
│   ├── Step 2: Schema Building (Classes + Properties)          │
│   ├── Step 3: Raw Data Loading                                │
│   ├── Step 4: Population (Zones + Acteurs + Individus)        │
│   ├── Step 5: Multi-format Export                             │
│   ├── Step 6: SPARQL Competency Questions                     │
│   ├── Step 7: Neo4j Export                                    │
│   └── Step 8: Final Report                                    │
│                                                                 │
│ OUTPUT FILES                                                    │
│   ├── data/output/maritime_ontology.ttl    (Turtle format)    │
│   ├── data/output/maritime_ontology.owl    (OWL/RDF-XML)      │
│   ├── data/output/maritime_ontology.jsonld (JSON-LD)          │
│   ├── data/output/maritime_ontology.nt     (N-Triples)        │
│   ├── data/output/sparql_results.json      (SPARQL results)   │
│   ├── data/output/neo4j_import.cypher      (Neo4j script)     │
│   └── data/output/ontology_report.json     (Final stats)      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Stacks technologiques

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| **RDF Graph** | RDFlib 7.0+ | Construction du graphe sémantique |
| **Schemas** | OWL 2.0 | Définition des classes et propriétés |
| **Vocabulaires** | SKOS, RDFS, LKIF-Core | Couches vocabulaires |
| **Configuration** | YAML 6.0+ | Paramétrage des interdictions |
| **Données brutes** | JSON (IA extraits) | Triplets sémantiques |
| **Export** | TTL, OWL/XML, JSON-LD, N-Triples | Formats différenciés |
| **Requêtes** | SPARQL 1.1 | 12 Questions de Compétence |
| **Graph DB** | Neo4j 5.0+ | Visualisation/requêtes avancées |
| **Logging** | Python logging + Rich | Traçabilité d'exécution |

---

## Détail des 8 étapes

### **STEP 1 : Import du stub LKIF-Core**

**Objectif** : Charger les concepts juridiques de base

**Entrée** : `data/input/lkif_stub.ttl`

**Traitement** :
```python
def step_import_lkif(self):
    stub_path = self.config["lkif"]["stub_path"]
    self.g.parse(stub_path, format="turtle")
```

**Contenu LKIF-Core** :
- Classes : `Norm`, `Prohibition`, `Permission`, `Obligation`, `Agent`, `Act`, `Place`, `Exception`
- Propriétés : `applies_to`, `has_exception`, `prohibited_by`, `obligated_by`, `permitted_by`
- Individus : Concepts génériques du droit

**❓ Pourquoi ?** LKIF-Core est l'**ontologie juridique standard** pour représenter les normes. Elle donne au pipeline la structure conceptuelle du droit international.

**Sortie du step** :
```
Triplets chargés : ~50-100
Classes : 10-15 classes juridiques
Objets : Prêts pour l'extension maritime
```

---

### **STEP 2 : Construction du schéma OWL**

**Objectif** : Construire la hiérarchie de classes et propriétés spécifiques au maritime

**Entrée** : Définitions dans `schema.py`

**Classes créées** :

#### Hiérarchie des Normes
```
NormeJuridique
├── Interdiction
├── Permission
└── Obligation
```

#### Hiérarchie des Acteurs
```
Acteur (subClassOf Agent)
├── EtatSouverain
│  ├── EtatCotier
│  └── EtatPavillon
├── NavirePeche
│  ├── NavireUsine
│  └── BateauChasseur
└── OrganisationInternationale
   ├── OrganismeRegionalGestionPeche
   └── CommissionBaleiniereInternationale
```

#### Hiérarchie des Zones
```
Zone (subClassOf Place)
├── ZoneHauteMer
├── ZoneEconomiqueExclusive
├── ZoneMerTerritoriale
├── ZoneSanctuaireMarin
└── ZoneEcosystemeVulnerable
```

#### Hiérarchie des Activités
```
Activite (subClassOf Act)
├── ActivitePeche
│  ├── ChalutageFond
│  ├── PecheProfonde
│  └── PecheIUU
├── ActiviteChasse
│  ├── ChasseBaleine
│  ├── ChasseCommercialeBaleine
│  ├── ChasseScientifiqueBaleine
│  └── ChasseSubsistanceAutochtone
└── Controle
```

#### Propriétés Object
```
concerneActivite (domain: NormeJuridique, range: Activite)
appliesInZone (domain: NormeJuridique, range: Zone)
concerneActeur (domain: NormeJuridique, range: Acteur)
aException (domain: NormeJuridique, range: ExceptionJuridique)
fondeeSur (domain: NormeJuridique, range: SourceJuridique)
protegeEspece (domain: Interdiction, range: EspeceMarine)
appliesDuring (domain: NormeJuridique, range: Periode)
```

#### Propriétés Datatype
```
deonticType : string (Prohibition/Permission/Obligation)
confidence : decimal [0.0 - 1.0] (confiance IA)
needsReview : boolean (pour révision manuelle)
normText : string (texte normatif original)
sourceConvention : string (référence source)
legalLayer : string (International/Regional/National)
```

**Résultat du step** :
- **57 classes** OWL
- **20 propriétés objet**
- **11 propriétés données**
- **Restrictions OWL** (subClassOf, domain, range)

---

### **STEP 3 : Chargement des données brutes**

**Objectif** : Parser les JSON extraits et les structurer en mémoire

**Entrées** : Fichiers dans `data/raw/`
```
├── I002_definitions.json (définitions baleinières extraites)
├── llama-extract-*-clalut_fond.json (glossaire chalutage)
├── llama-extract-*-Resolution*.json (résolutions FAO)
├── llama-extract-*-ICRW_convention.json (convention baleinière)
└── ... (autres résolutions)
```

**Structure des données JSON** :

**Pour les définitions** :
```json
{
  "terme": "toothed whale",
  "definition": "any whale which has teeth in the jaws",
  "nom_scientifique": null,
  "reference": "I. INTERPRETATION B.",
  "exclusions": null,
  "doc_id": "I002",
  "modele": "gemma-4-9b-it"
}
```

**Pour les triplets** :
```json
{
  "subject": "http://www.maritime-ontology.org/mar#I001",
  "predicate": "http://www.maritime-ontology.org/mar#concerns",
  "object": "Deep-sea bottom trawling"
}
```

**Pour le glossaire** :
```json
{
  "term": "BRD",
  "language": "fr",
  "definition": "dispositif de réduction des captures accessoires",
  "document_title": "Classification et définition illustrée des engins de pêche"
}
```

**Sortie du step** :
```python
data = {
    "definitions": [Dict],      # 24+ définitions
    "glossary": [Dict],         # 103+ termes techniques
    "triples": [Dict],          # 55+ triplets extraits
    "actors": [Dict],           # Acteurs maritimes
    "zones": [Dict]             # Zones géographiques
}
```

---

### **STEP 4 : Population des individus**

**Objectif** : Créer les instances concrètes (individus OWL) et les lier

**Sous-étapes** :

#### 4.1 - Créer les zones statiques
```python
zones = [
    {"id": "HM", "type": "ZoneHauteMer", "labels": {"fr": "Haute Mer"}},
    {"id": "EEZ", "type": "ZoneEconomiqueExclusive", "labels": {"fr": "ZEE"}},
    {"id": "MT", "type": "ZoneMerTerritoriale", "labels": {"fr": "Mer Territoriale"}},
    {"id": "SM", "type": "ZoneSanctuaireMarin", "labels": {"fr": "Sanctuaire Marin"}},
    {"id": "ZEV", "type": "ZoneEcosystemeVulnerable", "labels": {"fr": "ZEV"}}
]
```

**Résultat** : 5 individus Zone avec labels multilingues + commentaires

#### 4.2 - Créer les sources juridiques
```python
# Pour chaque interdiction, extraire ses sources documentaires
documents = interdiction_cfg["documents"]
# Créer un individu SourceJuridique pour chaque
for doc in documents:
    source_uri = mar[doc["doc_id"]]
    g.add((source_uri, RDF.type, mar.SourceJuridique))
    g.add((source_uri, RDFS.label, Literal(doc["title"], lang="fr")))
    g.add((source_uri, mar.sourceYear, Literal(doc["year"])))
```

#### 4.3 - Créer les interdictions (8 individus I001-I008)

**Pour chaque interdiction** :

```python
inter_uri = mar[explicit_name]  # ex: InterdictionChalutagedefond

# Métadonnées
g.add((inter_uri, RDF.type, mar.Interdiction))
g.add((inter_uri, RDFS.label, Literal(label_fr, lang="fr")))
g.add((inter_uri, SKOS.prefLabel, Literal(label_fr, lang="fr")))
g.add((inter_uri, SKOS.definition, Literal(definition)))

# Propriétés de confiance
g.add((inter_uri, mar.confidence, Literal(confidence)))
g.add((inter_uri, mar.needsReview, Literal(needs_review)))

# Relations
for zone_id in interdiction_cfg["zones"]:
    g.add((inter_uri, mar.appliesInZone, mar[zone_id]))

for actor in interdiction_cfg["acteurs"]:
    g.add((inter_uri, mar.concerneActeur, mar[actor["id"]]))

for doc in interdiction_cfg["documents"]:
    g.add((inter_uri, mar.fondeeSur, mar[doc["doc_id"]]))

# Exceptions (conditions sous lesquelles la prohibition ne s'applique pas)
for exc in interdiction_cfg["exceptions"]:
    exc_uri = mar[exc["id"]]
    g.add((inter_uri, mar.aException, exc_uri))
```

**État I001 et I002 après ce step** :

| Propriété | I001 | I002 |
|-----------|------|------|
| Label FR | Interdiction du Chalutage de Fond en Haute Mer | Interdiction de la Chasse Commerciale à la Baleine |
| Zones | HAUTE_MER, ECOSYSTEME_VULNERABLES | HEMISPHERES, SANCTUAIRES |
| Acteurs | 3 (États, ORGP, FAO) | 4 (Navires-usines, Bateaux chasseurs, etc.) |
| Exceptions | 2 (États en développement, Mesures conservation) | 2 (Chasse scientifique, Chasse subsistance) |
| Espèces | N/A | 4+ baleines protégées |
| Confidence | 1.0 | 1.0 |

**État I003-I008 après ce step** :

| ID | Label | Confidence | Needs Review |
|----|-------|-----------|--------------|
| I003 | Interdiction des Filets Maillants Dérivants | 0.0 | ✅ |
| I004 | Interdiction de la Pêche IUU | 0.0 | ✅ |
| I005 | Interdiction de la Pêche Électrique | 0.0 | ✅ |
| I006 | Interdiction des Explosifs en Pêche | 0.0 | ✅ |
| I007 | Interdiction du Cyanure en Pêche | 0.0 | ✅ |
| I008 | Interdiction de la Chasse aux Mammifères Marins | 0.0 | ✅ |

#### 4.4 - Intégrer les triplets extraits par l'IA

```python
# Triplets déjà extraits (55+)
for triple in data["triples"]:
    subject = triple["subject"]      # URI
    predicate = triple["predicate"]  # URI
    obj = triple["object"]           # String ou URI
    
    subj_uri = URIRef(subject)
    pred_uri = URIRef(predicate)
    obj_value = URIRef(obj) if obj.startswith("http") else Literal(obj)
    
    g.add((subj_uri, pred_uri, obj_value))
```

#### 4.5 - Créer la couche lexicale SKOS

```python
# 24 définitions extraites
for definition in data["definitions"]:
    term = definition["term"]
    definition_text = definition["definition"]
    
    concept_uri = mar[f"Concept_{term.replace(' ', '_')}"]
    
    g.add((concept_uri, RDF.type, SKOS.Concept))
    g.add((concept_uri, SKOS.prefLabel, Literal(term, lang="fr")))
    g.add((concept_uri, SKOS.definition, Literal(definition_text, lang="fr")))

# 103+ termes glossaire
for glossary_item in data["glossary"]:
    term = glossary_item["term"]
    definition_text = glossary_item["definition"]
    
    concept_uri = mar[f"Glossaire_{term}"]
    
    g.add((concept_uri, RDF.type, SKOS.Concept))
    g.add((concept_uri, SKOS.prefLabel, Literal(term, lang="fr")))
    g.add((concept_uri, SKOS.definition, Literal(definition_text, lang="fr")))
```

**Résultat du step** :
- **8 individus Interdiction** (2 remplis, 6 vides)
- **5 individus Zone**
- **15+ individus SourceJuridique**
- **127+ concepts SKOS** (définitions + glossaire)
- **~600 nouveaux triplets ajoutés**

---

### **STEP 5 : Export multi-format**

**Objectif** : Générer l'ontologie dans 4 formats pour différents usages

#### 5.1 - Turtle Format (TTL)
```
Format : Turtle (Terse RDF Triple Language)
Fichier : maritime_ontology.ttl
Objectif : Lisible par humains, format principal pour développement
Exemple :
```

```turtle
PREFIX mar: <http://www.maritime-ontology.org/mar#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

mar:InterdictionChalutagedefond
  a mar:Interdiction ;
  rdfs:label "Interdiction du Chalutage de Fond en Haute Mer"@fr ;
  skos:definition "Norme juridique internationale prohibant le chalutage de fond en haute mer..."@fr ;
  mar:appliesInZone mar:HM ;
  mar:concerneActeur mar:Acteur_EtatPavillon ;
  mar:fondeeSur mar:Res61_105 .
```

#### 5.2 - OWL/RDF-XML Format
```
Format : RDF/XML (OWL 2.0 compliant)
Fichier : maritime_ontology.owl
Objectif : Ouverture dans Protégé, éditeurs ontologiques
Avantage : Format standard, validation OWL2
Exemple :
```

```xml
<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:owl="http://www.w3.org/2002/07/owl#"
         xmlns:mar="http://www.maritime-ontology.org/mar#">
  
  <rdf:Description rdf:about="http://www.maritime-ontology.org/mar#InterdictionChalutagedefond">
    <rdf:type rdf:resource="http://www.maritime-ontology.org/mar#Interdiction"/>
    <rdfs:label xml:lang="fr">Interdiction du Chalutage de Fond...</rdfs:label>
  </rdf:Description>
</rdf:RDF>
```

#### 5.3 - JSON-LD Format
```
Format : JSON-LD (JSON Linked Data)
Fichier : maritime_ontology.jsonld
Objectif : APIs web, intégration JavaScript, REST APIs
Avantage : Compact, navigable par JSON parsers
Exemple :
```

```json
{
  "@context": {
    "mar": "http://www.maritime-ontology.org/mar#",
    "skos": "http://www.w3.org/2004/02/skos/core#"
  },
  "@graph": [
    {
      "@id": "mar:InterdictionChalutagedefond",
      "@type": "mar:Interdiction",
      "rdfs:label": {"@language": "fr", "@value": "Interdiction du..."},
      "skos:definition": "..."
    }
  ]
}
```

#### 5.4 - N-Triples Format
```
Format : N-Triples (RDF triplets simples)
Fichier : maritime_ontology.nt
Objectif : Échange de données brutes, streaming RDF
Avantage : Fineline, ligne = triplet
Exemple :
```

```
<http://www.maritime-ontology.org/mar#InterdictionChalutagedefond> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.maritime-ontology.org/mar#Interdiction> .
<http://www.maritime-ontology.org/mar#InterdictionChalutagedefond> <http://www.w3.org/2000/01/rdf-schema#label> "Interdiction du Chalutage de Fond"@fr .
```

**Résultats du step** :
- 4 fichiers générés
- Vérification intégrité RDF (parsing validation)
- Tailles environ 1400-1600 lignes chacun

---

### **STEP 6 : Questions de compétence SPARQL**

**Objectif** : Valider que l'ontologie répond aux besoins de recherche

**12 Questions de Compétence** :

| CQ# | Question | Type | Utilité RAG |
|-----|----------|------|------------|
| CQ1 | Lister toutes les interdictions | List | Base : retrouver toutes les normes |
| CQ2 | Quels acteurs concernent I001 ? | Filter | RAG : "qui est affecté ?" |
| CQ3 | Dans quelles zones s'applique I002 ? | Navigate | RAG : "où ça s'applique ?" |
| CQ4 | Quelles exceptions à I001 ? | Drill | RAG : "quand ça ne s'applique pas ?" |
| CQ5 | Trouver tous les concepts SKOS | List | RAG : vocabulaire |
| CQ6 | Hiérarchie d'une classe (ex: NavirePeche) | Hierarchy | RAG : taxonomie |
| CQ7 | Sources juridiques pour I002 | Reference | RAG : références légales |
| CQ8 | Interdictions par zone | Inverse | RAG : filtrer par zone |
| CQ9 | Espèces protégées | Domain | RAG : conservation |
| CQ10 | Activités interdites | Domain | RAG : restrictions opérationnelles |
| CQ11 | Périodes d'application | Time | RAG : conditions temporelles |
| CQ12 | Graphe complet d'une interdiction | Traverse | RAG : contexte complet |

**Exemple : CQ1 (Lister toutes les interdictions)** :
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX mar: <http://www.maritime-ontology.org/mar#>

SELECT ?interdiction ?label
WHERE {
  ?interdiction rdf:type mar:Interdiction .
  ?interdiction rdfs:label ?label .
}
```

**Résultat attendu** :
```
interdiction                                                      | label
──────────────────────────────────────────────────────────────────┼────────────────────────────────────
http://www.maritime-ontology.org/mar#InterdictionChalutagedefond | Interdiction du Chalutage de Fond
http://www.maritime-ontology.org/mar#InterdictionChassBaleine    | Interdiction de la Chasse Baleine
http://www.maritime-ontology.org/mar#InterdictionFiletsMaillants | Interdiction des Filets Maillants
... (6 autres)
```

**Résultat du step** :
- 12 requêtes exécutées
- Résultats sauvegardés en JSON
- Rapport de compétence généré

---

### **STEP 7 : Export Neo4j**

**Objectif** : Préparer les données pour une visualisation graphique avancée

**Processus** :

#### 7.1 - Construction du graphe de nœuds et arêtes
```python
def build_graph_data(g: Graph):
    nodes = {}  # URI → {properties}
    edges = []  # [(subject_id, predicate, object_id), ...]
    
    for s, p, o in g:
        # Créer nœud pour subject
        if s not in nodes:
            nodes[s] = {
                "uri": str(s),
                "type": infer_type(s, g),
                "labels": extract_labels(s, g)
            }
        
        # Créer nœud pour objet (si URI)
        if isinstance(o, URIRef) and o not in nodes:
            nodes[o] = {
                "uri": str(o),
                "type": infer_type(o, g),
                "labels": extract_labels(o, g)
            }
        
        # Ajouter arête
        if isinstance(o, URIRef):
            edges.append((str(s), str(p), str(o)))
    
    return nodes, edges
```

#### 7.2 - Génération du script Cypher
```cypher
// Créer les nœuds
CREATE (n:Interdiction {
  uri: "http://www.maritime-ontology.org/mar#InterdictionChalutagedefond",
  label: "Interdiction du Chalutage de Fond",
  confidence: 1.0
})

CREATE (z:Zone {
  uri: "http://www.maritime-ontology.org/mar#HM",
  label: "Haute Mer"
})

// Créer les relations
CREATE (n)-[:APPLIES_IN_ZONE]->(z)
```

#### 7.3 - Options d'import

**Option A : Import direct (si Neo4j en local)** :
```bash
# Dans Neo4j Browser
:play neo4j_import.cypher
```

**Option B : Script à exécuter** :
```bash
# Via Cypher-Shell
cypher-shell -u neo4j -p password < neo4j_import.cypher
```

**Résultat du step** :
- Script Cypher généré : `neo4j_import.cypher`
- Prêt pour visualisation graphique
- Requêtes Neo4j possibles sur l'ontologie

---

### **STEP 8 : Rapport final**

**Objectif** : Générer un résumé complet de l'exécution

**Contenu du rapport** (`ontology_report.json`) :

```json
{
  "timestamp": "2026-04-14T16:45:41.234567",
  "version": "1.0.0",
  "stats": {
    "total_triples": 1022,
    "classes": 57,
    "object_properties": 20,
    "data_properties": 11,
    "individuals": 111,
    "sparql_questions_run": 12
  },
  "output_files": {
    "ttl": "data/output/maritime_ontology.ttl",
    "owl": "data/output/maritime_ontology.owl",
    "jsonld": "data/output/maritime_ontology.jsonld",
    "nt": "data/output/maritime_ontology.nt",
    "cypher": "data/output/neo4j_import.cypher"
  },
  "interdictions": {
    "I001": {
      "label": "Interdiction du Chalutage de Fond",
      "confidence": 1.0,
      "zones": 3,
      "acteurs": 3,
      "exceptions": 2,
      "sources": 4
    },
    "I002": {
      "label": "Interdiction de la Chasse Baleine",
      "confidence": 1.0,
      "zones": 4,
      "acteurs": 4,
      "exceptions": 2,
      "especes": 4
    },
    "I003-I008": {
      "status": "Templates vides - Prêts pour population",
      "confidence": 0.0,
      "needs_review": true
    }
  }
}
```

**Affichage terminal du résumé** :
```
[OK] PIPELINE TERMINE
[TRIPLETS] Total : 1022
[CLASSES] OWL : 57
[PROPS_OBJ] Proprietes objet : 20
[PROPS_DATA] Proprietes donnees : 11
[INDIVIDUALS] Individus : 111
[FILES] Fichiers generes :
   [TTL    ] data/output/maritime_ontology.ttl
   [OWL    ] data/output/maritime_ontology.owl
   [JSONLD ] data/output/maritime_ontology.jsonld
   [NT     ] data/output/maritime_ontology.nt
   [CYPHER ] data/output/neo4j_import.cypher
```

---

## Format des données

### Configuration YAML (`data/config/interdictions.yaml`)

Chaque interdiction est définie comme :

```yaml
- id: "I001"
  label_fr: "Interdiction du Chalutage de Fond en Haute Mer"
  label_en: "Prohibition of Deep-Sea Bottom Trawling on the High Seas"
  type_activite: "CHALUTAGE_FOND"
  deontic_type: "Prohibition"
  legal_layer: "International"
  confidence: 1.0
  needs_review: false
  
  zones:
    - "HAUTE_MER"
    - "ZONE_HorsJuridiction"
    - "ECOSYSTEME_VULNERABLES"
  
  acteurs:
    - id: "Acteur_EtatPavillon"
      label: "États du Pavillon"
      type: "EtatPavillon"
    - id: "Acteur_OrgRegionalPeche"
      label: "Organismes régionaux de gestion des pêches"
      type: "OrganisationInternationale"
  
  periodes:
    - id: "Periode_AbsenceEvaluation"
      label: "En l'absence d'évaluations scientifiques"
      type: "ConditionnelJusquA"
  
  exceptions:
    - id: "Exception_EtatsDeveloppement"
      label: "Besoins particuliers des États en développement"
      source_ref: "A/RES/61/105 §121"
  
  controles:
    - id: "Controle_EvaluationScientifique"
      label: "Évaluation d'impact sur écosystèmes marins vulnérables"
  
  documents:
    - doc_id: "Res61_105"
      title: "Résolution AG-ONU 61/105"
      year: 2006
      reference: "A/RES/61/105"
      type: "ResolutionAGONU"
```

### Données JSON brutes (`data/raw/*.json`)

Trois types de données extraites par LLM :

1. **Définitions** : Termes clés extraits de conventions
2. **Glossaire** : Vocabulaire technique
3. **Triplets** : Relation (subject, predicate, object)

---

## Sorties générées

### Fichiers d'ontologie

| Fichier | Format | Taille | Usage |
|---------|--------|--------|-------|
| maritime_ontology.ttl | Turtle | ~1400 lignes | Développement, lisibilité |
| maritime_ontology.owl | OWL/RDF-XML | ~1600 lignes | Protégé, validation OWL |
| maritime_ontology.jsonld | JSON-LD | ~1500 lignes | APIs web, REST |
| maritime_ontology.nt | N-Triples | ~1450 lignes | Streaming, échange |

### Fichiers de requêtes

| Fichier | Contenu | Usage |
|---------|---------|-------|
| sparql_results.json | 12 résultats CQ | Validation compétences |
| sparql_report.txt | Rapport formaté | Audit lisible |

### Fichiers de graphe

| Fichier | Contenu | Usage |
|---------|---------|-------|
| neo4j_import.cypher | ~200 commandes | Import Neo4j |
| ontology_report.json | Statistiques | Suivi d'exécution |

---

## Exemple d'exécution

### Commande de lancement

```bash
cd /path/to/version_1_Ontologie
python main.py
```

### Sortie console

```
[04/14/26 16:45:41] INFO     =================================== 
                             ==============================                     
                    INFO       MARITIME ONTOLOGY PIPELINE --     
                             LKIF-Core Aligned                                  
                    INFO       Prototype : I001 + I002                  
                    INFO     =================================== 
                             ==============================                     

STEP 1 -- Import du stub LKIF-Core
  [OK] LKIF-Core importe depuis : data/input/lkif_stub.ttl

STEP 2 -- Construction du schema OWL
  [OK] 57 classes creees
  [OK] 20 proprietes objet
  [OK] 11 proprietes donnees

STEP 3 -- Chargement des donnees
  [OK] 24 definitions chargees
  [OK] 103 termes glossaire
  [OK] 55 triplets IA

STEP 4 -- Population des individus
  [ZONES] 5 zones creees
  [SOURCES] 15 sources juridiques creees
  [OK] I001 : InterdictionChalutagedefond
  [OK] I002 : InterdictionChassBaleine
  [OK] I003-I008 : Templates vides
  [AI] 55 triplets IA integres
  [LEXICAL] 127 concepts lexicaux crees

STEP 5 -- Export des fichiers ontologiques
  [OK] TTL  -> data/output/maritime_ontology.ttl
  [OK] OWL  -> data/output/maritime_ontology.owl
  [OK] JSON-LD -> data/output/maritime_ontology.jsonld
  [OK] N-Triples -> data/output/maritime_ontology.nt

STEP 6 -- Questions de competence SPARQL
  [CQ1 ] Lister toutes les interdictions : 8 resultats
  [CQ2 ] Acteurs concernés : 12 resultats
  [CQ3 ] Zones d'application : 15 resultats
  [CQ11] Hiérarchie des classes : 5 resultats
  [OK] 12 SPARQL CQ executees

STEP 7 -- Export Neo4j
  [OK] Script Cypher -> data/output/neo4j_import.cypher

STEP 8 -- Rapport final
  [OK] Rapport JSON -> data/output/ontology_report.json

=================================== 
  [OK] PIPELINE TERMINE
  [TRIPLETS] Total : 1022
  [CLASSES] OWL : 57
  [PROPS_OBJ] Proprietes objet : 20
  [PROPS_DATA] Proprietes donnees : 11
  [INDIVIDUALS] Individus : 111
  [FILES] Fichiers generes :
     [TTL    ] data/output/maritime_ontology.ttl
     [OWL    ] data/output/maritime_ontology.owl
     [JSONLD ] data/output/maritime_ontology.jsonld
     [NT     ] data/output/maritime_ontology.nt
     [CYPHER ] data/output/neo4j_import.cypher
===================================
```

---

## Flux RAG

### Intégration avec un système RAG

L'ontologie générée supporte un **système RAG** (Retrieval-Augmented Generation) via un cycle de 3 phases :

```
┌─────────────────────────────────────────────────────────────┐
│                 RAG Pipeline (Retrieval)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PHASE 1: INDEXATION                                        │
│  ├─ Parser maritime_ontology.ttl ou .owl                  │
│  ├─ Créer un index SPARQL (Fuseki/OWLIM)                 │
│  └─ Pré-calculer les embeddings SKOS                      │
│                                                             │
│  PHASE 2 : REQUÊTE UTILISATEUR                             │
│  ├─ Utilisateur : "Quelles zones sont affectées par       │
│  │               l'interdiction du chalutage ?"            │
│  ├─ Conversion en SPARQL query                             │
│  └─ Exécution sur l'index                                 │
│                                                             │
│  PHASE 3 : CONTEXTE POUR LLM                               │
│  ├─ Résultats SPARQL →Embeddings                          │
│  ├─ Top-K nodes pertinents triés                          │
│  └─ Injection dans le prompt du LLM generatif             │
│     pour augmenter la réponse                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Exemple full RAG

**Requête utilisateur** :
> "Quelles sont les exceptions pour le chalutage de fond ?"

**Conversion SPARQL automatique** :
```sparql
PREFIX mar: <http://www.maritime-ontology.org/mar#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?exception ?label
WHERE {
  mar:InterdictionChalutagedefond mar:aException ?exception .
  ?exception rdfs:label ?label .
}
```

**Résultats du triple store** :
```
exception UUID | label
───────────────┼─────────────────────────────────────
mar:Exception_EtatsDeveloppement | Besoins particuliers des États en développement
mar:Exception_MesuresConservation | Si mesures de conservation et gestion adoptées
```

**Contexte injecté au LLM** :
```
Faits pertinents du graphe RDF:
- Interdiction : InterdictionChalutagedefond
- Zone : Haute Mer (UNCLOS Art. 86)
- Exceptions trouvées :
  1. Exception_EtatsDeveloppement: "Besoins particuliers des États..."
  2. Exception_MesuresConservation: "Si mesures de conservation..."
- Sources juridiques : A/RES/61/105, A/RES/64/72, A/RES/66/68, A/RES/71/123

Question utilisateur: Quelles sont les exceptions pour le chalutage de fond ?
```

**Réponse LLM augmentée** :
> "Selon l'ontologie maritime, l'interdiction du chalutage de fond en haute mer 
> comporte deux exceptions principales, fondées sur les Résolutions AG-ONU :
> 
> 1. **Exception pour États en développement** (A/RES/61/105 §121)
>    - Les États ayant des besoins particuliers...
> 
> 2. **Exception pour mesures de conservation** (A/RES/64/72 §119b)
>    - Si des mesures adéquates sont adoptées..."

---

## Conclusion

Le pipeline maritime est un **système d'orchestration complet** qui :

✅ **Transforme** les conventions internationales en ontologie structurée  
✅ **Valide** via SPARQL (12 question de compétence)  
✅ **Exporte** en 4 formats (TTL, OWL, JSON-LD, N-Triples)  
✅ **Supporte** les requêtes avancées pour RAG  
✅ **Visualise** dans Neo4j pour analyse graphique  
✅ **Extensible** pour 8 interdictions (2 en production, 6 en préparation)  

---

**Prochaines étapes** :
1. Remplir les templates I003-I008 avec données réelles
2. Valider avec experts du droit maritime
3. Intégrer avec système RAG (LLM + Embedding)
4. Déployer dans environnement de production

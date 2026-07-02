# 📖 Guide d'Utilisation et d'Extension de l'Ontologie Maritime

## 🔍 Question 1 : "Je ne trouve pas les 24 définitions dans Protégé"

### ✅ Les définitions EXISTENT dans le fichier OWL

Les 24 définitions sont bien générées dans `maritime_ontology.owl` :
- **Format** : SKOS Concepts (`skos:Concept`)
- **Localisation** : Namespace `http://www.maritime-ontology.org/mar#`
- **Naming** : `Glossaire_*` (exemple: `mar:Glossaire_Chalutage`)

### 🔧 Comment les afficher dans Protégé ?

#### Méthode 1 : Chercher par SPARQL (recommandé)
```
1. Ouvrir maritime_ontology.owl dans Protégé
2. Menu : "Window" → "SPARQL Query"
3. Copier cette requête :

PREFIX mar: <http://www.maritime-ontology.org/mar#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?concept ?label ?definition WHERE {
  ?concept a mar:ConceptLexical ;
           skos:prefLabel ?label ;
           skos:definition ?definition .
}
ORDER BY ?label
```

#### Méthode 2 : Activer la vue "Ontologie"
```
1. Ouvrir maritime_ontology.owl
2. Menu : "View" → "Class hierarchy"
3. Chercher la classe "ConceptLexical"
4. Les concepts sont listés dessous comme instances (individuals)
```

#### Méthode 3 : RDFlib (en Python)
```python
from rdflib import Graph, Namespace, SKOS, RDF
g = Graph()
g.parse("maritime_ontology.owl")

MAR = Namespace("http://www.maritime-ontology.org/mar#")

# Trouver tous les concepts lexicaux
concepts = list(g.subjects(RDF.type, MAR.ConceptLexical))
print(f"Nombre de concepts : {len(concepts)}")

# Afficher les définitions
for concept in concepts[:5]:
    labels = list(g.objects(concept, SKOS.prefLabel))
    definitions = list(g.objects(concept, SKOS.definition))
    print(f"\n{concept}")
    for label in labels:
        print(f"  Label: {label}")
    for defn in definitions:
        print(f"  Definition: {defn}")
```

### ⚠️ Pourquoi Protégé ne les affiche pas en vue graphique ?

Protégé affiche par défaut les **classes OWL** et leurs **individus nommés**. Les concepts SKOS sont techniquement des individus, mais rangés dans le namespace SKOS qui est moins visible. C'est normal et volontaire en ontologie moderne.

---

## 🎯 Question 2 : "Mon modèle est ouvert aux modifications ?"

### ✅ OUI ! Le modèle est **100% extensible**

#### 1️⃣ Ajouter une NOUVELLE INTERDICTION

**Fichier à éditer** : `data/config/interdictions.yaml`

```yaml
interdictions:
  # Interdictions existantes (I001, I002)
  - id: "I001"
    labels: {"fr": "Chalutage de fond"}
    # ...
  
  # NOUVELLE INTERDICTION : Exemple
  - id: "I003"
    labels:
      fr: "Pêche aux engins explosifs"
      en: "Fishing with explosives"
    description: "Interdiction de l'utilisation d'explosifs pour la pêche"
    deontic_type: "Prohibition"
    zones: ["HM", "EEZ"]  # Références aux zones existantes
    activities: ["Peche_Explosifs"]  # À créer ou référencer
    actors: ["ETAT", "ORGP"]  # Références existantes
    exceptions: []
    legal_sources: ["UNCLOS_1982"]
    species: ["Baleine", "Dauphin"]
```

**Puis relancer le pipeline** :
```bash
python main.py
```

✅ La nouvelle interdiction I003 sera automatiquement créée avec :
- 111+ triplets additionnels
- Relations vers zones, acteurs, activités
- Couche lexicale
- Export dans tous les formats (TTL, OWL, JSON-LD)

#### 2️⃣ Ajouter de NOUVELLES ZONES

Éditer `src/maritime_ontology/populator.py`, méthode `populate_zones()` :

```python
def populate_zones(self) -> None:
    zones = [
        # Zones existantes : HM, EEZ, MT, SM, ZEV
        
        # NOUVELLE ZONE : Exemple
        {
            "id": "ZCC",
            "type": "ZoneCorailsCommunautaires",
            "labels": {"fr": "Zone Récifs de Corail", "en": "Coral Reef Zone"},
            "description": "Zone de protection des écosystèmes coraliens fragiles"
        }
    ]
```

Puis relancer : `python main.py`

#### 3️⃣ Ajouter de NOUVELLES ACTIVITÉS

Éditer `src/maritime_ontology/populator.py`, ajouter une méthode :

```python
def populate_activities(self) -> None:
    activities = [
        {
            "id": "Peche_Explosifs",
            "type": "ActivitePeche",
            "labels": {"fr": "Pêche aux explosifs", "en": "Explosive Fishing"},
            "description": "Utilisation d'explosifs pour capturer le poisson"
        },
        # Ajouter d'autres activités...
    ]
    
    for activity in activities:
        self.create_activity(
            activity["id"],
            activity["type"],
            activity["labels"],
            activity["description"]
        )
```

Appeler dans `step_populate()` :
```python
pop.populate_activities()  # Ajouter cette ligne
```

#### 4️⃣ Ajouter de NOUVEAUX ACTEURS

Éditer `src/maritime_ontology/populator.py`, ajouter :

```python
def populate_actors(self) -> None:
    actors = [
        {
            "id": "CITES",
            "type": "OrganisationInternationale",
            "labels": {"fr": "CITES", "en": "Convention on International Trade in Endangered Species"}
        }
    ]
    
    for actor in actors:
        actor_uri = self.mar[actor["id"]]
        actor_class = getattr(self.mar, actor["type"], self.mar.Acteur)
        self.g.add((actor_uri, RDF.type, actor_class))
        self.g.add((actor_uri, RDF.type, OWL.NamedIndividual))
        
        for lang, label in actor["labels"].items():
            self.g.add((actor_uri, RDFS.label, Literal(label, lang=lang)))
        
        self.created_individuals.append(str(actor_uri))
```

---

## 📋 Architecture d'Extension : Diagramme

```
ONTOLOGIE MARITIME
│
├── SCHÉMA (schema.py) — Définit les classes OWL
│   ├── Classes : Interdiction, Zone, Activité, Acteur, etc.
│   └── Propriétés : appliesInZone, concerneActivite, etc.
│
├── CONFIGURATION (data/config/interdictions.yaml) — Données métier
│   ├── I001, I002, I003... (facilement extensible)
│   └── Références vers zones, acteurs, activités
│
├── POPULATION (populator.py) — Crée les individus
│   ├── populate_zones() → 5 zones (extensible)
│   ├── populate_sources_juridiques() → Depuis config
│   ├── integrate_ai_triples() → 55 triplets IA
│   ├── populate_lexical_layer() → 127 concepts lexicaux
│   └── À ajouter : populate_actors(), populate_activities()
│
└── EXPORT (pipeline.py → data/output/) — 5 formats
    ├── maritime_ontology.ttl (Turtle)
    ├── maritime_ontology.owl (OWL/RDF-XML)
    ├── maritime_ontology.jsonld (JSON-LD)
    ├── maritime_ontology.nt (N-Triples)
    └── neo4j_import.cypher (Neo4j)
```

---

## 🔒 Points de Verrouillage (Pas d'extension recommandée)

Ces parties du schéma NE doivent PAS être modifiées directement (c'est du code, pas de la config) :

❌ `schema.py` → Hiérarchie de classes OWL
❌ `pipeline.py` → Orchestration des étapes
❌ `sparql_runner.py` → Requêtes SPARQL

✅ TOUT LE RESTE est extensible !

---

## 📊 Contrôle de Version

Pour tracker les modifications à votre ontologie :

```bash
# Initialiser Git (si pas déjà fait)
git init
git add .
git commit -m "Initial: Maritime Ontology v1.0 - 2 interdictions, 111 individus"

# Après ajout d'une interdiction I003
python main.py
git add data/output/
git commit -m "Add interdiction I003: Explosive fishing"
git tag -a v1.1 -m "Version 1.1: +1 interdiction, +50 triplets"
```

---

## 🎓 Exemple Complet : Ajouter I003

### Étape 1 : Éditer data/config/interdictions.yaml
```yaml
interdictions:
  - id: "I001"
    # ... existant
  - id: "I002"
    # ... existant
  
  # NOUVELLE INTERDICTION
  - id: "I003"
    labels:
      fr: "Pêche aux engins explosifs"
      en: "Explosive Fishing"
    description: "Interdiction de l'utilisation d'engins explosifs pour la pêche"
    deontic_type: "Prohibition"
    zones: ["HM", "EEZ", "SM"]
    activities: []  # À créer dans populate_activities()
    actors: ["Etat", "ORGP"]
    exceptions: ["Exception_Recherche_Scientifique"]
    legal_sources: ["UNCLOS_1982", "US_Law_Marine_Mammal_Protection"]
    species: ["Cetaces", "Poissons_Demersaux"]
```

### Étape 2 : Relancer le pipeline
```bash
python main.py
```

### Résultat attendu :
```
[OK] PIPELINE TERMINE
[TRIPLETS] Total : 1200+ (augmentation)
[INDIVIDUALS] Individus : 120+ (augmentation)
```

### Étape 3 : Vérifier dans Protégé
```
1. Ouvrir maritime_ontology.owl
2. Chercher "I003" dans la classe Interdiction
3. Voir les relations : appliesInZone, concerneActeur, etc.
```

---

## 🚀 Résumé : Extensibilité

| Défi | Difficulté | Solution |
|------|-----------|----------|
| Ajouter 1 interdiction | ⭐ Très facile | Éditer `interdictions.yaml` |
| Ajouter zone / acteur | ⭐⭐ Facile | Editer `populator.py` |
| Ajouter classe OWL | ⭐⭐⭐ Modéré | Éditer `schema.py` |
| Ajouter propriété OWL | ⭐⭐⭐⭐ Expert | Éditer `schema.py` + restrictions |

**Votre modèle est 100% ouvert à l'extension!** 🎉

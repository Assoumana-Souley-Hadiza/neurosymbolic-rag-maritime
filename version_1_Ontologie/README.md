# 🌊 Maritime Ontology — Droit International de la Mer

Prototype d'ontologie juridique maritime alignée sur **LKIF-Core** couvrant :
- 🚫 **Interdictions** (Chalutage de Fond, Chasse à la Baleine)
- 📍 **Zones géographiques** (Haute Mer, ZEE, ZecoVul, etc.)
- 👥 **Acteurs** (États, Organisations, Navires)
- 🎯 **Activités** (Pêche, Chasse)
- ⚖️ **Cadre juridique** basé sur le droit maritime international

---

## 📁 Structure du Projet

```
maritime_ontology/
├── src/maritime_ontology/        # Code métier
│   ├── main.py                   # Point d'entrée CLI
│   ├── pipeline.py               # Orchestrateur principal
│   ├── schema.py                 # Construction OWL (classes, propriétés)
│   ├── loader.py                 # Chargement des données JSON
│   ├── populator.py              # Population des individus
│   ├── neo4j_export.py           # Export vers Neo4j
│   └── sparql_runner.py          # Questions de compétence
├── tests/
│   └── test_ontology.py          # Tests unitaires
├── data/
│   ├── config/
│   │   ├── settings.yaml         # Configuration globale
│   │   └── interdictions.yaml    # Définitions des interdictions
│   ├── input/
│   │   └── lkif_stub.ttl         # Stub LKIF-Core
│   ├── queries/
│   │   └── competency_questions.sparql
│   └── output/                   # Fichiers générés
├── docker-compose.yml            # Neo4j + Configuration
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## 🚀 Installation

### Prérequis
- Python 3.9+
- Neo4j 4.4+ (optionnel, pour l'export graphique)

### Setup
```bash
# 1. Clone/télécharge le projet
cd version_1_Ontologie

# 2. Crée un environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Installe les dépendances
pip install -r requirements.txt

# 4. (Optionnel) Lance Neo4j
docker-compose up -d
```

---

## 📖 Usage

### Pipeline complet
```bash
python -m maritime_ontology.main
```
Génère :
- ✅ Ontologie TTL/XML/JSON-LD
- ✅ Résultats SPARQL (questions de compétence)
- ✅ Script Cypher pour Neo4j
- ✅ Rapport d'execution

### Options CLI
```bash
# Questions de compétence SPARQL uniquement
python -m maritime_ontology.main --sparql-only

# Export Neo4j uniquement
python -m maritime_ontology.main --neo4j-only

# Validation OWL-RL
python -m maritime_ontology.main --validate

# Configuration personnalisée
python -m maritime_ontology.main --config path/to/settings.yaml
```

---

## 🔧 Configuration

### `data/config/settings.yaml`
```yaml
metadata:
  title: "Ontologie Maritime"
  version: "1.0.0"

namespaces:
  mar: "http://www.maritime-ontology.org/mar#"
  lkif: "http://www.estrellaproject.org/lkif-core/lkif-core.owl#"

output:
  dir: "data/output"
  formats: [turtle, xml, json-ld]

neo4j:
  uri: "bolt://localhost:7687"
  user: "neo4j"
  password: "maritime2024"

data:
  raw_dir: "data/raw"
```

### `data/config/interdictions.yaml`
Définit les interdictions avec :
- ✅ Deontic types (Prohibition, Permission, Obligation)
- ✅ Zones géographiques applicables
- ✅ Activités et acteurs concernés
- ✅ Exceptions juridiques
- ✅ Sources du droit

---

## 🧪 Tests

```bash
# Exécute tous les tests
pytest tests/

# Avec coverage
pytest tests/ --cov=src/maritime_ontology
```

---

## 📊 Sorties générées

| Format | Fichier | Description |
|--------|---------|-------------|
| TTL | `maritime_ontology.ttl` | Format Turtle (lisible) |
| XML | `maritime_ontology.owl` | OWL/RDF-XML (standard) |
| JSON-LD | `maritime_ontology.jsonld` | Format JSON-LD |
| Cypher | `maritime_ontology.cypher` | Script d'import Neo4j |
| Report | `report.txt` | Résultats SPARQL + stats |

---

## 🎯 Questions de Compétence

L'ontologie supporte 10 questions SPARQL :

| CQ | Question |
|----|----------|
| CQ1 | Quelles interdictions sont définies ? |
| CQ2 | Dans quelles zones s'applique une interdiction ? |
| CQ3 | Quelles activités sont interdites ? |
| CQ4 | Quels acteurs sont soumis à une interdiction ? |
| CQ5 | Quelles exceptions existent ? |
| CQ6 | Quelles espèces sont protégées ? |
| CQ7 | Quelle est la base juridique ? |
| CQ8 | Quels contrôles s'appliquent ? |
| CQ9 | Pendant quelle période ? |
| CQ10 | Quels concepts lexicaux sont définis ? |

---

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│     Data Extraction (JSON)      │
└──────────────┬──────────────────┘
               │
        ┌──────▼──────┐
        │   loader.py │
        └──────┬──────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼──┐  ┌────▼────┐  ┌─▼────────┐
│Schema│  │Populator│  │neo4j_exp.│
└───┬──┘  └────┬────┘  └─┬────────┘
    │          │        │
    └──────────┼────────┘
               │
        ┌──────▼──────┐
        │  RDF Graph  │
        │  (rdflib)   │
        └──────┬──────┘
               │
    ┌──────────┼──────────────┐
    │          │              │
┌───▼────┐  ┌──▼──┐  ┌────────▼───┐
│ Export │  │SPARQL│  │ Neo4j / DB │
│ TTL/OWL   │ CQ   │  │            │
└────────┘  └──────┘  └────────────┘
```

---

## 🔗 Alignement LKIF-Core

Mapping principal :
| Concept Maritime | LKIF-Core |
|-----------------|-----------|
| Interdiction | `lkif:Prohibition` |
| Zone | `lkif:Place` |
| Activité | `lkif:Act` |
| Acteur | `lkif:Agent` |
| Norme | `lkif:Norm` |

---

## 📚 Dépendances principales

- **rdflib 7.0+** — RDF/OWL parsing et sérialisation
- **owlrl 6.0+** — OWL-RL reasoner (inférence, validation)
- **pyyaml 6.0+** — Configuration YAML
- **neo4j 5.0+** — Export graphe de connaissances
- **rich 13.0+** — Affichage terminal coloré (optionnel)

---

## 🐛 Troubleshooting

### Erreur : "Module not found: maritime_ontology"
```bash
# Assure-toi d'être dans le bon répertoire
cd version_1_Ontologie
export PYTHONPATH=./src:$PYTHONPATH  # Unix/Mac
set PYTHONPATH=src;%PYTHONPATH%      # Windows
```

### Erreur Neo4j : "Connection refused"
```bash
# Vérifie que Neo4j est lancé
docker-compose ps
docker-compose up -d  # Redémarre si nécessaire
```

### Ontologie vide après exécution
Vérifier :
- ✅ `data/config/interdictions.yaml` existe et est valide
- ✅ `data/input/lkif_stub.ttl` est chargé
- ✅ Fichiers JSON bruts présents (si applicable)

---

## 📝 License

[À spécifier]

---

## 👨‍💻 Contribution

Pour proposer des améliorations :
1. Crée une branche `feature/xxx`
2. Effectue tes changements
3. Ajoute des tests `tests/test_*.py`
4. Soumets une PR

---

## 📞 Contact

Maritime Legal Ontology Project
- 📧 contact@maritime-ontology.org
- 🔗 [Documentation LKIF-Core](http://www.estrellaproject.org/lkif-core/)

---

**Last updated:** April 2026

# 🏗️ ARCHITECTURE V3 - IMPROVEMENTS & RESTRUCTURATION

## 📋 Résumé des Changements

Cette version 3 apporte des améliorations majeures en **sécurité**, **observabilité**, **robustesse** et **structure** du projet.

---

## 🔐 Phase 1: SÉCURITÉ & VERSIONING

### ✅ Secrets Sécurisés
- **Ancien** : `password: "nawras2026"` en dur dans `config.py`
- **Nouveau** : Variables d'environnement via `.env.local`
- **Fichier** : `.env.local` (ignoré git, non commité)

```python
# config.py (nouveau)
from dotenv import load_dotenv

NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
if not NEO4J_PASSWORD:
    raise ValueError("❌ NEO4J_PASSWORD manquante")
```

### ✅ Versioning des Embeddings & Indexes
- **Ancien** : `CHROMA_DB_DIR = OUTPUT_DIR / "chroma_db"` (statique)
- **Nouveau** : `CHROMA_DB_DIR = ... / f"chroma_db_{EMBEDDING_VERSION}"` (versionnée)

```python
EMBEDDING_VERSION = "bge-m3-v1"  # Changer quand upgrade du modèle
BM25_VERSION = "bm25-v1"

# Nouvelle structure
data/processed/embeddings/chroma_db_bge-m3-v1/
data/processed/indexes/bm25_bm25-v1/
```

**Bénéfice** : Rollback facile si changement de modèle

---

## 📊 Phase 2: OBSERVABILITÉ

### ✅ Logging Structuré
```python
# config.py (nouveau)
LOGGING_CONFIG = {
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 10485760,  # 10MB rotation
            "backupCount": 5,
        },
        "console": {...}
    }
}
```

**Bénéfice** : Logs structurés, rotatifs, avec timestamps précis

### ✅ Métriques de Performance
**Nouveau module** : `rag/utils/metrics.py`

```python
from rag.utils.metrics import get_metrics_logger

metrics = get_metrics_logger(OUTPUT_DIR)
metrics.log_query(
    query="Quelles conventions...",
    intent="factual",
    weights={"dense": 0.4, "sparse": 0.3, "graph": 0.3},
    sources_retrieved={"dense": 5, "sparse": 5, "graph": 3},
    top_scores={"dense": 0.92, "sparse": 0.85, "graph": 0.78},
    response_time_ms=2154,
)

# Export
metrics.export_json("metrics_2025-05-04.json")
metrics.export_csv("metrics_2025-05-04.csv")
```

**Bénéfice** : Analyse offline des performances, détection d'anomalies

### ✅ Versioning des Modèles
**Nouveau module** : `rag/utils/versioning.py`

```python
from rag.utils.versioning import get_version_manager

vm = get_version_manager(OUTPUT_DIR)
vm.save_embedding_version(
    version="bge-m3-v1",
    model_name="BAAI/bge-m3",
    model_version="1.0",
    embedding_dim=1024,
    num_documents=1250,
)
```

**Bénéfice** : Traçabilité complète des modèles utilisés

---

## 🆘 Phase 3: ROBUSTESSE

### ✅ Health Check Intégré
**Nouveau module** : `rag/utils/health_check.py`

```python
from rag.utils.health_check import get_health_check

health = get_health_check()
health.full_check()  # Vérifie tous les composants

print(health.print_report())
# ✅ dense: OK
# ❌ neo4j: ERREUR
# 🟡 graph: Dégradé (RDF fallback)
# ✅ ollama: OK
```

**Bénéfice** : Diagnostic rapide des défaillances

### ✅ Graceful Degradation Neo4j
**Nouveau module** : `rag/integration/neo4j_bridge_safe.py`

```python
from rag.integration.neo4j_bridge_safe import get_safe_bridge

bridge = get_safe_bridge()
# Si Neo4j down → bascule automatique vers RDFLib
# Si RDF down → retourne [] (no crash)
results = bridge.retrieve(query)  # Toujours disponible
```

**Flux**:
```
Query → [Neo4j Bridge disponible?]
         ├─ Yes → retrieve via Neo4j
         └─ No  → fallback RDFLib
                  ├─ Yes → retrieve via RDF
                  └─ No  → return []
```

**Bénéfice** : Zero downtime, système résilient

### ✅ Validation des Secrets
```python
# config.py (nouveau)
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
if not NEO4J_PASSWORD:
    print("❌ ERREUR: NEO4J_PASSWORD manquante dans .env.local")
    sys.exit(1)
```

**Bénéfice** : Erreur claire au démarrage, évite crashes en production

---

## 📁 Phase 4: RESTRUCTURATION DES RÉPERTOIRES

### Structure Ancienne ❌
```
rag/output/                    # Résultats
output/ontologie/              # Doublons?
RAG_data/                      # Données brutes
data/output/                   # Plus de doublons
```

### Structure Nouvelle ✅
```
project_root/
├── data/
│   ├── raw/                   # PDFs bruts, input
│   ├── processed/
│   │   ├── embeddings/
│   │   │   ├── chroma_db_bge-m3-v1/
│   │   │   └── versions.json
│   │   ├── indexes/
│   │   │   ├── bm25_bm25-v1/
│   │   │   └── versions.json
│   │   └── chunks/            # Textes chunked
│   ├── ontology/              # maritime_ontology.owl
│   └── config/                # settings.yaml, schemas
├── results/                   # Output final (logs, exports)
├── rag/                       # Code source
│   ├── core/
│   ├── ingestion/
│   ├── integration/
│   ├── api/
│   └── utils/                 # ✨ NOUVEAU (versioning, metrics, health)
├── docs/
├── .env.local                 # ✨ NOUVEAU (secrets, local only)
└── .gitignore                 # ✨ AMÉLIORÉ
```

**Avantages**:
- ✅ Clair et organisé (raw → processed → results)
- ✅ Facile à sauvegarder/synchroniser (data isolé)
- ✅ Versioning natif (embeddings_v1, embeddings_v2, etc.)
- ✅ Git-friendly (.env.local ignoré automatiquement)

---

## 📋 Checklist de Migration

### Pour les développeurs:
- [ ] Créer `.env.local` avec vos credentials Neo4j
- [ ] Installer `python-dotenv` : `pip install python-dotenv`
- [ ] Tester la nouvelle structure : `python -c "from rag.config import *; print('✅ Config OK')"`
- [ ] Tester le health check : `python -c "from rag.utils.health_check import get_health_check; get_health_check().full_check()"`

### Pour l'intégration CI/CD:
- [ ] Ajouter `NEO4J_PASSWORD` aux secrets GitHub Actions
- [ ] Mettre à jour les chemins de sauvegarde (data/ au lieu de rag/output/)
- [ ] Ajouter un test de health check avant le déploiement

### Pour la production:
- [ ] Configurer `.env.local` sur le serveur (sécurisé)
- [ ] Vérifier les permissions sur `data/processed/` (lecture/écriture)
- [ ] Tester le fallback Neo4j → RDF en arrêtant Neo4j temporairement
- [ ] Monitorer les logs dans `results/rag_system.log`

---

## 🚀 Utilisation Rapide

### 1. Configuration
```bash
# Créer le .env.local
echo "NEO4J_PASSWORD=your_password" > .env.local
```

### 2. Vérifier la santé
```python
from rag.utils.health_check import get_health_check

health = get_health_check()
health.full_check()
# Affiche le statut de tous les composants
```

### 3. Exporter les métriques
```python
from rag.utils.metrics import get_metrics_logger
from rag.config import OUTPUT_DIR

metrics = get_metrics_logger(OUTPUT_DIR)
metrics.export_json()  # Export JSON
metrics.export_csv()   # Export CSV
```

### 4. Vérifier les versions
```python
from rag.utils.versioning import get_version_manager
from rag.config import OUTPUT_DIR

vm = get_version_manager(OUTPUT_DIR)
print(vm.export_summary())
```

---

## 📊 Résumé des Améliorations

| Aspect | Avant | Après |
|--------|--------|---------|
| **Secrets** | En dur (risque) | Dotenv (.gitignore) ✅ |
| **Versioning** | Statique | Dynamique ✅ |
| **Logging** | Basique | Structuré + Rotation ✅ |
| **Métriques** | Aucune | Complètes (JSON/CSV) ✅ |
| **Observabilité** | Manuelle | Automatisée ✅ |
| **Résilience** | Crash on Neo4j down | Graceful degradation ✅ |
| **Structure dossiers** | Chaotique | Organisée ✅ |
| **Health Check** | Aucun | Complet ✅ |

---

## 🔗 Fichiers Modifiés/Créés

### Créés
- ✨ `rag/utils/versioning.py` - Gestion des versions
- ✨ `rag/utils/metrics.py` - Métriques de performance
- ✨ `rag/utils/health_check.py` - Vérification santé système
- ✨ `rag/utils/__init__.py` - Module utils
- ✨ `rag/integration/neo4j_bridge_safe.py` - Wrapper Neo4j safe
- ✨ `.env.local` - Configuration locale (non commité)
- ✨ `data/raw/`, `data/processed/`, `results/` - Structure nouvelle

### Modifiés
- 🔄 `rag/config.py` - Dotenv, logging structuré, versioning, validation
- 🔄 `rag/api/app_streamlit.py` - Health check intégré, safe bridge
- 🔄 `rag/requirements.txt` - Ajout python-dotenv + requests
- 🔄 `.gitignore` - Ajout data/processed, .env.local, etc.

---

## ⚠️ Notes Importantes

### Backward Compatibility
- ✅ `rag/output/` toujours utilisé pour les logs (legacy)
- ✅ Ancienne API `Neo4jBridge` toujours disponible
- ✅ Structure données peut être migrée progressivement

### Migration Progressive
```python
# Ancienne API (toujours OK)
from rag.integration.neo4j_bridge import Neo4jBridge
bridge = Neo4jBridge.from_config()

# Nouvelle API (recommandée)
from rag.integration.neo4j_bridge_safe import get_safe_bridge
bridge = get_safe_bridge()  # Résistant aux pannes
```

---

## 📞 Support

Pour toute question sur cette architecture v3:
1. Vérifier `rag/utils/health_check.py` pour diagnostiquer
2. Consulter les logs dans `results/rag_system.log`
3. Exporter les métriques pour analyser les performances

**Merci d'avoir mis à jour vers l'architecture v3! 🚀**

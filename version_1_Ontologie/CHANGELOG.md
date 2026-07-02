# 📝 CHANGELOG - V3.0

## [3.0.0] - 2026-05-04

### ✨ NOUVELLES FONCTIONNALITÉS

#### Sécurité
- Secrets externalisés via `.env.local` (python-dotenv)
- Validation des credentials au démarrage
- `.env.local` automatiquement ignoré par git

#### Versioning
- Versioning des modèles d'embedding (bge-m3-v1, bge-m3-v2, etc.)
- Versioning des indexes BM25
- Métadonnées de versions dans `versions.json`
- Historique complet des versions

#### Observabilité
- Logging structuré avec rotation (10MB, 5 backups)
- Métriques de qualité retrieval (JSON + CSV)
- Export statistiques performances
- Health check système complète

#### Robustesse
- Graceful degradation Neo4j → RDFLib
- Zéro downtime en cas de panne composant
- Fallback automatique des retrievers
- Validation data paths au démarrage

#### Outils & Scripts
- `setup_v3.py` - Setup automatique
- `rag/utils/versioning.py` - Gestion versions
- `rag/utils/metrics.py` - Métriques performance
- `rag/utils/health_check.py` - Diagnostic système
- `rag/integration/neo4j_bridge_safe.py` - Wrapper résistant pannes

### 📁 RESTRUCTURATION

#### Répertoires
```
data/raw/                           # Input PDFs (nouveau)
data/processed/embeddings/          # ChromaDB versionnée (nouveau)
data/processed/indexes/             # BM25 versionnée (nouveau)
data/processed/chunks/              # Chunks textuels (nouveau)
results/                            # Logs + exports (nouveau)
rag/utils/                          # Utilitaires (nouveau)
```

#### Fichiers
- `.env.local` (nouveau)
- `.env.local.example` (nouveau)
- `setup_v3.py` (nouveau)
- `docs/ARCHITECTURE_V3.md` (nouveau)
- `docs/MIGRATION_GUIDE_V2_V3.md` (nouveau)

### 🔄 MODIFICATIONS

#### `rag/config.py`
- ✅ Ajout dotenv (python-dotenv)
- ✅ Logging structuré avec RotatingFileHandler
- ✅ Versioning EMBEDDING_VERSION, BM25_VERSION
- ✅ Validation NEO4J_PASSWORD obligatoire
- ✅ Chemins restructurés (data/processed/)

#### `rag/api/app_streamlit.py`
- ✅ Import health_check et metrics
- ✅ Neo4jBridgeSafe au lieu de Neo4jBridge
- ✅ Health check dans sidebar
- ✅ Affichage statut des 4 retrievers
- ✅ Timing capture pour métriques

#### `rag/requirements.txt`
- ✅ Ajout python-dotenv>=1.0.0
- ✅ Ajout requests>=2.31.0 (health check Ollama)
- ✅ Ajout neo4j>=5.0.0 (explicite)

#### `.gitignore`
- ✅ Ajout .env.local
- ✅ Ajout data/processed/embeddings/
- ✅ Ajout data/processed/indexes/
- ✅ Ajout results/
- ✅ Ajout rag/output/ (legacy)

### 📊 STATISTIQUES

| Métrique | Valeur |
|----------|--------|
| Fichiers créés | 9 |
| Fichiers modifiés | 6 |
| Lignes ajoutées | ~800 |
| Modules utils | 3 |
| Documentation pages | 2 |

### 🔐 SÉCURITÉ

- Credentials externalisés (NEO4J_PASSWORD, OLLAMA credentials)
- .env.local non commité
- Validation au démarrage
- Pas de hardcodes dans config.py

### ✅ COMPATIBILITÉ

- ✅ Rétro-compatible avec V2 (ancien code continue de marcher)
- ✅ Ancien répertoire `rag/output/` toujours accessible
- ✅ API `Neo4jBridge` toujours disponible (deprecated)
- ✅ Migration progressive possible

### 🚀 DÉPLOIEMENT

```bash
# Setup
python setup_v3.py

# Configuration
cp .env.local.example .env.local
# Éditer .env.local

# Test
streamlit run rag/api/app_streamlit.py
# Vérifier Health Check dans sidebar
```

### 📖 DOCUMENTATION

- `docs/ARCHITECTURE_V3.md` - Architecture complète
- `docs/MIGRATION_GUIDE_V2_V3.md` - Guide migration V2→V3
- `COMPLETION_SUMMARY.md` - Résumé du travail
- `.env.local.example` - Template configuration

### 🐛 BUGFIXES & AMÉLIORATIONS

- Logging sans crash si fichier inaccessible
- Health check non-bloquant
- Fallback Neo4j → RDF sans user interruption
- Validation paths au démarrage

### ⚠️ BREAKING CHANGES

Aucun. Version 3.0 est **100% rétro-compatible**.

---

## Guide de Mise à Jour

### Avant (V2):
```python
from rag.config import OUTPUT_DIR
from rag.integration.neo4j_bridge import Neo4jBridge

bridge = Neo4jBridge.from_config()  # Peut crash si Neo4j down
```

### Après (V3):
```python
from rag.config import configure_logging
from rag.integration.neo4j_bridge_safe import get_safe_bridge

configure_logging()  # Setup logging structuré
bridge = get_safe_bridge()  # Auto-fallback si Neo4j down
```

---

## Prochaines Versions (Roadmap)

### V3.1 (Optionnel)
- [ ] Auto-backup versioned indexes
- [ ] Métriques dans Prometheus
- [ ] Alertes email si composant down

### V3.2 (Optionnel)
- [ ] Dashboard Grafana
- [ ] A/B testing models
- [ ] Auto-archiving old versions

---

**Version**: 3.0.0  
**Date**: 2026-05-04  
**Status**: ✅ Production Ready

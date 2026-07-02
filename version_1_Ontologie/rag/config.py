"""
Configuration centralisée pour le système RAG Maritime v3.

Nouvelles fonctionnalités:
  - Secrets via .env.local (dotenv)
  - Versioning des embeddings et indexes
  - Logging structuré avec rotation
"""
import os
import sys
import logging
import logging.config
from pathlib import Path
from dotenv import load_dotenv

# ═══════════════════════════════════════════════════════════════════
# CHARGER LES SECRETS DEPUIS .env.local
# ═══════════════════════════════════════════════════════════════════
PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env.local"
if ENV_FILE.exists():
    try:
        # Nettoyer le fichier .env des caractères null avant de le charger
        with open(ENV_FILE, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        content = content.replace('\x00', '')  # Supprimer les caractères null
        
        with open(ENV_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        load_dotenv(ENV_FILE)
    except Exception as e:
        print(f"⚠️  Erreur lors du chargement de .env.local: {e}")
else:
    print(f"⚠️  .env.local manquante: {ENV_FILE}")

# ═══════════════════════════════════════════════════════════════════
# RÉPERTOIRES
# ═══════════════════════════════════════════════════════════════════
RAG_DIR = Path(__file__).parent
RAG_DATA_DIR = PROJECT_ROOT / "RAG_data"

# Structure de données nouvelle (versionnée)
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Output (résultats)
OUTPUT_DIR = PROJECT_ROOT / "results"
RESULTS_DIR = OUTPUT_DIR

# Backward compatibility: utiliser rag/output pour les logs
LEGACY_OUTPUT_DIR = RAG_DIR / "output"

# Versioning des indexes
EMBEDDING_VERSION = os.getenv("EMBEDDING_VERSION", "bge-m3-v1")
BM25_VERSION = os.getenv("BM25_VERSION", "bm25-v1")

CHROMA_DB_DIR = LEGACY_OUTPUT_DIR / "chroma_db"
BM25_INDEX_DIR = LEGACY_OUTPUT_DIR / "bm25_index"
CHUNKS_DIR = LEGACY_OUTPUT_DIR / "chunks"

# Créer les répertoires s'ils n'existent pas
for d in [OUTPUT_DIR, LEGACY_OUTPUT_DIR, CHROMA_DB_DIR, BM25_INDEX_DIR, CHUNKS_DIR, DATA_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ─── Catégories RAG ──────────────────────────────────────────────
CATEGORIES = [
    "Baleine", 
    "Oiseaux marins", 
    "Rejet hydrocarbure", 
    "Chalutage de fond", 
    "Construction", 
    "Sable"
]

# ─── Configuration d'extraction PDF ─────────────────────────────
PDF_CONFIG = {
    "chunk_size": 800,              # tokens par chunk
    "chunk_overlap": 100,           # chevauchement entre chunks
    "min_chunk_length": 50,         # minimum de caractères par chunk
    "language": "french",
}

# ─── Configuration embedding ────────────────────────────────────
EMBEDDING_CONFIG = {
    "model_name": "BAAI/bge-m3",
    "device": "cpu",                # utiliser "cuda" si GPU disponible
    "embedding_dim": 1024,
}

# ─── Configuration ChromaDB ─────────────────────────────────────
CHROMA_CONFIG = {
    "persist_directory": str(CHROMA_DB_DIR),
    "is_persistent": True,
}

# ─── Logging ───────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = OUTPUT_DIR / "rag_system.log"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s | %(name)s | %(levelname)-8s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(levelname)s: %(message)s",
        }
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": LOG_LEVEL,
            "filename": str(LOG_FILE),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "detailed",
            "encoding": "utf-8",
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": LOG_LEVEL,
            "formatter": "detailed",
        }
    },
    "root": {
        "level": LOG_LEVEL,
        "handlers": ["file", "console"],
    },
}

# Configurer logging au démarrage
def configure_logging():
    """Applique la configuration de logging."""
    logging.config.dictConfig(LOGGING_CONFIG)

# ─── Extraction PDF ─────────────────────────────────────────────
EXTRACTION_CONFIG = {
    "ocr_enabled": False,           # OCR pour scans (lent, installer tesseract)
    "extract_tables": True,
    "extract_images": False,
    "timeout": 30,                  # secondes par PDF
}

# ─── Configuration LLM (Ollama) ─────────────────────────────────
LLM_CONFIG = {
    "base_url":    os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    "model":       os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
    "temperature": float(os.getenv("LLM_TEMPERATURE", "0.0")),
    "timeout":     300,   # secondes — ajustez selon votre machine
}

# ─── Configuration Neo4j ────────────────────────────────────────
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
if not NEO4J_PASSWORD:
    print("❌ ERREUR: NEO4J_PASSWORD manquante dans .env.local")
    print("   Veuillez créer un fichier .env.local avec vos credentials Neo4j")
    print("   Voir .env.local.example pour un template")
    sys.exit(1)

NEO4J_CONFIG = {
    "uri":      os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    "user":     os.getenv("NEO4J_USER", "neo4j"),
    "password": NEO4J_PASSWORD,
    "database": os.getenv("NEO4J_DB", "neo4j"),
}

# ─── Configuration Reranker (Cross-Encoder) ─────────────────────
RERANKER_CONFIG = {
    # Modèle recommandé si > 16Go RAM : "BAAI/bge-reranker-v2-m3" (2.2 Go)
    "model_name": "BAAI/bge-reranker-v2-m3", # Très léger (130Mo), bon en multilingue
    "top_k_after_rerank": 5,
    "device": "cpu",                # "cuda" si disponible
}

# ─── Configuration Query Analyzer ───────────────────────────────
QUERY_ANALYZER_CONFIG = {
    "default_weights": {
        "dense":  0.80,
        "sparse": 0.20,
    },
    "factual_weights": {
        "dense":  0.80,
        "sparse": 0.20,
    },
    "exploratory_weights": {
        "dense":  0.85,
        "sparse": 0.15,
    },
    "legal_weights": {
        "dense":  0.85,
        "sparse": 0.15,
    },
    "existence_weights": {
        "dense":  0.80,
        "sparse": 0.20,
    },
    "sanction_penale_weights": {
        "dense":  0.70,
        "sparse": 0.30,
    },
    "sanction_financiere_weights": {
        "dense":  0.70,
        "sparse": 0.30,
    },
    "condition_temporelle_weights": {
        "dense":  0.70,
        "sparse": 0.30,
    },
    "condition_spatiale_weights": {
        "dense":  0.70,
        "sparse": 0.30,
    },
    "controle_institution_weights": {
        "dense":  0.75,
        "sparse": 0.25,
    },
    "exception_weights": {
        "dense":  0.75,
        "sparse": 0.25,
    }
}

"""
app_streamlit.py — Interface Web NeuroLex
Raisonnement Neuro-Symbolique pour le Droit Environnemental

Pipeline :
  Query → QueryAnalyzer → [Dense + Sparse] → HybridFusion
        → OntologyAgent.enrich() → LLMGenerator.generate() → Réponse

Onglets :
  1. Consultation Juridique (RAG)
  2. Cartographie des Interdictions (Folium)
  3. Pipeline Neuro-Symbolique (Debug / Visualisation)
"""
import streamlit as st
import logging
from pathlib import Path
import sys
import json
import csv
import re
import time
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from rag.config import OUTPUT_DIR, configure_logging
from rag.core.retrievers import DenseRetriever, SparseRetriever
from rag.core.fusion import HybridFusion
from rag.core.query_analyzer import QueryAnalyzer
from rag.integration.neo4j_bridge_safe import get_safe_bridge
from rag.neo4j_ontology_agent import Neo4jOntologyAgent
from rag.llm_generator import LLMGenerator
from rag.utils.health_check import get_health_check
from rag.utils.metrics import get_metrics_logger
from rag.utils.evaluator import RagasDataCollector

configure_logging()

# ── Page Config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="NeuroLex ",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════
# PREMIUM DARK THEME — Glassmorphism + Animated Gradients
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── PREMIUM LIGHT MARINE THEME ── */
    :root {
        --bg-primary: #f8fafb;
        --bg-secondary: #f0f4f7;
        --bg-card: #ffffff;
        --bg-glass: rgba(255,255,255,0.85);
        --border-light: #e2e8f0;
        --border-hover: #0284c7;
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-muted: #94a3b8;
        --ocean-600: #0284c7;
        --ocean-500: #0ea5e9;
        --ocean-400: #38bdf8;
        --ocean-100: #e0f2fe;
        --ocean-50: #f0f9ff;
        --teal-500: #14b8a6;
        --teal-100: #ccfbf1;
        --emerald-500: #10b981;
        --amber-500: #f59e0b;
        --rose-500: #f43f5e;
        --gradient-ocean: linear-gradient(135deg, #0284c7, #0ea5e9, #14b8a6);
        --gradient-ocean-soft: linear-gradient(135deg, rgba(2,132,199,0.08), rgba(14,165,233,0.04));
        --shadow-soft: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.06);
        --shadow-ocean: 0 4px 20px rgba(2,132,199,0.12);
        --radius-lg: 16px;
        --radius-md: 12px;
        --radius-sm: 8px;
    }

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: var(--text-primary) !important;
        background-color: var(--bg-primary) !important;
    }

    .stApp {
        background: var(--bg-primary) !important;
    }

    .block-container {
        padding-top: 1rem !important;
        max-width: 1200px !important;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-primary) !important;
    }

    /* ── ANIMATED HEADER ── */
    .nl-hero {
        position: relative;
        text-align: center;
        padding: 44px 24px 28px;
        margin-bottom: 28px;
        overflow: hidden;
        border-bottom: 1px solid var(--border-light);
    }
    .nl-hero::before {
        content: '';
        position: absolute;
        top: -60%;
        left: -30%;
        width: 160%;
        height: 220%;
        background: radial-gradient(ellipse at 30% 50%, rgba(2,132,199,0.06) 0%, transparent 50%),
                    radial-gradient(ellipse at 70% 50%, rgba(20,184,166,0.05) 0%, transparent 50%);
        animation: hero-glow 8s ease-in-out infinite alternate;
    }
    @keyframes hero-glow {
        0% { transform: translate(0, 0) scale(1); }
        100% { transform: translate(-2%, 1%) scale(1.05); }
    }
    .nl-hero-content {
        position: relative;
        z-index: 1;
    }
    .nl-brand {
        font-size: 3em;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: var(--gradient-ocean);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        line-height: 1.15;
    }
    .nl-subtitle {
        font-size: 1em;
        font-weight: 400;
        color: var(--text-secondary) !important;
        margin-top: 6px;
        letter-spacing: 0.04em;
    }

    /* ── PIPELINE STEPS ── */
    .nl-pipeline {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 4px;
        margin: 20px auto 0;
        flex-wrap: wrap;
        max-width: 700px;
    }
    .nl-pipe-step {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: var(--bg-card);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-sm);
        padding: 6px 14px;
        font-size: 0.78em;
        font-weight: 500;
        color: var(--text-secondary) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: default;
        box-shadow: var(--shadow-soft);
    }
    .nl-pipe-step:hover {
        background: var(--ocean-50);
        border-color: var(--ocean-400);
        color: var(--ocean-600) !important;
        transform: translateY(-2px);
        box-shadow: var(--shadow-ocean);
    }
    .nl-pipe-arrow {
        color: var(--text-muted) !important;
        font-size: 0.9em;
        margin: 0 2px;
    }

    /* ── ANSWER BOX ── */
    .nl-answer {
        position: relative;
        background: var(--bg-card);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-lg);
        padding: 28px 32px;
        margin: 16px 0;
        font-size: 1.02em;
        line-height: 1.9;
        white-space: pre-wrap;
        color: var(--text-primary) !important;
        overflow: hidden;
        box-shadow: var(--shadow-md);
    }
    .nl-answer::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-ocean);
        border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    }

    /* ── STATUS DOTS ── */
    .nl-status-row {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 0;
        font-size: 0.85em;
        color: var(--text-secondary) !important;
    }
    .nl-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        display: inline-block;
        flex-shrink: 0;
    }
    .nl-dot-ok {
        background: var(--emerald-500);
        box-shadow: 0 0 6px rgba(16,185,129,0.35);
    }
    .nl-dot-fail {
        background: var(--rose-500);
        box-shadow: 0 0 6px rgba(244,63,94,0.35);
    }

    /* ── BADGES ── */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72em;
        margin: 2px;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }
    .badge-dense  { background: #d1fae5; color: #065f46 !important; }
    .badge-sparse { background: #fef3c7; color: #92400e !important; }
    .badge-graph  { background: var(--ocean-100); color: #075985 !important; }

    /* ── GAP WARNING ── */
    .gap-warning {
        background: #fffbeb;
        border-left: 3px solid var(--amber-500);
        padding: 12px 16px;
        border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
        margin: 8px 0;
        font-size: 0.9em;
        color: var(--text-secondary) !important;
    }

    /* ── FACT ITEM ── */
    .fact-item {
        padding: 4px 0;
        font-size: 0.9em;
        color: var(--text-secondary) !important;
    }
    .fact-item b { color: var(--text-primary) !important; }
    .fact-item i { color: var(--ocean-600) !important; }

    /* ── INTENT / WEIGHT PILLS ── */
    .nl-intent-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: var(--ocean-50);
        border: 1px solid rgba(2,132,199,0.2);
        border-radius: 20px;
        padding: 6px 16px;
        font-size: 0.85em;
        font-weight: 500;
        color: var(--ocean-600) !important;
    }
    .nl-weight-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: var(--teal-100);
        border: 1px solid rgba(20,184,166,0.2);
        border-radius: 20px;
        padding: 6px 16px;
        font-size: 0.85em;
        font-weight: 500;
        color: #0d9488 !important;
    }

    /* ── SECTION TITLE ── */
    .nl-section-title {
        font-size: 1.2em;
        font-weight: 700;
        color: var(--text-primary) !important;
        margin: 24px 0 12px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .nl-section-title::after {
        content: '';
        flex: 1;
        height: 1px;
        background: var(--border-light);
    }

    /* ── METRIC CARDS ── */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: 20px;
        text-align: center;
        box-shadow: var(--shadow-soft);
    }
    .metric-value {
        font-size: 2em;
        font-weight: 800;
        background: var(--gradient-ocean);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .metric-label {
        font-size: 0.82em;
        color: var(--text-muted) !important;
        font-weight: 500;
        margin-top: 4px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    /* ── MAP ── */
    .nl-map-title {
        font-size: 1.3em;
        font-weight: 700;
        color: var(--text-primary) !important;
        margin-bottom: 4px;
    }
    .nl-map-legend {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 12px 0 20px;
        font-size: 0.85em;
    }
    .nl-map-legend-item {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        color: var(--text-secondary) !important;
        background: var(--bg-card);
        border: 1px solid var(--border-light);
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.88em;
        box-shadow: var(--shadow-soft);
    }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-light) !important;
    }
    .sidebar-title {
        font-size: 1.1em;
        font-weight: 700;
        background: var(--gradient-ocean);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 12px;
    }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 2px solid var(--border-light) !important;
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 14px 28px !important;
        font-weight: 500 !important;
        font-size: 0.9em !important;
        font-family: 'Inter', sans-serif !important;
        border-radius: 0 !important;
        border-bottom: 2px solid transparent !important;
        margin-bottom: -2px !important;
        color: var(--text-muted) !important;
        background: transparent !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-secondary) !important;
    }
    .stTabs [aria-selected="true"] {
        border-bottom: 2px solid var(--ocean-500) !important;
        color: var(--ocean-600) !important;
        font-weight: 600 !important;
    }

    /* ── SEARCH INPUT ── */
    .stTextInput input {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-md) !important;
        font-size: 1em !important;
        padding: 14px 18px !important;
        color: var(--text-primary) !important;
        transition: all 0.25s ease !important;
        box-shadow: var(--shadow-soft) !important;
    }
    .stTextInput input::placeholder {
        color: var(--text-muted) !important;
    }
    .stTextInput input:focus {
        border-color: var(--ocean-500) !important;
        box-shadow: 0 0 0 3px rgba(14,165,233,0.12), var(--shadow-soft) !important;
    }

    /* ── BUTTONS ── */
    .stButton button {
        border-radius: var(--radius-md) !important;
        font-weight: 600 !important;
        font-size: 0.9em !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid var(--border-light) !important;
        color: var(--text-primary) !important;
        background: var(--bg-card) !important;
    }
    .stButton button:hover {
        border-color: var(--ocean-400) !important;
        background: var(--ocean-50) !important;
        color: var(--ocean-600) !important;
    }
    .stButton button[kind="primary"] {
        background: var(--gradient-ocean) !important;
        border: none !important;
        color: #fff !important;
        box-shadow: var(--shadow-soft) !important;
    }
    .stButton button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-ocean) !important;
    }

    /* ── SECTION DIVIDER ── */
    hr {
        border: none !important;
        border-top: 1px solid var(--border-light) !important;
        margin: 20px 0 !important;
    }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

    /* ── EMPTY STATE ── */
    .nl-empty-state {
        text-align: center;
        padding: 60px 20px;
    }
    .nl-empty-icon {
        font-size: 3em;
        margin-bottom: 12px;
        opacity: 0.5;
    }
    .nl-empty-text {
        font-size: 1em;
        color: var(--text-muted) !important;
    }

    /* ── ARCHITECTURE CARDS ── */
    .arch-card {
        background: var(--bg-card);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-lg);
        padding: 24px;
        height: 100%;
        box-shadow: var(--shadow-soft);
        transition: all 0.3s ease;
    }
    .arch-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }
    .arch-card-title {
        font-size: 1.1em;
        font-weight: 700;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .arch-card-neural .arch-card-title { color: var(--ocean-600) !important; }
    .arch-card-symbolic .arch-card-title { color: #7c3aed !important; }

    /* ── COUNTRY PILLS ── */
    .country-pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: var(--bg-card);
        border: 1px solid var(--border-light);
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.82em;
        color: var(--text-secondary) !important;
        margin: 3px;
        box-shadow: var(--shadow-soft);
    }

    /* ── HIDE STREAMLIT BRANDING ── */
    /* #MainMenu {visibility: hidden;} (Commenté pour permettre le Record Screencast) */
    footer {visibility: hidden;}

    .nl-empty-state {
        text-align: center;
        padding: 60px 20px;
        color: var(--text-muted) !important;
    }
    .nl-empty-icon {
        font-size: 3em;
        margin-bottom: 12px;
        opacity: 0.4;
    }
    .nl-empty-text {
        font-size: 1em;
        color: var(--text-muted) !important;
    }

    /* ── ARCHITECTURE CARDS ── */
    .arch-card {
        background: var(--bg-glass);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-lg);
        padding: 24px;
        height: 100%;
    }
    .arch-card-title {
        font-size: 1.1em;
        font-weight: 700;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .arch-card-neural .arch-card-title { color: var(--accent-cyan) !important; }
    .arch-card-symbolic .arch-card-title { color: var(--accent-purple) !important; }

    /* ── HIDE STREAMLIT BRANDING ── */
    /* #MainMenu {visibility: hidden;} (Commenté pour permettre le Record Screencast) */
    footer {visibility: hidden;}

    /* ── COUNTRY PILLS ── */
    .country-pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: var(--bg-glass);
        border: 1px solid var(--border-glass);
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.82em;
        color: var(--text-secondary) !important;
        margin: 3px;
    }

    /* ── LOADING PULSE ── */
    @keyframes pulse-glow {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 1; }
    }
    .loading-pulse {
        animation: pulse-glow 1.5s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# LOADERS (pipeline identique)
# ══════════════════════════════════════════════════════════════════

@st.cache_resource
def load_dense():
    try:
        r = DenseRetriever(); return r if r.is_ready() else None
    except Exception as e:
        logger.warning(f"Dense: {e}"); return None

@st.cache_resource
def load_sparse():
    try:
        r = SparseRetriever(); return r if r.is_ready() else None
    except Exception as e:
        logger.warning(f"Sparse: {e}"); return None

@st.cache_resource
def load_onto_bridge():
    try:
        bridge = get_safe_bridge()
        return bridge if bridge.is_ready() else None
    except Exception as e:
        logger.warning(f"Neo4jBridge: {e}")
        return None

@st.cache_resource
def load_onto_agent():
    bridge = load_onto_bridge()
    if bridge and bridge.is_ready():
        return Neo4jOntologyAgent(bridge)
    return None

@st.cache_resource
def load_llm():
    return LLMGenerator()

@st.cache_data(ttl=3600)
def perform_health_check_cached():
    health = get_health_check()
    health.full_check()
    return health.get_status_dict(), health.get_errors()


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def render_source_card(result: dict, index: int):
    meta = result.get("metadata", {})
    src  = meta.get("source", "N/A").split("/")[-1].replace(".pdf", "")
    page = meta.get("page", "")
    country = meta.get("country", "")
    rrf_score = result.get("hybrid_score", 0.0)
    rerank_score = result.get("rerank_score", 0.0)
    sources = result.get("retriever_sources", [])

    label = f"📄 [{index}] {src}"
    if country: label += f" — {country.upper()}"
    if page:    label += f" (p.{page})"

    with st.expander(label, expanded=False):
        badges = " ".join(
            f'<span class="badge badge-{s}">{s}</span>' for s in sources
        )
        score_display = f"{rerank_score:.4f} (Reranker) | RRF: {rrf_score:.4f}" if rerank_score else f"{rrf_score:.4f} (RRF)"
        st.markdown(f"**Score :** `{score_display}` {badges}", unsafe_allow_html=True)
        text = result.get("text", "").strip()
        if "\n\n" in text and ">" in text.split("\n\n")[0]:
            text = text.split("\n\n", 1)[1].strip()
        st.write(text)


def log_interaction(query: str, system_prompt: str, doc_context: str, response: str, country: str = "N/A"):
    """Logue la question, le contexte et la réponse dans un fichier JSONL et CSV."""
    log_file_jsonl = OUTPUT_DIR / "qa_history.jsonl"
    log_file_csv = OUTPUT_DIR / "qa_history.csv"
    timestamp = datetime.now().isoformat()

    record = {
        "timestamp": timestamp, "query": query, "country": country,
        "system_prompt": system_prompt,
        "document_context_length": len(doc_context),
        "response": response
    }
    try:
        with open(log_file_jsonl, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.warning(f"Erreur log JSONL : {e}")

    try:
        file_exists = log_file_csv.exists()
        with open(log_file_csv, "a", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=';')
            if not file_exists:
                writer.writerow(["Question", "Pays", "Reponse"])
            clean_response = re.sub(r'<analyse>.*?</analyse>', '', response.strip(), flags=re.DOTALL).strip()
            clean_response = re.sub(r'\s+', ' ', clean_response)
            writer.writerow([query, country, clean_response])
    except Exception as e:
        logger.warning(f"Erreur log CSV : {e}")


def render_enriched_context(enriched_ctx):
    """Affiche le résultat de l'OntologyAgent."""
    if enriched_ctx is None:
        st.info("OntologyAgent non disponible ou non utilisé pour cette requête.")
        return

    st.caption(enriched_ctx.ontology_summary)

    if enriched_ctx.detected_entities:
        st.markdown(f"**Entités détectées :** {', '.join(enriched_ctx.detected_entities)}")

    if enriched_ctx.synonyms_map:
        with st.expander("📚 Référentiel de synonymes (Neo4j)", expanded=True):
            inter_keys = [k for k in enriched_ctx.synonyms_map.keys() if "interdiction" in k.lower()]
            hidden_terms = set()
            for ik in inter_keys:
                name_part = ik.replace("L'interdiction '", "").replace("'", "").lower()
                for k in enriched_ctx.synonyms_map.keys():
                    if k != ik and (k.lower() in name_part or name_part in k.lower()):
                        hidden_terms.add(k)

            for k in inter_keys:
                syns = enriched_ctx.synonyms_map[k]
                st.markdown(f"• **{k}** ↔ {', '.join(sorted(syns))}")

            remaining_keys = [k for k in enriched_ctx.synonyms_map.keys() if k not in inter_keys and k not in hidden_terms]
            if remaining_keys:
                if inter_keys: st.markdown("---")
                for k in remaining_keys:
                    syns = set(enriched_ctx.synonyms_map[k]) - {k}
                    if syns:
                        st.markdown(f"• **{k}** ↔ {', '.join(sorted(syns))}")
                    else:
                        st.markdown(f"• **{k}** (aucun synonyme direct)")

    if enriched_ctx.direct_facts:
        st.markdown("##### Faits directs (1 saut)")
        for f in enriched_ctx.direct_facts[:10]:
            st.markdown(
                f'<div class="fact-item">• <b>{f.subject}</b> {f.predicate} <i>{f.obj}</i></div>',
                unsafe_allow_html=True
            )

    if enriched_ctx.multi_hop_facts:
        st.markdown("##### Relations indirectes (multi-sauts)")
        for f in enriched_ctx.multi_hop_facts[:10]:
            st.markdown(
                f'<div class="fact-item">• <b>{f.subject}</b> {f.predicate} <i>{f.obj}</i> '
                f'<span style="color:var(--text-muted)">[{f.hop_distance} saut(s)]</span></div>',
                unsafe_allow_html=True
            )

    if enriched_ctx.cross_enrichment_facts:
        st.markdown("##### Complément croisé (entités extraites des PDF)")
        for f in enriched_ctx.cross_enrichment_facts[:8]:
            st.markdown(
                f'<div class="fact-item">• <b>{f.subject}</b> {f.predicate} <i>{f.obj}</i></div>',
                unsafe_allow_html=True
            )

    if enriched_ctx.coverage_gaps:
        st.markdown("##### ⚠️ Lacunes documentaires détectées")
        for gap in enriched_ctx.coverage_gaps:
            st.markdown(f'<div class="gap-warning">{gap}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# CARTOGRAPHIE : données des pays et carte Folium
# ══════════════════════════════════════════════════════════════════

PAYS_COORDS = {
    "Bénin":         {"lat": 9.3077,  "lon": 2.3158,   "code": "ben"},
    "Cameroun":      {"lat": 5.9631,  "lon": 10.1591,  "code": "cmr"},
    "Comores":       {"lat":-12.2361, "lon": 44.3530,  "code": "com"},
    "Congo":         {"lat":-4.2634,  "lon": 15.2429,  "code": "cng"},
    "Côte d'Ivoire": {"lat": 7.5400,  "lon": -5.5471,  "code": "ivc"},
    "Djibouti":      {"lat": 11.5721, "lon": 43.1456,  "code": "dji"},
    "Gabon":         {"lat":-0.8037,  "lon": 11.6094,  "code": "gab"},
    "Guinée":        {"lat": 9.9456,  "lon": -9.6966,  "code": "gui"},
    "Madagascar":    {"lat":-18.7669, "lon": 46.8691,  "code": "mad"},
    "Maroc":         {"lat": 31.7917, "lon": -7.0926,  "code": "mor"},
    "Mauritanie":    {"lat": 21.0079, "lon": -10.9408, "code": "mau"},
    "Sénégal":       {"lat": 14.4974, "lon": -14.4524, "code": "sen"},
    "Togo":          {"lat": 8.6195,  "lon": 0.8248,   "code": "tog"},
    "Tunisie":       {"lat": 33.8869, "lon": 9.5375,   "code": "tun"},
}

INTERDICTIONS_MAP = [
    {"icon": "🐋", "label": "Chasse à la baleine",         "question": "Est-ce qu'il existe un article portant sur l'interdiction de la chasse des baleines {prep} ?"},
    {"icon": "🏗️", "label": "Construction sur le littoral", "question": "Est-ce qu'il existe un article portant sur l'interdiction de la construction sur le littoral {prep} ?"},
    {"icon": "🛢️", "label": "Rejet d'hydrocarbures",       "question": "Est-ce qu'il existe un article portant sur l'interdiction du rejet d'hydrocarbures {prep} ?"},
    {"icon": "🎣", "label": "Chalutage de fond",            "question": "Est-ce qu'il existe un article portant sur l'interdiction du chalutage de fond {prep} ?"},
    {"icon": "🦅", "label": "Oiseaux marins",               "question": "Est-ce qu'il existe un article portant sur l'interdiction des oiseaux marins {prep} ?"},
    {"icon": "⛏️", "label": "Extraction de sable marin",    "question": "Est-ce qu'il existe un article portant sur l'interdiction d'extraction de sable marin {prep} ?"},
]

PREPS = {
    "Bénin": "au Bénin", "Cameroun": "au Cameroun", "Comores": "aux Comores",
    "Congo": "au Congo", "Côte d'Ivoire": "en Côte d'Ivoire", "Djibouti": "à Djibouti",
    "Gabon": "au Gabon", "Guinée": "en Guinée", "Madagascar": "à Madagascar",
    "Maroc": "au Maroc", "Mauritanie": "en Mauritanie", "Sénégal": "au Sénégal",
    "Togo": "au Togo", "Tunisie": "en Tunisie",
}


def build_map():
    """Construit la carte Folium avec les 14 pays et les 6 interdictions."""
    import folium
    m = folium.Map(
        location=[10.0, 10.0],
        zoom_start=4,
        tiles="CartoDB positron",
        attr="© CartoDB"
    )

    for pays, info in PAYS_COORDS.items():
        prep = PREPS.get(pays, pays)

        # Construire le contenu HTML de la popup (thème clair marin)
        popup_lines = [
            f'<div style="font-family:Inter,sans-serif;min-width:240px;max-width:300px;background:#ffffff;color:#0f172a;padding:12px;border-radius:8px;border:1px solid #e2e8f0;">',
            f'<h4 style="margin:0 0 8px;color:#0284c7;font-size:1.1em;border-bottom:1px solid #e2e8f0;padding-bottom:6px">{pays}</h4>',
            f'<p style="font-size:0.78em;color:#64748b;margin:0 0 8px">6 interdictions environnementales étudiées</p>',
        ]

        for inter in INTERDICTIONS_MAP:
            question = inter["question"].replace("{prep}", prep)
            popup_lines.append(
                f'<div style="padding:3px 0;font-size:0.85em;color:#334155">'
                f'{inter["icon"]} {inter["label"]}'
                f'</div>'
            )

        popup_lines.append('</div>')
        popup_html = "\n".join(popup_lines)

        folium.Marker(
            location=[info["lat"], info["lon"]],
            popup=folium.Popup(popup_html, max_width=320),
            tooltip=pays,
            icon=folium.Icon(color="blue", icon="info-sign"),
        ).add_to(m)

    return m


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    # ── Session state ─────────────────────────────────────────────
    if "m_logger" not in st.session_state:
        st.session_state.m_logger = get_metrics_logger(OUTPUT_DIR)
    if "ragas_collector" not in st.session_state:
        st.session_state.ragas_collector = RagasDataCollector()

    # ── Header ────────────────────────────────────────────────────
    st.markdown("""
    <div class="nl-hero">
        <div class="nl-hero-content">
            <h1 class="nl-brand">⚖️ NeuroLex</h1>
            <p class="nl-subtitle">Raisonnement Neuro-Symbolique · Droit de l'environnement marin</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Pipeline visuel
    steps = [
        ("🔍", "Analyse"),
        ("📡", "Retrieval"),
        ("⚡", "Fusion"),
        ("🧬", "Ontologie"),
        ("🤖", "LLM"),
    ]
    steps_html = ""
    for i, (icon, label) in enumerate(steps):
        steps_html += f'<span class="nl-pipe-step">{icon} {label}</span>'
        if i < len(steps) - 1:
            steps_html += '<span class="nl-pipe-arrow">→</span>'
    st.markdown(f'<div class="nl-pipeline">{steps_html}</div>', unsafe_allow_html=True)

    # ── Sidebar ───────────────────────────────────────────────────
    with st.sidebar:
        st.markdown('<div class="sidebar-title">⚖️ NeuroLex</div>', unsafe_allow_html=True)
        st.caption("Système RAG Neuro-Symbolique")

        st.markdown("---")

        with st.expander("⚙️ Paramètres", expanded=False):
            top_k       = st.slider("Documents à récupérer", 3, 15, 6)
            stream_mode = st.checkbox("Streaming", value=True)
            use_dense   = st.checkbox("Dense (ChromaDB)", value=True)
            use_sparse  = st.checkbox("Sparse (BM25)", value=True)
            use_agent   = st.checkbox("OntologyAgent (Neo4j)", value=True,
                                      help="Navigation multi-sauts + enrichissement croisé PDF↔Ontologie")

        # Valeurs par défaut si l'expander n'a jamais été ouvert
        if "top_k" not in dir():
            top_k = 6; stream_mode = True
            use_dense = True; use_sparse = True; use_agent = True

        st.markdown("---")
        st.markdown("**Système**")

        with st.spinner("Vérification..."):
            health_status, health_errors = perform_health_check_cached()

        components = [
            ("Dense",  health_status.get("dense")),
            ("Sparse", health_status.get("sparse")),
            ("Neo4j",  health_status.get("neo4j")),
            ("Ollama", health_status.get("ollama")),
        ]
        for name, ok in components:
            dot_class = "nl-dot-ok" if ok else "nl-dot-fail"
            status_text = "Actif" if ok else "Inactif"
            st.markdown(
                f'<div class="nl-status-row"><span class="nl-dot {dot_class}"></span> {name} — {status_text}</div>',
                unsafe_allow_html=True
            )

        if health_errors:
            with st.expander("⚠️ Erreurs", expanded=False):
                for component, error in health_errors.items():
                    st.error(f"**{component}**: {error}")

        st.markdown("---")
        st.caption("NeuroLex v1.0 · Neuro-Symbolique")

    # ══════════════════════════════════════════════════════════════
    # ONGLETS PRINCIPAUX
    # ══════════════════════════════════════════════════════════════

    tab_consult, tab_map, tab_pipeline = st.tabs([
        "🔎  Consultation",
        "🌍  Cartographie",
        "🧬  Pipeline",
    ])

    # ══════════════════════════════════════════════════════════════
    # ONGLET 1 : CONSULTATION JURIDIQUE
    # ══════════════════════════════════════════════════════════════

    with tab_consult:
        col1, col2 = st.columns([5, 1])
        with col1:
            query = st.text_input(
                "Posez votre question juridique :",
                placeholder="Ex : Quelles sont les sanctions pour la chasse des baleines au Bénin ?",
                label_visibility="collapsed",
            )
        with col2:
            st.write("")
            search_button = st.button("Rechercher", use_container_width=True, type="primary")

        # Suggestions
        st.markdown('<div class="nl-section-title">💡 Suggestions</div>', unsafe_allow_html=True)
        suggestions = [
            "Quelles sont les sanctions pour la pêche dans une aire marine protégée au Bénin ?",
            "Existe-t-il des dérogations pour la chasse traditionnelle des espèces protégées au Cameroun ?",
            "Quelles espèces marines sont protégées au Sénégal ?",
            "Quelles sont les sanctions pour le rejet d'hydrocarbures au Maroc ?",
            "Est-ce que l'extraction de sable marin est interdite au Togo ?",
            "Quelles procédures de contrôle existent pour le chalutage de fond en Guinée ?",
        ]
        cols = st.columns(3)
        for i, sug in enumerate(suggestions):
            if cols[i % 3].button(sug, key=f"sug_{i}", use_container_width=True):
                query = sug

        st.markdown("---")

        # ── Pipeline RAG ──────────────────────────────────────────
        if not (query and query.strip()) and not search_button:
            st.markdown(
                '<div class="nl-empty-state">'
                '<div class="nl-empty-icon">⚖️</div>'
                '<div class="nl-empty-text">Saisissez une question ou cliquez sur une suggestion pour commencer.</div>'
                '</div>',
                unsafe_allow_html=True
            )
        elif not query or not query.strip():
            st.warning("Veuillez entrer une question.")
        else:
            start_time = time.time()

            # Étape 1 : Analyse d'intention
            analyzer = QueryAnalyzer()
            intent, weights, country_filter, category_filter = analyzer.analyze(query)

            # Intent + Weights pills
            icons = {"factual": "📊", "legal": "⚖️", "exploratory": "🔭", "existence": "❓", "default": "🔍",
                     "sanction_penale": "⛓️", "sanction_financiere": "💰", "condition_temporelle": "📅",
                     "condition_spatiale": "📍", "controle_institution": "🏛️", "exception": "🔓"}
            intent_icon = icons.get(intent, "🔍")
            country_badge = f" · 🌍 <b>{country_filter.upper()}</b>" if country_filter else ""
            weights_str = " · ".join(f"<code>{k}: {v:.0%}</code>" for k, v in weights.items())
            st.markdown(
                f'<div style="display:flex;gap:10px;flex-wrap:wrap;margin:8px 0 16px">'
                f'<span class="nl-intent-pill">{intent_icon} {intent}{country_badge}</span>'
                f'<span class="nl-weight-pill">⚖ {weights_str}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

            # Étape 2 : Retrieval
            retriever_results = {}
            k = top_k * 2

            with st.spinner("🔍 Retrieval en cours..."):
                graph_entities = set()
                synonym_sets = {}
                expanded_terms = []
                query_context = None

                if use_agent:
                    agent = load_onto_agent()
                    if agent and agent.is_ready():
                        query_context = agent.prepare_query(query, intent=intent)
                        synonym_sets = query_context.get("synonyms_map", {})
                        graph_entities = query_context.get("graph_entities", set())
                        expanded_terms = query_context.get("expanded_terms", [])

                if use_dense:
                    d = load_dense()
                    if d: retriever_results["dense"] = d.retrieve(query, k, expanded_terms=expanded_terms, country_filter=country_filter)

                if use_sparse:
                    s = load_sparse()
                    if s: retriever_results["sparse"] = s.retrieve(query, k, expanded_terms=expanded_terms, country_filter=country_filter)

            if not retriever_results:
                st.error("❌ Aucun retriever disponible.")
                return

            # Étape 3 : Fusion RRF
            fusion = HybridFusion()
            fused = fusion.fuse(
                retriever_results=retriever_results,
                weights=weights,
                graph_entities=graph_entities,
                synonym_sets=synonym_sets,
                ontology_boost=0.5,
                top_k=top_k,
                country_filter=country_filter,
                category_filter=category_filter,
                query=query,
                intent=intent,
                expanded_terms=expanded_terms
            )

            # Étape 4 : OntologyAgent
            enriched_ctx = None
            if use_agent:
                agent = load_onto_agent()
                if agent:
                    with st.spinner("🧬 OntologyAgent — navigation du graphe..."):
                        enriched_ctx = agent.enrich(query=query, fusion_results=fused, query_context=query_context)

            # Étape 5 : Génération LLM
            st.markdown('<div class="nl-section-title">💬 Réponse</div>', unsafe_allow_html=True)
            llm = load_llm()

            if not llm.is_ollama_available():
                st.error("Ollama non accessible. Lancez `ollama serve` puis `ollama pull mistral`.")
            else:
                if stream_mode:
                    result = llm.generate(
                        query=query, fusion_results=fused, intent=intent,
                        enriched_context=enriched_ctx, stream=True,
                    )
                    if result.get("error"):
                        st.error(result["error"])
                    else:
                        placeholder = st.empty()
                        full = ""
                        for token in result["stream_generator"]:
                            full += token
                            display_text = re.sub(r'<analyse>.*?(?:</analyse>|$)', '', full, flags=re.DOTALL).strip()
                            placeholder.markdown(
                                f'<div class="nl-answer">{display_text}▌</div>',
                                unsafe_allow_html=True
                            )

                        display_text = re.sub(r'<analyse>.*?(?:</analyse>|$)', '', full, flags=re.DOTALL).strip()
                        placeholder.markdown(
                            f'<div class="nl-answer">{display_text}</div>',
                            unsafe_allow_html=True
                        )

                        match = re.search(r'<analyse>(.*?)</analyse>', full, flags=re.DOTALL)
                        if match:
                            with st.expander("🧠 Raisonnement de l'IA (Chain of Thought)"):
                                st.markdown(match.group(1).strip())

                        # Métriques
                        duration_ms = int((time.time() - start_time) * 1000)
                        m_logger = st.session_state.m_logger
                        m_logger.log_query(
                            query=query, intent=intent, weights=weights,
                            sources_retrieved={k: len(v) for k, v in retriever_results.items()},
                            top_scores={}, response_time_ms=duration_ms,
                            country_filter=country_filter
                        )
                        m_logger.log_fusion_impact(query, fused, retriever_results, boost_count=len(synonym_sets))
                        m_logger.log_generation(query, full, len(full)//4, duration_ms)

                        st.session_state.ragas_collector.add_sample(
                            question=query, answer=display_text,
                            contexts=[r.get("text", "") for r in fused if r.get("source_retriever") != "graph"]
                        )
                        log_interaction(query, result.get("system_prompt", ""), result.get("document_context", ""), full, country_filter or "N/A")

                        # Stocker pour l'onglet Pipeline
                        st.session_state["last_enriched_ctx"] = enriched_ctx
                        st.session_state["last_fused"] = fused
                        st.session_state["last_retriever_results"] = retriever_results
                        st.session_state["last_query"] = query
                        st.session_state["last_intent"] = intent
                        st.session_state["last_weights"] = weights
                else:
                    with st.spinner(f"🤖 {llm.model_name} génère..."):
                        result = llm.generate(
                            query=query, fusion_results=fused, intent=intent,
                            enriched_context=enriched_ctx, stream=False,
                        )
                    if result.get("error"):
                        st.error(result["error"])
                    else:
                        ans = result.get("answer", "")
                        display_text = re.sub(r'<analyse>.*?(?:</analyse>|$)', '', ans, flags=re.DOTALL).strip()
                        st.markdown(
                            f'<div class="nl-answer">{display_text}</div>',
                            unsafe_allow_html=True
                        )
                        match = re.search(r'<analyse>(.*?)</analyse>', ans, flags=re.DOTALL)
                        if match:
                            with st.expander("🧠 Raisonnement de l'IA (Chain of Thought)"):
                                st.markdown(match.group(1).strip())

                        st.session_state.ragas_collector.add_sample(
                            question=query, answer=display_text,
                            contexts=[r.get("text", "") for r in fused if r.get("source_retriever") != "graph"]
                        )
                        log_interaction(query, result.get("system_prompt", ""), result.get("document_context", ""), ans, country_filter or "N/A")

                        st.session_state["last_enriched_ctx"] = enriched_ctx
                        st.session_state["last_fused"] = fused
                        st.session_state["last_retriever_results"] = retriever_results
                        st.session_state["last_query"] = query
                        st.session_state["last_intent"] = intent
                        st.session_state["last_weights"] = weights

            # ── Sources ───────────────────────────────────────────
            st.markdown('<div class="nl-section-title">📄 Sources</div>', unsafe_allow_html=True)
            doc_results = [r for r in fused if r.get("source_retriever") != "graph"
                           and r.get("metadata", {}).get("source") != "ontology"]

            if doc_results:
                for i, r in enumerate(doc_results, 1):
                    render_source_card(r, i)
            else:
                st.info("Aucun document récupéré.")

    # ══════════════════════════════════════════════════════════════
    # ONGLET 2 : CARTOGRAPHIE DES INTERDICTIONS
    # ══════════════════════════════════════════════════════════════

    with tab_map:
        st.markdown('<p class="nl-map-title">🌍 Pays étudiés et interdictions environnementales</p>', unsafe_allow_html=True)
        st.markdown(
            '<p style="color:var(--text-secondary);font-size:0.9em;margin-bottom:16px">'
            'Cliquez sur un marqueur pour voir les 6 interdictions étudiées dans chaque pays.</p>',
            unsafe_allow_html=True
        )

        # Légende
        legend_html = '<div class="nl-map-legend">'
        for inter in INTERDICTIONS_MAP:
            legend_html += f'<span class="nl-map-legend-item">{inter["icon"]} {inter["label"]}</span>'
        legend_html += '</div>'
        st.markdown(legend_html, unsafe_allow_html=True)

        # Carte
        try:
            from streamlit_folium import st_folium
            m = build_map()
            st_folium(m, width=None, height=520, use_container_width=True)
        except ImportError:
            st.error("⚠️ `streamlit-folium` n'est pas installé. Exécutez : `pip install folium streamlit-folium`")
        except Exception as e:
            st.error(f"Erreur lors du chargement de la carte : {e}")

        st.markdown("---")
        st.markdown('<div class="nl-section-title">📋 Pays couverts</div>', unsafe_allow_html=True)
        pays_html = ""
        for pays in sorted(PAYS_COORDS.keys()):
            pays_html += f'<span class="country-pill">🏴 {pays}</span>'
        st.markdown(f'<div style="margin:8px 0">{pays_html}</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    # ONGLET 3 : PIPELINE NEURO-SYMBOLIQUE
    # ══════════════════════════════════════════════════════════════

    with tab_pipeline:
        st.markdown('<div class="nl-section-title">🏗️ Architecture du Pipeline</div>', unsafe_allow_html=True)
        st.markdown(
            '<p style="color:var(--text-secondary);font-size:0.95em;margin-bottom:20px">'
            'Ce système hybride combine un <b>modèle de langage</b> (composante neuronale) '
            'et un <b>graphe de connaissances Neo4j</b> (composante symbolique) pour raisonner '
            'sur le droit environnemental.</p>',
            unsafe_allow_html=True
        )

        col_neural, col_symbolic = st.columns(2)
        with col_neural:
            st.markdown(
                '<div class="arch-card arch-card-neural">'
                '<div class="arch-card-title">🧠 Composante Neuronale</div>'
                '<p style="font-size:0.9em;line-height:1.7;color:var(--text-secondary) !important">'
                '• <b>Dense Retriever</b> — Recherche sémantique BGE-M3<br>'
                '• <b>Sparse Retriever</b> — Recherche lexicale BM25<br>'
                '• <b>Cross-Encoder</b> — Reranking des documents<br>'
                '• <b>LLM</b> — Génération (Mistral/Llama via Ollama)</p>'
                '</div>',
                unsafe_allow_html=True
            )
        with col_symbolic:
            st.markdown(
                '<div class="arch-card arch-card-symbolic">'
                '<div class="arch-card-title">🔗 Composante Symbolique</div>'
                '<p style="font-size:0.9em;line-height:1.7;color:var(--text-secondary) !important">'
                '• <b>OntologyAgent</b> — Navigation du graphe Neo4j<br>'
                '• <b>Synonymes</b> — baleine → mammifère marin<br>'
                '• <b>Expansion</b> — Enrichissement des requêtes<br>'
                '• <b>Multi-sauts</b> — Relations indirectes</p>'
                '</div>',
                unsafe_allow_html=True
            )

        st.markdown("---")

        # Afficher les résultats de la dernière requête si disponibles
        if "last_enriched_ctx" in st.session_state and st.session_state["last_enriched_ctx"]:
            st.markdown(f'<div class="nl-section-title">🔬 Dernière requête</div>', unsafe_allow_html=True)
            st.markdown(f'*{st.session_state.get("last_query", "")}*')

            tab_onto, tab_debug = st.tabs(["🔗 Raisonnement Ontologique", "🔧 Données Brutes"])

            with tab_onto:
                render_enriched_context(st.session_state["last_enriched_ctx"])

            with tab_debug:
                last_fused = st.session_state.get("last_fused", [])
                last_rr = st.session_state.get("last_retriever_results", {})
                last_ctx = st.session_state.get("last_enriched_ctx")
                st.json({
                    "query": st.session_state.get("last_query", ""),
                    "intent": st.session_state.get("last_intent", ""),
                    "weights": st.session_state.get("last_weights", {}),
                    "retrievers": list(last_rr.keys()),
                    "candidates": {k: len(v) for k, v in last_rr.items()},
                    "fused": len(last_fused),
                    "agent_entities": last_ctx.detected_entities if last_ctx else [],
                    "agent_facts": len(last_ctx.all_facts) if last_ctx else 0,
                })
        else:
            st.markdown(
                '<div class="nl-empty-state">'
                '<div class="nl-empty-icon">🧬</div>'
                '<div class="nl-empty-text">Effectuez une recherche dans l\'onglet Consultation pour voir le détail du raisonnement neuro-symbolique ici.</div>'
                '</div>',
                unsafe_allow_html=True
            )

        # Métriques de performance
        with st.expander("📊 Métriques de Performance (Session)", expanded=False):
            m_logger = st.session_state.m_logger
            stats = m_logger.summary_stats()
            if stats:
                c1, c2, c3, c4 = st.columns(4)
                c1.markdown(
                    f'<div class="metric-card"><div class="metric-value">{stats.get("total_queries", 0)}</div>'
                    f'<div class="metric-label">Requêtes</div></div>', unsafe_allow_html=True)
                c2.markdown(
                    f'<div class="metric-card"><div class="metric-value">{stats.get("avg_response_time_ms", 0):.0f}ms</div>'
                    f'<div class="metric-label">Latence Moy.</div></div>', unsafe_allow_html=True)
                c3.markdown(
                    f'<div class="metric-card"><div class="metric-value">{stats.get("avg_graph_contribution", 0):.1f}</div>'
                    f'<div class="metric-label">Contrib. Graphe</div></div>', unsafe_allow_html=True)
                c4.markdown(
                    f'<div class="metric-card"><div class="metric-value">{stats.get("total_boosts", 0)}</div>'
                    f'<div class="metric-label">Total Boosts</div></div>', unsafe_allow_html=True)
            else:
                st.info("Lancez une recherche pour voir les statistiques.")


if __name__ == "__main__":
    main()
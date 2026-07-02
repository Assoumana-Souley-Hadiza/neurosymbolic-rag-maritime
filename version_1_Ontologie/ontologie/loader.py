"""
loader.py v2 — Chargement des fichiers JSON bruts du pipeline NLP.

Gère les deux formats :
  1. Nouveau format : *_final.json (raw_extractions, sources_juridiques, pipeline_triples)
  2. Ancien format  : step3_triples_I*.json et step2_definitions_I*.json
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

logger = logging.getLogger(__name__)


def load_json(path: Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _normalize_def(entry: dict, interdiction_id: Optional[str] = None) -> Optional[dict]:
    term = (entry.get("terme") or entry.get("term") or entry.get("label") or "").strip()
    defn = (entry.get("definition") or entry.get("meaning") or "").strip()
    if not term or not defn:
        return None
    out = dict(entry)
    out["term"] = term
    out["terme"] = term
    out["definition"] = defn
    out["interdiction_id"] = interdiction_id or entry.get("interdiction_id")
    return out


def load_raw_final_files(raw_dir: Path, glob_patterns: list[str] = ["*_final.json", "*_merged.json"]) -> Dict[str, Any]:
    """
    Charge les fichiers *_final.json ou *_merged.json du dossier all_entité_triplets ou extraction_merged.
    """
    result: Dict[str, Any] = {
        "triples": [], "definitions": [], "glossary": [],
        "raw_by_file": {}, "definitions_by_interdiction": {},
    }

    files: List[Path] = []
    for pattern in glob_patterns:
        for p in sorted(raw_dir.rglob(pattern)):
            files.append(p)
    
    if not files:
        logger.info(f"  ℹ️ Aucun fichier {glob_patterns} trouvé dans {raw_dir}")
        return result

    logger.info(f"  📁 {len(files)} fichier(s) de données trouvé(s) dans {raw_dir}")

    for fpath in files:
        try:
            data = load_json(fpath)
        except Exception as e:
            logger.warning(f"  ⚠️ Impossible de lire {fpath.name}: {e}")
            continue

        iid = data.get("interdiction_id") or _extract_iid(fpath.name)
        result["raw_by_file"][fpath.name] = data

        # Triplets (pipeline_triples ou triplets)
        triples = data.get("pipeline_triples", data.get("triplets", []))
        for t in triples:
            t.setdefault("interdiction_id", iid)
            t.setdefault("_source_file", fpath.name)
        result["triples"].extend(triples)

        # Entités extraites : On ne crée plus de définitions automatiques pour réduire le bruit
        # entites_trouvees = rx.get("entites_trouvees", data.get("entites", []))
        defs = []

        # Définitions explicites
        for d in data.get("definitions", []):
            nd = _normalize_def(d, iid)
            if nd:
                defs.append(nd)

        result["definitions"].extend(defs)
        result["definitions_by_interdiction"][iid] = defs

        logger.info(f"  📄 {fpath.name}: iid={iid}, {len(triples)} triplets, {len(defs)} entités/defs")

    return result


def _extract_iid(filename: str) -> str:
    m = re.search(r"(I\d{3})", filename)
    return m.group(1) if m else "UNKNOWN"


def load_all_raw_data(raw_dir_or_config: Any,
                      file_mapping: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Point d'entrée unique.

    Modes :
      1. config dict avec 'raw_dir' et optionnellement 'processed_dir'
      2. chemin direct (str ou Path)
      3. legacy : (raw_dir, file_mapping)
    """
    if isinstance(raw_dir_or_config, dict) and file_mapping is None:
        cfg = raw_dir_or_config
        # Essayer d'abord le dossier raw
        raw_dir = cfg.get("raw_dir") or cfg.get("processed_dir")
        if raw_dir:
            raw_path = Path(raw_dir)
            if raw_path.exists():
                return load_raw_final_files(raw_path)
        # Si processed_dir existe avec fichiers step*
        return _load_processed(cfg)

    if isinstance(raw_dir_or_config, (str, Path)) and file_mapping is None:
        return load_raw_final_files(Path(raw_dir_or_config))

    # Legacy mode
    return _load_legacy(str(raw_dir_or_config), file_mapping or {})


def _load_processed(cfg: dict) -> Dict[str, Any]:
    """Charge les fichiers step2/step3 générés par le pipeline NLP."""
    processed_dir = Path(cfg.get("processed_dir", "."))
    result: Dict[str, Any] = {
        "triples": [], "definitions": [], "glossary": [],
        "raw_by_file": {}, "definitions_by_interdiction": {},
    }
    if not processed_dir.exists():
        logger.warning(f"  ⚠️ processed_dir non trouvé : {processed_dir}")
        return result

    for fpath in sorted(processed_dir.glob("step3_triples_I*.json")):
        data = load_json(fpath)
        iid = _extract_iid(fpath.stem)
        triples = data if isinstance(data, list) else data.get("triples", [])
        for t in triples:
            t.setdefault("interdiction_id", iid)
        result["triples"].extend(triples)
        result["raw_by_file"][fpath.name] = data

    for fpath in sorted(processed_dir.glob("step2_definitions_I*.json")):
        data = load_json(fpath)
        iid = _extract_iid(fpath.stem)
        entries = data if isinstance(data, list) else data.get("definitions", [])
        defs = [d for e in entries if (d := _normalize_def(e, iid)) is not None]
        result["definitions"].extend(defs)
        result["definitions_by_interdiction"][iid] = defs
        result["raw_by_file"][fpath.name] = data

    logger.info(f"  ✅ {len(result['triples'])} triplets | {len(result['definitions'])} définitions (mode processed)")
    return result


def _load_legacy(raw_dir: str, file_mapping: Dict[str, str]) -> Dict[str, Any]:
    raw_path = Path(raw_dir)
    result: Dict[str, Any] = {
        "triples": [], "definitions": [], "glossary": [],
        "raw_by_file": {}, "definitions_by_interdiction": {},
    }
    for filename, iid in file_mapping.items():
        fpath = raw_path / filename
        if not fpath.exists():
            logger.warning(f"  ⚠️ {filename} introuvable")
            continue
        data = load_json(fpath)
        result["raw_by_file"][filename] = data
        inner = data.get("data", data) if isinstance(data, dict) else {}
        triples = inner.get("pipeline_triples", inner.get("triples", []))
        for t in triples:
            t.setdefault("interdiction_id", iid)
        result["triples"].extend(triples)
        defs = [d for e in inner.get("definitions", []) if (d := _normalize_def(e, iid)) is not None]
        result["definitions"].extend(defs)
        result["definitions_by_interdiction"].setdefault(iid, []).extend(defs)
    logger.info(f"  ✅ {len(result['triples'])} triplets | {len(result['definitions'])} defs (mode legacy)")
    return result


# ══════════════════════════════════════════════════════════════
# CHARGEMENT DES DÉFINITIONS RETENUES (Definitions_retenues/)
# ══════════════════════════════════════════════════════════════

# Mapping interdiction_id → convention source pour le lien mar:estDefiniPar
_INTERDICTION_SOURCE_MAP = {
    "I001": "Classification et définition illustrée des engins de pêche / Résolutions AGNU",
    "I002": "ICRW Schedule – Convention Baleinière Internationale (1946)",
    "I003": "Loi Littoral / Protocole GIZC / Construction littorale",
    "I004": "Convention sur la Diversité Biologique (CDB) / Extraction sable",
    "I005": "Convention CMS / Convention de Bonn (1979) / Oiseaux marins",
    "I006": "MARPOL 73/78 Annexe I – Rejets d'hydrocarbures",
}


def load_definitions_retenues(defs_dir: Path) -> Dict[str, List[dict]]:
    """
    Charge les fichiers de Definitions_retenues/.

    Gère les deux formats JSON :
      1. Array plat : [{terme, definition, ...}, ...]
      2. Objet structuré : {data: {glossary_entries: [{term, definition, ...}, ...]}}

    Retourne un dict : { interdiction_id: [normalized_entry, ...] }
    """
    result: Dict[str, List[dict]] = {}

    if not defs_dir.exists():
        logger.warning(f"  ⚠️ Dossier Definitions_retenues non trouvé : {defs_dir}")
        return result

    files = sorted(defs_dir.glob("*.json"))
    logger.info(f"  📚 {len(files)} fichier(s) de définitions trouvé(s) dans {defs_dir}")

    for fpath in files:
        iid = _extract_iid(fpath.stem)
        try:
            raw = load_json(fpath)
        except Exception as e:
            logger.warning(f"  ⚠️ Impossible de lire {fpath.name}: {e}")
            continue

        entries = []

        # Format 1 : Array plat [{terme, definition, ...}]
        if isinstance(raw, list):
            entries = raw

        # Format 2 : {data: {glossary_entries: [...]}}
        elif isinstance(raw, dict):
            data_block = raw.get("data", raw)
            if isinstance(data_block, dict):
                entries = data_block.get("glossary_entries", [])

        # Normaliser
        normalized = []
        for entry in entries:
            term = (entry.get("term") or entry.get("terme") or "").strip()
            defn = (entry.get("definition") or entry.get("meaning") or "").strip()
            lang = entry.get("language", "fr")
            if not term or not defn:
                continue
            normalized.append({
                "term": term,
                "definition": defn,
                "language": lang,
                "scientific_name": entry.get("scientific_name") or entry.get("nom_scientifique"),
                "article_reference": entry.get("article_reference") or entry.get("reference"),
                "document_title": entry.get("document_title") or entry.get("doc_id") or "",
                "interdiction_id": iid,
                "source_convention": _INTERDICTION_SOURCE_MAP.get(iid, ""),
            })

        result[iid] = normalized
        logger.info(f"    📄 {fpath.name}: {iid} → {len(normalized)} définitions")

    total = sum(len(v) for v in result.values())
    logger.info(f"  ✅ {total} définitions retenues chargées au total")
    return result


# ── Mapping contenu → IID pour les fichiers synonymes ─────────────
# Les fichiers 03/04/05 ne suivent PAS le même ordre que I003/I004/I005.
# On mappe par le contenu du champ "interdiction" dans chaque JSON.
_INTERDICTION_LABEL_TO_IID = {
    "chalutage de fond":            "I001",
    "chasse à la baleine":          "I002",
    "construction sur le littoral": "I003",
    "extraction de sable":          "I004",
    "chasse des oiseaux marins":    "I005",
    "rejet d'hydrocarbures":        "I006",
}


def _guess_iid_from_content(data: dict, filename: str) -> str:
    """
    Détermine l'IID (I001–I006) à partir du champ 'interdiction'
    présent dans le JSON. Fallback sur le nom de fichier.
    """
    label = (data.get("interdiction") or "").strip().lower()
    for key, iid in _INTERDICTION_LABEL_TO_IID.items():
        if key in label:
            return iid
    # Fallback: extraction du numéro du nom de fichier
    match = re.search(r"(\d{2})", filename)
    if match:
        return f"I0{match.group(1)}"
    return "UNKNOWN"


def load_synonyms_hypernyms(syn_dir: Path) -> Dict[str, Dict[str, Any]]:
    """
    Charge les fichiers de Synonyme et hyperonymes/.
    Retourne { interdiction_id: { "interdiction": str, "synonymes": [...], "hyperonymes": [...] } }

    Le mapping fichier → IID est basé sur le champ "interdiction" du JSON,
    pas sur le numéro du fichier (03_extraction_de_sable → I004, pas I003).
    """
    result: Dict[str, Dict[str, Any]] = {}
    if not syn_dir.exists():
        logger.warning(f"  ⚠️ Dossier Synonymes non trouvé : {syn_dir}")
        return result

    files = sorted(syn_dir.glob("*.json"))
    logger.info(f"  📚 {len(files)} fichier(s) de synonymes trouvé(s) dans {syn_dir}")

    for fpath in files:
        try:
            data = load_json(fpath)
            iid = _guess_iid_from_content(data, fpath.name)
            interdiction_label = (data.get("interdiction") or fpath.stem).strip()
            result[iid] = {
                "interdiction": interdiction_label,
                "synonymes": data.get("synonymes", []),
                "hyperonymes": data.get("hyperonymes", [])
            }
            logger.info(
                f"    📄 {fpath.name}: \"{interdiction_label}\" → {iid} "
                f"({len(result[iid]['synonymes'])} syn, {len(result[iid]['hyperonymes'])} hyp)"
            )
        except Exception as e:
            logger.warning(f"  ⚠️ Impossible de lire {fpath.name}: {e}")

    return result
"""
pdf_extractor.py — Extraction et preprocessing des PDFs du corpus maritime.
"""
import logging
import json
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import fitz  # PyMuPDF

from rag.config import (
    RAG_DATA_DIR, CHUNKS_DIR, CATEGORIES,
    PDF_CONFIG, EXTRACTION_CONFIG
)

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extraction de texte depuis les PDFs avec gestion des métadonnées."""

    def __init__(self):
        self.chunk_size = PDF_CONFIG["chunk_size"]
        self.chunk_overlap = PDF_CONFIG["chunk_overlap"]
        self.min_chunk_length = PDF_CONFIG["min_chunk_length"]
        self.extracted_chunks = []
        self.chunk_id_counter = 0
        # Déduplication cross-catégories : hashes MD5 des textes déjà vus
        self._seen_hashes = set()

    # ─────────────────────────────────────────────────────────────────────
    #  EXTRACTION
    # ─────────────────────────────────────────────────────────────────────

    def extract_text_from_pdf(self, pdf_path: Path, category: str, country: str) -> List[Dict]:
        """Extrait le texte et les TABLEAUX d'un PDF page par page."""
        # Rendre MuPDF silencieux pour les erreurs d'annotations non supportées
        try:
            fitz.TOOLS.mupdf_display_errors(False)
        except:
            pass

        texts = []
        try:
            doc = fitz.open(str(pdf_path))
            logger.info(f"Traitement: {pdf_path.name} ({len(doc)} pages)")

            for page_num in range(len(doc)):
                try:
                    page = doc[page_num]
                    
                    # 1. Détecter et extraire les tableaux en Markdown
                    tables_md = self._extract_tables_as_markdown(page)
                    
                    # 2. Extraire le texte avec votre méthode "parfaite" (get_text("text"))
                    # C'est la plus robuste pour garder l'ordre des articles
                    page_text = page.get_text("text")
                    
                    # 3. Assembler le texte de la page et les tableaux Markdown
                    if tables_md:
                        page_text += "\n\n### [TABLEAUX DÉTECTÉS]\n" + "\n\n".join(tables_md)
                    
                    if page_text.strip():
                        page_text = self._clean_text(page_text)
                        texts.append({
                            "text": page_text,
                            "page": page_num + 1
                        })
                except Exception as e:
                    logger.warning(f"Erreur page {page_num + 1}: {e}")
                    continue

            doc.close()

        except Exception as e:
            logger.error(f"Erreur extraction {pdf_path.name}: {e}")

        return texts

    def _extract_tables_as_markdown(self, page) -> List[str]:
        """Détecte et convertit les tableaux d'une page en Markdown."""
        md_tables = []
        try:
            # find_tables est dispo depuis PyMuPDF 1.23.0
            tabs = page.find_tables()
            for table in tabs.tables:
                rows = table.extract()
                if not rows or len(rows) < 1:
                    continue
                
                # Conversion manuelle en Markdown (plus robuste que de dépendre de pandas/tabulate)
                md = self._rows_to_markdown(rows)
                if md:
                    md_tables.append(md)
        except Exception as e:
            # Fail silently if old version or error
            pass
        return md_tables

    def _is_bbox_inside(self, child, parent, tolerance=2):
        """Vérifie si une zone (bbox) est contenue dans une autre."""
        return (child[0] >= parent[0] - tolerance and 
                child[1] >= parent[1] - tolerance and
                child[2] <= parent[2] + tolerance and 
                child[3] <= parent[3] + tolerance)

    def _rows_to_markdown(self, rows: List[List[str]]) -> str:
        """Convertit une liste de listes en tableau Markdown propre."""
        if not rows or not rows[0]:
            return ""
            
        # Nettoyer les cellules (enlever les sauts de ligne internes)
        clean_rows = []
        for r in rows:
            clean_rows.append([cell.replace('\n', ' ').strip() if cell else "" for cell in r])
            
        # Créer l'entête
        header = "| " + " | ".join(clean_rows[0]) + " |"
        separator = "| " + " | ".join(["---"] * len(clean_rows[0])) + " |"
        
        # Créer les lignes de données
        body = []
        for r in clean_rows[1:]:
            body.append("| " + " | ".join(r) + " |")
            
        return "\n".join([header, separator] + body)

    def _clean_text(self, text: str) -> str:
        """
        Nettoyage NON-destructif adapté aux textes juridiques.
        Conserve : n°, %, apostrophes, accents, références (art. 12.3, règl. 1.2)
        Supprime  : artefacts PDF uniquement (césures, headers, espaces multiples)
        """
        # Normaliser fins de ligne
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # 2. Supprimer les en-têtes et pieds de page récurrents (JO, codes, dates)
        text = re.sub(r'JOURNAL OFFICIEL.*?\n', '', text, flags=re.IGNORECASE)
        text = re.sub(r'République Islamique.*?\n', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Texte\s+\d+\s+sur\s+\d+.*?\n', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Page\s+\d+\s+/\s+\d+.*?\n', '', text, flags=re.IGNORECASE)
        text = re.sub(r'n°\s+du\s+\d+/\d+/\d+.*?\n', '', text, flags=re.IGNORECASE)

        # Recoller les césures de fin de ligne (ex: "ap-\nplication" → "application")
        text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)

        # Supprimer les en-têtes/pieds de page récurrents (Journaux Officiels)
        # On cible les lignes qui contiennent ces termes, avec plus de flexibilité sur les espaces
        header_pattern = r'^.*(?:JOURNAL\s+OFFICIEL|J\.?\s*O\.?\s+Sp[eé]cial|R[eé]publique\s+Islamique|R[eé]publique\s+de\s+Guin[eé]e).*$\n?'
        text = re.sub(header_pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)

        # Fusionner les lignes qui prolongent une phrase
        # (préserve les doubles sauts = vrais séparateurs d'alinéas)
        # Utilisation de flags explicites pour éviter les erreurs de positionnement de flags inline
        text = re.sub(r'(?<!\n)\n(?!\n)(?![A-ZVUÀ-Ö])', ' ', text)

        # Normaliser espaces multiples sans toucher aux sauts de ligne
        text = re.sub(r'[ \t]{2,}', ' ', text)

        # Uniformiser tirets longs
        text = text.replace('–', '-').replace('—', '-')

        # 3. Corrections "OCR" courantes pour les textes juridiques
        text = text.replace("!'", "l'")
        text = text.replace("I' ", "l'")
        text = re.sub(r'\bmin\s+istre\b', 'ministre', text, flags=re.IGNORECASE)
        text = re.sub(r'n[]\s*', 'n° ', text)
        
        # Supprimer les fragments de bruit isolés (ex: " I -, ") souvent issus de bordures de PDF
        text = re.sub(r'\n\s*[I\-,]{1,3}\s*\n', '\n', text)

        return text.strip()

    # ─────────────────────────────────────────────────────────────────────
    #  CHUNKING
    # ─────────────────────────────────────────────────────────────────────

    def chunk_text(self, pages_data: List[Dict], pdf_name: str,
                   category: str, country: str) -> List[Dict]:
        """
        Chunking par unité légale (Article / Règle / Chapitre / Section).

        Stratégie :
          1. Ignorer le préambule (tout ce qui précède le premier Article)
             → pas pertinent pour les questions de type "qu'interdit l'article X ?"
          2. Découper sur les marqueurs de structure légale
          3. Si une unité dépasse chunk_size → sous-découpage par alinéa avec overlap
        """
        chunks = []

        full_text = "\n\n".join([p["text"] for p in pages_data])
        if not full_text.strip():
            return chunks

        # On cherche le premier Article ou la première Règle (doit être en début de ligne)
        first_marker_pattern = r'^(?:\s*)(?:art(?:icle|\.)\s*(?:l?er|1er|\d+)|r[eè]gle\s+\d+)'
        first_marker = re.search(first_marker_pattern, full_text, flags=re.IGNORECASE | re.MULTILINE)
        
        if first_marker:
            start_body = first_marker.start()
        else:
            logger.info(f"{pdf_name}: aucun Article ou Règle détecté, traitement par défaut.")
            start_body = 0

        # ── Extraction du vrai titre du document depuis le préambule ───────
        # On utilise simplement le nom du fichier comme titre du document
        doc_title = pdf_name.replace(".pdf", "")

        body = full_text[start_body:]

        # ── Pattern de structure légale ───────────────────────────────────
        pattern = re.compile(
            r"""
            (?P<titre>     \btitre\s+[IVXLCDM]+\b                               ) |
            (?P<chap>      \bchapitre\s+(?:[IVXLCDM]+|\d+)\b                    ) |
            (?P<sect>      \bsection\s+(?:[IVXLCDM]+|\d+)\b                     ) |
            (?P<annexe>    \bannexe\s+(?:[IVXLCDM]+|\d+|[A-Z])\b                ) |
            (?P<regle>     \br[eè]gle\s+\d+(?:\.\d+)*\b                         ) |
            (?P<art>
                # Strictement en début de ligne, non précédé de mots de citation (vu, selon, etc.)
                ^(?:\s*)
                art(?:icle|\.)\s*
                (?:l?er|1er|\d+(?:\s*bis|\s*ter)?)
                [\s\.\:\-–]
            )
            """,
            re.VERBOSE | re.IGNORECASE | re.MULTILINE,
        )

        matches = list(pattern.finditer(body))

        if not matches:
            return self._fallback_sentence_chunking(
                body, pages_data, pdf_name, category, country, doc_title=doc_title
            )

        current_hierarchy = {
            "titre": "", "chapitre": "", "section": "",
            "article": "", "annexe": "", "regle": ""
        }

        for i, match in enumerate(matches):
            mtype = match.lastgroup
            # Formatage propre : "Titre I", "Chapitre 1" (évite "Titre i" via .capitalize())
            raw_label = match.group().strip()
            parts = raw_label.split()
            if len(parts) > 1:
                mlabel = parts[0].capitalize() + " " + " ".join(parts[1:])
            else:
                mlabel = raw_label.capitalize()

            # Mettre à jour la hiérarchie (réinitialise les niveaux inférieurs)
            if mtype == "titre":
                current_hierarchy = {k: "" for k in current_hierarchy}
                current_hierarchy["titre"] = mlabel
            elif mtype == "chap":
                current_hierarchy.update({
                    "chapitre": mlabel, "section": "", "article": "", "regle": ""
                })
            elif mtype == "sect":
                current_hierarchy.update({
                    "section": mlabel, "article": "", "regle": ""
                })
            elif mtype == "art":
                current_hierarchy["article"] = mlabel
                current_hierarchy["regle"] = ""
            elif mtype == "regle":
                current_hierarchy["regle"] = mlabel
                current_hierarchy["article"] = ""
            elif mtype == "annexe":
                current_hierarchy["annexe"] = mlabel

            start_pos = match.start()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(body)
            unit_text = body[start_pos:end_pos].strip()

            if not unit_text or len(unit_text) < self.min_chunk_length:
                continue

            page = self._estimate_page(start_pos, body, pages_data)

            if len(unit_text) <= self.chunk_size:
                chunk = self._build_chunk(
                    unit_text, pdf_name, category, country,
                    current_hierarchy.copy(), page, doc_title
                )
                if chunk:
                    chunks.append(chunk)
            else:
                sub = self._fallback_sentence_chunking(
                    unit_text, pages_data, pdf_name, category, country,
                    hierarchy=current_hierarchy.copy(), base_page=page, doc_title=doc_title
                )
                chunks.extend(sub)

        return chunks

    def _fallback_sentence_chunking(self, text: str, pages_data: List[Dict],
                                    pdf_name: str, category: str, country: str,
                                    hierarchy: Optional[Dict] = None,
                                    base_page: Optional[int] = None,
                                    doc_title: str = "") -> List[Dict]:
        """
        Sous-découpage par alinéa puis par phrase avec overlap.
        Appelé quand une unité légale dépasse chunk_size ou quand
        aucune structure n'est détectée.
        """
        chunks = []
        current_page = base_page or (pages_data[0]["page"] if pages_data else 1)

        # Priorité aux séparateurs d'alinéas juridiques (;\n, tiret de liste, double saut)
        alinea_re = re.compile(r'(?:;\s*\n|\n\s*[-–•]\s+|\n{2,})')
        alineas = [a.strip() for a in alinea_re.split(text) if a.strip()]
        if not alineas:
            alineas = re.split(r'(?<=[.!?])\s+', text)

        current_chunk = ""

        for alinea in alineas:
            if len(current_chunk) + len(alinea) + 1 <= self.chunk_size:
                current_chunk = (current_chunk + " " + alinea).strip() if current_chunk else alinea
            else:
                if len(current_chunk) >= self.min_chunk_length:
                    chunk = self._build_chunk(
                        current_chunk, pdf_name, category, country,
                        hierarchy or {}, current_page, doc_title
                    )
                    if chunk:
                        chunks.append(chunk)

                # Overlap : reprendre la fin du chunk précédent
                overlap_size = max(self.chunk_overlap, int(self.chunk_size * 0.1))
                tail = current_chunk[-overlap_size:] if len(current_chunk) > overlap_size else current_chunk
                current_chunk = (tail + " " + alinea).strip()

        if len(current_chunk) >= self.min_chunk_length:
            chunk = self._build_chunk(
                current_chunk, pdf_name, category, country,
                hierarchy or {}, current_page, doc_title
            )
            if chunk:
                chunks.append(chunk)

        return chunks

    def _build_chunk(self, text: str, pdf_name: str, category: str,
                     country: str, hierarchy: Dict, page: int, doc_title: str) -> Optional[Dict]:
        """
        Construit le dictionnaire d'un chunk.

        - 'text'       : texte pur — seul ce champ est vectorisé
        - 'breadcrumb' : contexte lisible injecté dans le prompt LLM
                         (jamais dans le vector store)
        - Déduplication par hash MD5 (cross-catégories)
        """
        text = text.strip()
        if not text:
            return None

        # Déduplication cross-catégories
        content_hash = hashlib.md5(text.encode()).hexdigest()[:12]
        if content_hash in self._seen_hashes:
            return None
        self._seen_hashes.add(content_hash)

        # Quality score
        normative_re = re.compile(
            r'\b(?:interdit[es]?|doit|doivent|obligatoire|sanctionn[ée]e?s?'
            r'|peine|amende|emprisonnement|infraction|autoris[ée]e?s?)\b',
            re.IGNORECASE,
        )
        quality = 1.0
        if len(text.split()) < 15:
            quality -= 0.4
        if not normative_re.search(text):
            quality -= 0.15
        quality = round(max(0.0, min(1.0, quality)), 2)

        # Breadcrumb pour le prompt LLM (construit ici, utilisé à la génération)
        # Format premium : [Pays] Titre du Doc | Hiérarchie | Article
        hierarchy_parts = [p for p in [
            hierarchy.get("titre", ""),
            hierarchy.get("chapitre", ""),
            hierarchy.get("section", ""),
            hierarchy.get("article", "") or hierarchy.get("regle", ""),
            hierarchy.get("annexe", ""),
        ] if p]
        
        breadcrumb = f"[{country}] {doc_title}"
        if hierarchy_parts:
            breadcrumb += " | " + " | ".join(hierarchy_parts)

        chunk_dict = {
            "id":           f"{pdf_name.replace('.pdf', '')}_{self.chunk_id_counter:04d}",
            "content_hash": content_hash,
            # ── Texte pur — seul ce champ est vectorisé ──────────────────
            "text":         text,
            # ── Provenance ───────────────────────────────────────────────
            "source":       pdf_name,
            "doc_title":    doc_title,
            "category":     category,
            "country":      country,
            "page":         page,
            # ── Hiérarchie légale (filtrage / KG, pas dans le vecteur) ───
            "titre":        hierarchy.get("titre", ""),
            "chapitre":     hierarchy.get("chapitre", ""),
            "section":      hierarchy.get("section", ""),
            "article":      hierarchy.get("article", "") or hierarchy.get("regle", ""),
            "annexe":       hierarchy.get("annexe", ""),
            # ── Stats ────────────────────────────────────────────────────
            "word_count":   len(text.split()),
            "quality_score": quality,
            # ── Contexte pour le prompt LLM (jamais indexé) ──────────────
            "breadcrumb":   breadcrumb,
        }

        self.chunk_id_counter += 1
        return chunk_dict

    # ─────────────────────────────────────────────────────────────────────
    #  HELPERS
    # ─────────────────────────────────────────────────────────────────────

    def _estimate_page(self, char_pos: int, body: str, pages_data: List[Dict]) -> int:
        """Estime le numéro de page à partir de la position dans le texte fusionné."""
        if not pages_data:
            return 1
        cumulative = 0
        for p in pages_data:
            cumulative += len(p["text"])
            if char_pos <= cumulative:
                return p["page"]
        return pages_data[-1]["page"]

    def extract_country_code(self, filename: str) -> str:
        """Extrait le code pays du nom du fichier."""
        match = re.match(r'([a-zA-Z]+)', filename)
        return match.group(1).capitalize() if match else "Unknown"

    # ─────────────────────────────────────────────────────────────────────
    #  ORCHESTRATION
    # ─────────────────────────────────────────────────────────────────────

    def process_all_pdfs(self) -> Tuple[List[Dict], Dict]:
        """Traite tous les PDFs du corpus."""
        all_chunks = []
        stats = {
            "total_pdfs": 0,
            "successful": 0,
            "failed": 0,
            "total_chunks": 0,
            "by_category": {}
        }

        for category in CATEGORIES:
            category_path = RAG_DATA_DIR / category
            if not category_path.exists():
                logger.warning(f"Dossier non trouvé: {category}")
                continue

            stats["by_category"][category] = {
                "pdfs": 0,
                "chunks": 0,
                "total_words": 0
            }

            pdf_files = list(category_path.glob("*.pdf"))
            logger.info(f"\n{'='*60}")
            logger.info(f"Traitement catégorie: {category} ({len(pdf_files)} PDFs)")
            logger.info(f"{'='*60}")

            for pdf_file in pdf_files:
                stats["total_pdfs"] += 1
                country = self.extract_country_code(pdf_file.name)

                try:
                    pages_data = self.extract_text_from_pdf(pdf_file, category, country)
                    if not pages_data:
                        logger.warning(f"Aucun texte extrait: {pdf_file.name} (Le PDF est peut-être une image scannée)")
                        stats["failed"] += 1
                        continue

                    chunks = self.chunk_text(pages_data, pdf_file.name, category, country)
                    if chunks:
                        all_chunks.extend(chunks)
                        stats["successful"] += 1
                        stats["by_category"][category]["pdfs"] += 1
                        stats["by_category"][category]["chunks"] += len(chunks)
                        stats["by_category"][category]["total_words"] += sum(
                            c["word_count"] for c in chunks
                        )
                        logger.info(f"[OK] {pdf_file.name}: {len(chunks)} chunks")
                    else:
                        logger.warning(f"Pas de chunks: {pdf_file.name}")
                        stats["failed"] += 1

                except Exception as e:
                    logger.error(f"Erreur {pdf_file.name}: {e}")
                    stats["failed"] += 1

        stats["total_chunks"] = len(all_chunks)
        return all_chunks, stats

    def save_chunks(self, chunks: List[Dict], output_file: str = "all_chunks.json"):
        """Sauvegarde les chunks en JSON."""
        output_path = CHUNKS_DIR / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        logger.info(f"Chunks sauvegardés: {output_path}")
        return output_path
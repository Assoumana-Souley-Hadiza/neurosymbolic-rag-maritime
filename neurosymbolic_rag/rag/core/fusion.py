import logging
import re  # ← Remonté au niveau global
from typing import List, Dict, Optional, Set
from rag.config import RERANKER_CONFIG
logger = logging.getLogger(__name__)
class CrossEncoderReranker:
    """
    Reranker Cross-Encoder avec support des termes techniques expansés.
    """
    def __init__(self):
        self.model_name = RERANKER_CONFIG.get("model_name", "BAAI/bge-reranker-v2-m3")
        self.device = RERANKER_CONFIG.get("device", "cpu")
        self.model = None
        self._load_model()
    def _load_model(self):
        try:
            from sentence_transformers import CrossEncoder
            logger.info(f"[Reranker] Chargement {self.model_name} sur {self.device}...")
            self.model = CrossEncoder(self.model_name, device=self.device)
            logger.info("[Reranker] Modèle chargé.")
        except ImportError:
            logger.warning("[Reranker] 'sentence_transformers' non installé.")
        except Exception as e:
            logger.error(f"[Reranker] Erreur chargement : {e}")
    def rerank(
        self,
        query: str,
        docs: List[Dict],
        top_k: int = 5,
        expanded_terms: Optional[List[str]] = None,
        intent: str = "legal",
    ) -> List[Dict]:
        if not self.model or not docs:
            return docs[:top_k]
        
        clean_query = query
        
        # On n'injecte PLUS les synonymes dans le Reranker.
        # Testé : ajouter un "sac de mots" à une phrase naturelle détruit le score sémantique du CrossEncoder.
        # Par exemple, ajouter "temporaire période durée" fait chuter le score d'un article pertinent de 0.86 à 0.74.
        logger.info(f"[Reranker] Requête pure envoyée au modèle (Intent: {intent}) : «{clean_query}»")
                
        pairs = []
        for doc in docs:
            if doc.get("source_retriever") == "graph":
                text = doc.get("label", "") or doc.get("text", "")
            else:
                text = doc.get("text", "")
            pairs.append([clean_query, text])
        try:
            scores = self.model.predict(pairs)
            for i, doc in enumerate(docs):
                doc["rerank_score"] = float(scores[i])
            return sorted(docs, key=lambda x: (-x.get("rerank_score", 0.0), x.get("id", "")))[:top_k]
        except Exception as e:
            logger.error(f"[Reranker] Erreur inférence : {e}")
            return docs[:top_k]
class HybridFusion:
    """
    Fusion RRF + boost ontologique + protection des matchs techniques.
    """
    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k
        self.reranker = CrossEncoderReranker()
    def _normalize_ocr(self, text: str) -> str:
        """Normalise le texte pour contrer les erreurs d'OCR courantes."""
        if not text:
            return ""
        t = text.lower()
        t = t.replace("œ", "oe").replace("æ", "ae")
        t = t.replace("bceufs", "boeufs")  # ← Nettoyé de sa redondance
        
        t = re.sub(r"[^a-z0-9à-ÿ\s]", " ", t)
        return " ".join(t.split())
    def fuse(
        self,
        retriever_results:  Dict[str, List[Dict]],
        weights:            Dict[str, float],
        synonym_sets:       Optional[Dict[str, Set[str]]] = None,
        graph_entities:     Optional[Set[str]] = None,
        ontology_boost:     float = 0.05,
        top_k:              int = 5,
        country_filter:     Optional[str] = None,
        category_filter:    Optional[str] = None,
        query:              Optional[str] = None,
        expanded_terms:     Optional[List[str]] = None,
        original_query_terms: Optional[List[str]] = None,
        intent:             Optional[str] = None,
        disable_reranker:   bool = False,
    ) -> List[Dict]:
        
        if synonym_sets is None:
            synonym_sets = {}
            if graph_entities:
                for ent in graph_entities:
                    synonym_sets[ent] = {ent}
        all_boost_terms: Set[str] = set()
        for syns in synonym_sets.values():
            for s in syns:
                if s and len(s.strip()) > 2:
                    all_boost_terms.add(s.lower().strip())
        original_terms_lower: Set[str] = set()
        if original_query_terms:
            original_terms_lower = {t.lower() for t in original_query_terms if t}
        elif query:
            original_terms_lower = {
                w.lower() for w in re.findall(r"[a-zà-ÿ]{3,}", query)
            }
        # Blacklist de termes trop génériques qui ne doivent JAMAIS déclencher 
        # un technical_hit pur (ils donnent juste un boost normal)
        GENERIC_BLACKLIST = {
            "protection spéciale", "domaine public", 
            "domaine public maritime", "milieu marin", "environnement marin",
            "zone protégée", "activités maritimes",
            "aires protégées", "zone sensible", "faune sauvage", "flore sauvage"
        }
        
        technical_terms: Set[str] = {
            t for t in all_boost_terms
            if t.lower() not in original_terms_lower and t.lower() not in GENERIC_BLACKLIST
        }
        logger.info(f"[Fusion] Termes techniques (expansion pure) : {technical_terms}")
        # ── 1. Calcul RRF pondéré ───────────────────────────────────────────
        fusion_scores:   Dict[str, float] = {}
        all_docs:        Dict[str, Dict]  = {}
        doc_sources:     Dict[str, List[str]] = {}
        technical_hits:  Dict[str, Set[str]] = {}
        for retriever_name, results in retriever_results.items():
            weight = weights.get(retriever_name, 1.0)
            for result in results:
                doc_id = result["id"]
                if country_filter and result.get("source_retriever") != "graph":
                    doc_country = result.get("country") or result.get("metadata", {}).get("country", "")
                    if doc_country:
                        doc_country = str(doc_country).lower().strip()
                        if doc_country != country_filter.lower().strip():
                            continue
                if category_filter and result.get("source_retriever") != "graph":
                    doc_category = result.get("category") or result.get("metadata", {}).get("category", "")
                    if doc_category:
                        doc_category = str(doc_category).lower().strip()
                        if doc_category != category_filter.lower().strip():
                            continue
                rank = result["rank"]
                rrf_score = weight / (self.rrf_k + rank)
                fusion_scores[doc_id] = fusion_scores.get(doc_id, 0.0) + rrf_score
                if doc_id not in all_docs:
                    all_docs[doc_id] = result
                doc_sources.setdefault(doc_id, []).append(retriever_name)
        # ── 2. Détection des technical_hits + boost additif + BOOST INTENT ───
        BOOST_TECHNICAL = 0.40
        BOOST_GENERAL   = 0.10
        BOOST_MAX       = 0.60
        BOOST_INTENT    = 0.20  # Boost spécifique à l'intention

        # Définition des mots-clés liés à l'intention
        intent_keywords = set()
        if intent == "controle_institution":
            intent_keywords = {"contrôle", "inspection", "surveillance", "agent", "assermenté", "visite", "police"}
        elif intent == "sanction_penale":
            intent_keywords = {"emprisonnement", "prison", "mois", "ans", "peine", "puni", "réclusion"}
        elif intent == "sanction_financiere":
            intent_keywords = {"amende", "francs", "cfa", "montant", "pénalité"}
        elif intent == "condition_temporelle":
            intent_keywords = {"temporaire", "période", "durée", "suspendu", "exceptionnel","saison"}
        elif intent == "condition_spatiale":
            intent_keywords = {"zone", "aire", "région", "territoire", "réserve", "parc", "domaine"}
        elif intent == "exception":
            intent_keywords = {"autoriser", "exception", "dérogation" ,"autorisation"}

        if all_boost_terms or intent_keywords:
            normalized_technical = {self._normalize_ocr(t) for t in technical_terms if t}
            normalized_general   = {self._normalize_ocr(t) for t in all_boost_terms if t and t not in technical_terms}
            normalized_intent    = {self._normalize_ocr(t) for t in intent_keywords if t}

            noise = {"zone", "dans", "pour", "avec", "article", "texte", "document", "national", "litto"}

            for doc_id in list(fusion_scores.keys()):
                doc_data = all_docs.get(doc_id)
                if not doc_data:
                    continue

                text_raw = doc_data.get("text", "")
                text_norm = self._normalize_ocr(text_raw)
                n_technical = 0.0
                n_general = 0.0
                has_intent = False
                found_technical: Set[str] = set()

                # 1. Boost lié à l'intention de la question
                for t in normalized_intent:
                    if t in text_norm:
                        has_intent = True
                        found_technical.add(f"intent:{t}")
                        break

                # 2. Boost lié à l'ontologie
                for term in all_boost_terms:
                    term_norm = self._normalize_ocr(term)

                    if term_norm in text_norm:
                        is_technical = term_norm in normalized_technical
                        if is_technical:
                            n_technical += 1.0
                            found_technical.add(term)
                        else:
                            n_general += 1.0
                        continue

                    # Match partiel sur mots rares
                    words_to_check = (w for w in term_norm.split() if len(w) > 4 and w not in noise)
                    for word in words_to_check:
                        if word in text_norm:
                            # Un seul mot qui matche ne doit PAS déclencher un technical_hit,
                            # sinon le mot "maritime" protège la moitié des documents !
                            n_general += 0.25 
                            break

                import math
                accumulated_boost = 0.0
                if has_intent:
                    accumulated_boost += BOOST_INTENT
                if n_technical > 0:
                    accumulated_boost += BOOST_TECHNICAL * math.log2(1 + n_technical)
                if n_general > 0:
                    accumulated_boost += BOOST_GENERAL * math.log2(1 + n_general)

                if accumulated_boost > 0:
                    fusion_scores[doc_id] += min(accumulated_boost, BOOST_MAX + BOOST_INTENT)

                if found_technical:
                    technical_hits[doc_id] = found_technical
                    logger.info(
                        f"[Fusion] ⚡ Technical hit sur '{doc_id}' "
                        f"— termes : {found_technical} "
                        f"— score RRF+boost : {fusion_scores[doc_id]:.4f}"
                    )
        # ── 3. Tri pré-rerank ────────────────────────────────────────────────
        sorted_docs = sorted(fusion_scores.items(), key=lambda x: (-x[1], x[0]))
        pre_rerank_k = 30
        pre_rerank_results = []
        for doc_id, score in sorted_docs[:pre_rerank_k]:
            doc = all_docs[doc_id].copy()
            doc["hybrid_score"]      = score
            doc["retriever_sources"] = doc_sources.get(doc_id, [])
            doc["multi_retriever"]   = len(doc["retriever_sources"]) > 1
            doc["technical_hit"]     = bool(technical_hits.get(doc_id))
            doc["technical_terms"]   = sorted(list(technical_hits.get(doc_id, set())))
            pre_rerank_results.append(doc)
        if query and self.reranker.model and not disable_reranker:
            reranked = self.reranker.rerank(
                query=query,
                docs=pre_rerank_results,
                top_k=top_k,
                expanded_terms=expanded_terms,
                intent=intent,
            )
            # ── 5. Protection post-rerank des technical_hits ─────────────────
            final_results = self._protect_technical_hits(
                reranked_docs=reranked,
                pre_rerank_docs=pre_rerank_results,
                top_k=top_k,
                intent=intent,
            )
            logger.info(
                f"[Fusion/Reranked] {len(final_results)} résultats | "
                f"technical_hits={len(technical_hits)} | pays={country_filter}"
            )
        else:
            final_results = pre_rerank_results[:top_k]
            logger.info(
                f"[Fusion/RRF] {len(final_results)} résultats | "
                f"technical_hits={len(technical_hits)} | pays={country_filter}"
            )
        return final_results
    # ════════════════════════════════════════════════════════════════════════
    # PROTECTION POST-RERANK (CORRIGÉE)
    # ════════════════════════════════════════════════════════════════════════
    def _protect_technical_hits(
        self,
        reranked_docs: List[Dict],
        pre_rerank_docs: List[Dict],
        top_k: int,
        intent: Optional[str] = None,
    ) -> List[Dict]:
        """
        Garantit qu'un document avec un technical_hit et un bon score RRF
        ne peut pas être évincé du top-K par un document générique, SAUF pour 
        les questions complexes où on fait confiance au Reranker à 100%.
        """
        if not reranked_docs:
            return reranked_docs
        complex_intents = {
            "sanction_penale", "sanction_financiere", 
            "condition_temporelle", "condition_spatiale", 
            "controle_institution", "exploratory"
        }
        if intent and intent in complex_intents:
            logger.info(f"[Fusion] Protection technique désactivée car l'intention est complexe ({intent}). Reranker prioritaire.")
            return reranked_docs[:top_k]
        final = list(reranked_docs)  # Copie de taille top_k maximum
        top_k_ids = {d["id"] for d in final[:top_k]}
        missing_hits = [
            d for d in pre_rerank_docs
            if d.get("technical_hit") and d["id"] not in top_k_ids
        ]
        if missing_hits:
            missing_hits.sort(key=lambda x: x.get("hybrid_score", 0), reverse=True)
            for hit_doc in missing_hits:
                hit_score = hit_doc.get("hybrid_score", 0)
                if len(final) >= top_k:
                    last_in_topk_score = final[top_k - 1].get("hybrid_score", 0)
                else:
                    break
                # Seuil de compétitivité RRF
                if hit_score > last_in_topk_score * 0.5:
                    # Chercher le dernier document NON-technique présent dans le top-K
                    swap_idx = None
                    for i in range(min(len(final), top_k) - 1, -1, -1):
                        if not final[i].get("technical_hit"):
                            swap_idx = i
                            break
                    if swap_idx is not None:
                        # CORRECTION : Remplacement direct par index (écrase le doc générique ciblé)
                        hit_doc_copy = hit_doc.copy()
                        hit_doc_copy["protected_by_technical_hit"] = True
                        final[swap_idx] = hit_doc_copy
                        
                        logger.info(
                            f"[Fusion] 🛡️ Protection technical_hit : "
                            f"'{hit_doc['id']}' a remplacé le document générique en position {swap_idx + 1} "
                            f"(score RRF={hit_score:.4f})"
                        )
                        break  # Un seul remplacement par passe
                    
        # ── PROPULSION EN HAUT DE LISTE ──
        # Tous les documents du top-K final qui ont un technical_hit
        # DOIVENT être placés en tête de liste pour que le LLM les lise en premier !
        final_top_k = final[:top_k]
        
        # PENALISATION DES FAUX POSITIFS DU RERANKER
        # Si l'ontologie a trouvé un match technique exact, on pénalise drastiquement
        # les autres documents qui n'ont fait qu'un match lexical, pour éviter que le LLM
        # ne soit distrait par un faux positif avec un gros rerank_score.
        has_tech_hit = any(d.get("technical_hit", False) or d.get("protected_by_technical_hit", False) for d in final_top_k)
        if has_tech_hit:
            for d in final_top_k:
                if not (d.get("technical_hit", False) or d.get("protected_by_technical_hit", False)):
                    # Pénalité agressive : on divise par 20 pour faire passer sous le seuil de 0.10
                    if "rerank_score" in d:
                        d["rerank_score"] *= 0.05
                    if "hybrid_score" in d:
                        d["hybrid_score"] *= 0.05
        
        # On trie d'abord par présence de technical_hit (True avant False),
        # puis par leur score de rerank originel pour conserver l'ordre intelligent de BGE-M3.
        final_top_k.sort(key=lambda d: (d.get("technical_hit", False) or d.get("protected_by_technical_hit", False), d.get("rerank_score", 0.0)), reverse=True)
        
        return final_top_k
import logging
import os
from typing import List, Dict, Any, Tuple, Optional
logger = logging.getLogger(__name__)
# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Tu es un assistant juridique. Réponds à la question en te basant  sur les documents fournis.
Si un bloc [ENRICHISSEMENT ONTOLOGIQUE] est présent, utilise-le pour identifier l'article pertinent.
Tu DOIS recopier l'en-tête du document que tu cites, tel qu'il apparaît  dans le bloc correspondant.
Format de réponse :
OUI, il existe un article portant sur [réponse courte et directe à la question posée]. Selon [recopie l'en-tête du document entre crochets], "[CITATION EXACTE]".
NON, il n'existe pas d'article portant sur [sujet] dans les textes fournis.
"""
# Score minimum de pertinence pour qu'un document soit envoyé au LLM.
# Les documents en dessous de ce seuil sont du bruit et risquent de provoquer
# des hallucinations sur un modèle 3B avec seulement 4K tokens de contexte.
_MIN_RELEVANCE_SCORE = 0.10
# ─────────────────────────────────────────────────────────────────────────────
# SÉPARATION PDF vs GRAPH
# ─────────────────────────────────────────────────────────────────────────────
def _split_docs(documents: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """Sépare les documents PDF (source de réponse) des documents
    graph/ontologie (enrichissement de la requête uniquement)."""
    pdf_docs, graph_docs = [], []
    for doc in documents:
        source = doc.get("metadata", {}).get("source", "")
        is_graph = (
            doc.get("source_retriever") == "graph"
            or any(x in source.lower() for x in ["neo4j", "ontology", "graph", "generic", "activity"])
        )
        if is_graph:
            graph_docs.append(doc)
        else:
            pdf_docs.append(doc)
    logger.debug(
        "Split docs → %d PDF, %d graph",
        len(pdf_docs),
        len(graph_docs),
    )
    logger.debug(
        "Chemins PDF envoyés au LLM : %s",
        [d.get("metadata", {}).get("breadcrumb", "?") for d in pdf_docs],
    )
    return pdf_docs, graph_docs
# ─────────────────────────────────────────────────────────────────────────────
# FORMATAGE DES DOCUMENTS PDF
# ─────────────────────────────────────────────────────────────────────────────
def _format_pdf_doc(index: int, doc: Dict, use_breadcrumb: bool = True) -> str:
    """Formate un document PDF (texte juridique source de réponse).
    Inclut explicitement le champ 'annexe' dans le chemin si présent,
    pour que le LLM puisse identifier et citer les annexes."""
    text = doc.get("text", "").strip()
    
    if not use_breadcrumb:
        return f"── Document {index} ──\n{text}"
    meta = doc.get("metadata", {})
    breadcrumb = meta.get("breadcrumb") or meta.get("chemin") or meta.get("path", "")
    annexe = meta.get("annexe", "") or doc.get("annexe", "")
    if breadcrumb:
        chemin_str = f"[{breadcrumb}]"
        if annexe and annexe.lower() not in breadcrumb.lower():
            chemin_str = f"[{breadcrumb} | {annexe}]"
    else:
        source = meta.get("source", "").replace(".pdf", "")
        country = meta.get("country", "").capitalize()
        titre = meta.get("titre", "")
        chapitre = meta.get("chapitre", "")
        section = meta.get("section", "")
        article = meta.get("article", "")
        
        parts = [f"[{country[:3]}] {source}"]
        if titre: parts.append(titre)
        if chapitre: parts.append(chapitre)
        if section: parts.append(section)
        if article: parts.append(article)
        if annexe: parts.append(annexe)
        
        ref = " | ".join(p for p in parts if p.strip(" ."))
        chemin_str = f"[{ref}]"
    doc_type = "Annexe" if annexe else "Document"
    text = doc.get("text", "").strip()
    return f"── {doc_type} {index} : {chemin_str} ──\n{text}"
# ─────────────────────────────────────────────────────────────────────────────
# CONSTRUCTION DU PROMPT UTILISATEUR
# ─────────────────────────────────────────────────────────────────────────────
# Nombre maximum de documents PDF transmis au LLM.
# Augmenté à 5 car 5 chunks juridiques rentrent largement dans les 4096 tokens du modèle 3B.
_MAX_PDF_DOCS = 5

def _extract_enrichment(graph_docs: List[Dict]) -> str:
    if not graph_docs: return ""
    return "\n".join(d.get("text", "") for d in graph_docs)

def build_user_prompt(
    query: str,
    documents: List[Dict],
    enriched_context: Any = None,
    country: str = "",
    use_breadcrumb: bool = True,
    intent: str = "",
) -> str:
    """Construit le prompt final."""
    pdf_docs, graph_docs = _split_docs(documents)
    # 1. Bloc d'enrichissement sémantique (via OntologyAgent ou graph_docs)
    ontology_block = ""
    if enriched_context and hasattr(enriched_context, "to_prompt_block"):
        ontology_block = enriched_context.to_prompt_block()
    elif graph_docs:
        ontology_block = _extract_enrichment(graph_docs)

    # 2. Bloc des textes juridiques — filtrage par score + limite _MAX_PDF_DOCS
    # Étape cruciale : on ne garde que les documents au-dessus du seuil de pertinence
    # pour éviter que le modèle 3B s'accroche à un passage non pertinent,
    # SAUF s'ils ont un technical_hit (protection ontologique).
    scored_pdf = [
        d for d in pdf_docs
        if d.get("technical_hit", False) or d.get("rerank_score", d.get("hybrid_score", d.get("score", 1.0))) >= _MIN_RELEVANCE_SCORE
    ]
    
    if not scored_pdf and pdf_docs:
        best = max(
            pdf_docs,
            key=lambda d: d.get("rerank_score", d.get("hybrid_score", d.get("score", 0.0)))
        )
        scored_pdf = [best]
        logger.info(
            "[Prompt] Fallback : 1 document envoyé (score=%.3f, seuil=%.2f)",
            best.get("rerank_score", best.get("hybrid_score", best.get("score", 0.0))),
            _MIN_RELEVANCE_SCORE,
        )
    selected_pdf = scored_pdf[:_MAX_PDF_DOCS]
    docs_block = "\n\n".join(
        _format_pdf_doc(i, d, use_breadcrumb=use_breadcrumb) for i, d in enumerate(selected_pdf, 1)
    )
    if len(scored_pdf) < len(pdf_docs):
        logger.info(
            "[Prompt] %d/%d documents filtrés (score < %.2f)",
            len(pdf_docs) - len(scored_pdf), len(pdf_docs), _MIN_RELEVANCE_SCORE,
        )
    if len(pdf_docs) > _MAX_PDF_DOCS:
        logger.warning(
            "%d documents PDF disponibles mais seulement %d transmis au LLM "
            "(augmenter _MAX_PDF_DOCS si des articles pertinents sont manqués).",
            len(pdf_docs),
            _MAX_PDF_DOCS,
        )
    country_note = f"\nCONTEXTE : Pays concerné = {country.upper()}.\n" if country else ""
    intent_rules = {
        "sanction_financiere": (
            "Type de disposition recherchée : SANCTION FINANCIÈRE / AMENDE. "
            "L'article attendu doit mentionner explicitement une amende ou une pénalité financière ET s'appliquer spécifiquement à l'objet de la question ou à la catégorie générale à laquelle il appartient. "
            "Si l'article décrit une amende pour une autre infraction hors sujet, ignore-le."
            "Si aucune sanction pécuniaire n'est mentionnée pour ce cas, indiquez que la condition n'est pas remplie."
        ),
        "sanction_penale": (
            "Type de disposition recherchée : SANCTION PÉNALE. "
            "L'article attendu doit mentionner explicitement une peine de prison ou d'emprisonnement ET s'appliquer spécifiquement à l'objet de la question ou à la catégorie générale à laquelle il appartient. "
            "Si un article énonce une peine de prison mais régit un tout autre domaine, tu dois l'ignorer. "
            "Si aucune peine privative de liberté n'est applicable à ce cas précis, indiquez que la condition n'est pas remplie."
        ),
        "condition_temporelle": (
            "Type de disposition recherchée : INTERDICTION NON PERMANENTE / TEMPORALITÉ. "
            "L'article attendu doit mentionner une condition de temps (ex: fermeture saisonnière, période de repos biologique, suspension momentanée) ET s'appliquer à l'objet de la question. "
            "Si l'interdiction est absolue (en tout temps), indiquez que la condition n'est pas remplie."
        ),
        "condition_spatiale": (
            "Type de disposition recherchée : RESTRICTION SPATIALE / ZONAGE. "
            "L'article attendu doit mentionner une zone, aire ou région SPÉCIFIQUE ET LIMITÉE à laquelle l'interdiction s'applique exclusivement. "
            "Attention : si l'article dit 'en tous lieux', 'sur tout le territoire', 'dans toutes les eaux', ou s'applique sans restriction géographique locale, cela signifie que l'interdiction couvre TOUT (il n'y a PAS de restriction)."
        ),
        "controle_institution": (
            "Type de disposition recherchée : PROCÉDURE DE CONTRÔLE / INSPECTION. "
            "L'article attendu doit décrire explicitement un mécanisme d'inspection, de vérification ou de surveillance par des agents ou institutions. "
            "Si l'article se contente d'énoncer une interdiction ou une règle sans expliquer COMMENT le contrôle est effectué, indiquez que la condition n'est pas remplie."
        ),
        "exception": (
            "Type de disposition recherchée : EXCEPTION / DÉROGATION. "
            "L'article attendu doit mentionner explicitement une exception, une dérogation, ou un cas particulier où la règle ou l'interdiction NE s'applique PAS. "
            "Attention aux contraintes de la question (ex: 'ne pas inclure les délais' ou 'autres domaines que la santé'). "
            "Si aucune exception valide n'est mentionnée, indiquez que la condition n'est pas remplie."
        )
    }
    intent_note = ""
    disposition_hint = intent_rules.get(intent)
    if disposition_hint:
        intent_note = f"\n[ATTENTION - RÈGLE DE VALIDATION STRICTE]\n{disposition_hint}\nSi le texte fourni ne remplit pas EXACTEMENT cette condition, tu DOIS impérativement répondre par NON.\n"
    return f"""Question : {query}
{country_note}
{intent_note}
{ontology_block}
Documents :
{docs_block}
Cite un seul article, le plus pertinent. Réponds en un seul paragraphe sans retour à la ligne en respectant le format de réponse.Tu DOIS recopier l'en-tête du document que tu cites, tel qu'il apparaît dans le bloc correspondant et citer le texte exact de l'article.
"""
# ─────────────────────────────────────────────────────────────────────────────
# CLASSE PRINCIPALE
# ─────────────────────────────────────────────────────────────────────────────
class LLMGenerator:
    def __init__(self, model_name: Optional[str] = None):
        # Desactivation de Groq (grok) pour test en local avec Ollama
        # self.api_key = os.getenv("GROQ_API_KEY")
        self.api_key = None
        self.client: Any = None
        
        # Mode Ollama force pour test en local
        import ollama
        self.client = ollama  # type: ignore
        # Priorite a l'environnement OLLAMA_MODEL, sinon llama3.2:3b
        self.model_name = model_name or os.getenv("OLLAMA_MODEL") or "llama3.2:3b"
        self._call = self._call_ollama
    def is_ollama_available(self) -> bool:
        if self.api_key:
            return True
        try:
            import ollama
            ollama.list()
            return True
        except Exception:
            return False
    def _call_groq(self, system: str, user: str, stream: bool) -> Dict:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            stream=stream,
            temperature=0.0,
        )
        if stream:
            return {
                "stream_generator": (
                    chunk.choices[0].delta.content
                    for chunk in response
                    if chunk.choices[0].delta.content is not None
                )
            }
        return {"answer": response.choices[0].message.content}
    def _call_ollama(self, system: str, user: str, stream: bool) -> Dict:
        response = self.client.chat(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            stream=stream,
            options={"temperature": 0.0, "num_ctx": 4096},
        )
        if stream:
            return {"stream_generator": (chunk["message"]["content"] for chunk in response)}
        return {"answer": response["message"]["content"]}
    def generate(
        self,
        query: str,
        fusion_results: List[Dict],
        enriched_context: Any = None,
        stream: bool = False,
        use_breadcrumb: bool = True,
        intent: str = "",
        **_,
    ) -> Dict:
        country = (
            fusion_results[0].get("metadata", {}).get("country", "")
            if fusion_results
            else ""
        )
        
        pdf_docs, graph_docs = _split_docs(fusion_results)
        
        # Court-circuit absolu anti-hallucination : 
        # S'il n'y a VRAIMENT AUCUN document pertinent retourné par les retrievers.
        if not pdf_docs and not graph_docs:
            logger.info("Aucun document retourné par les retrievers. Court-circuit LLM.")
            ans = "NON, il n'existe pas d'article portant sur ce sujet dans les textes fournis."
            res = {
                "system_prompt": SYSTEM_PROMPT,
                "document_context": "Aucun document pertinent."
            }
            if stream:
                res["stream_generator"] = (chunk for chunk in [ans])
            else:
                res["answer"] = ans
            return res
        system = SYSTEM_PROMPT
        user   = build_user_prompt(query, fusion_results, enriched_context, country, use_breadcrumb=use_breadcrumb, intent=intent)
        logger.debug("=== PROMPT UTILISATEUR ENVOYÉ AU LLM ===\n%s", user)
        try:
            res = self._call(system, user, stream)
            if isinstance(res, dict):
                res["system_prompt"] = system
                res["document_context"] = user
            return res
        except Exception as e:
            logger.error("Erreur génération LLM : %s", e)
            res = {"system_prompt": system, "document_context": user}
            if stream:
                res["stream_generator"] = (chunk for chunk in [f"Erreur : {str(e)}"])
            else:
                res["error"] = str(e)
            return res
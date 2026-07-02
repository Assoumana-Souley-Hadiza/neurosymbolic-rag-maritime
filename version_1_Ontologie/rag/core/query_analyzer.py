"""
query_analyzer.py — Analyse de l'intention de la requête utilisateur.

Détermine automatiquement le type de requête et ajuste les poids
des retrievers en conséquence :
  - Factuelle  → privilégie le Graph Retriever (SPARQL)
  - Exploratoire → privilégie le Dense Retriever (sémantique)
  - Juridique   → privilégie BM25 + Graph (termes exacts + ontologie)
"""

import logging
import re
from typing import Dict, Tuple, Optional

from rag.config import QUERY_ANALYZER_CONFIG

logger = logging.getLogger(__name__)


class QueryAnalyzer:
    """Analyse l'intention d'une requête et renvoie les poids des retrievers."""

    # Patterns pour la détection d'intention
    FACTUAL_PATTERNS = [
        r"\bqu(?:el|elle)s?\b.*\b(?:sont|est)\b",      # "Quels/Quelles sont..."
        r"\bcombien\b",                                  # "Combien de..."
        r"\bliste[rz]?\b",                               # "Lister..."
        r"\bénumérer\b",                                 # "Énumérer..."
        r"\bqui\b.*\b(?:est|sont)\b",                    # "Qui est/sont..."
        r"\bdéfini(?:r|tion|e)\b",                       # "Définition de..."
        r"\bquel(?:le)?s?\s+(?:pays|état|zone|espèce)\b", # "Quels pays/zones..."
    ]

    LEGAL_PATTERNS = [
        r"\binterdiction\b",
        r"\bobligati(?:on|ons)\b",
        r"\bréglementation\b",
        r"\b(?:convention|résolution|article|loi)\b",
        r"\bsanction\b",
        r"\bjuridique\b",
        r"\bdroit\b",
        r"\blégal\b",
        r"\bnorme\b",
        r"\bpermission\b",
        r"\bexception\b",
        r"\bmoratoire\b",
    ]

    EXPLORATORY_PATTERNS = [
        r"\bcomment\b",                                  # "Comment..."
        r"\bpourquoi\b",                                 # "Pourquoi..."
        r"\bexpliquer?\b",                               # "Expliquer..."
        r"\bdécrire?\b",                                 # "Décrire..."
        r"\banalyser?\b",                                # "Analyser..."
        r"\bimpact\b",                                   # "Impact de..."
        r"\bconséquence\b",                              # "Conséquences..."
        r"\brelation\b",                                 # "Relation entre..."
        r"\bdifférence\b",                               # "Différence entre..."
    ]

    EXISTENCE_PATTERNS = [
        r"\best[- ]ce que\b",                            # "Est-ce que..."
        r"\by a[- ]t[- ]il\b",                          # "Y a-t-il..."
        r"\bexiste[- ]t[- ]il\b",                       # "Existe-t-il..."
        r"\binterdi(?:t|te|ction|re)\b.*\b(?:au|en|dans|pour)\b",  # "interdit au Maroc"
        r"\b(?:au|en|dans)\b.*\binterdi(?:t|te|ction)\b",          # "au Maroc interdit"
        r"\bprot[eé]g[eé](?:e|es|er)?\b",              # "protégé/protéger"
        r"\bautoris[eé](?:e|es|er)?\b",                 # "autorisé/autoriser"
    ]

    # --- Nouvelles intentions granulaires ---
    SANCTION_PENALE_PATTERNS = [
        r"\b(?:prison|emprisonnement|pénal(?:e)?|réclusion)\b",
    ]

    SANCTION_FINANCIERE_PATTERNS = [
        r"\b(?:amende|financière|franc|cfa)\b",
    ]

    CONDITION_TEMPORELLE_PATTERNS = [
        r"\b(?:temporalité|permanence|période(?:s)?|saison(?:s)?|temporaire(?:s)?)\b",
    ]

    CONDITION_SPATIALE_PATTERNS = [
        r"\b(?:zone(?:s)?|aire(?:s)?|région(?:s)?|lieu(?:x)?|spatial(?:e|es|aux)?)\b",
    ]

    CONTROLE_INSTITUTION_PATTERNS = [
        r"\b(?:contrôle|administration|comité|service|agent|superviser|évaluer|constater|procédure|procédures)\b",
    ]

    EXCEPTION_PATTERNS = [
        r"\b(?:exception(?:s)?|dérogation(?:s)?|sauf|exceptionnel(?:le)?|autorisé(?:e)? dans le cas|dérogation|dérogatoire)\b",
    ]



    def analyze(self, query: str) -> Tuple[str, Dict[str, float], Optional[str], Optional[str]]:
        """
        Analyse la requête et retourne l'intention + les poids + un éventuel filtre pays + filtre catégorie (désormais None).

        Returns:
            (intent_type, weights_dict, country_filter, category_filter)
        """
        query_lower = query.lower()

        # ── Détection de pays explicite ──
        COUNTRY_CODES = {
            r"\balg(?:érie|erie)?\b|\bdz\b": "alg",
            r"\bmaroc\b|\bma\b|\bmor(?:occo)?\b": "mor",
            r"\btunisie\b|\btun\b": "tun",
            r"\bfrance\b|\bfr\b|\bfrançais(?:e)?\b|\bfra\b": "fra",
            r"\bs[eé]n[eé]gal\b|\bsen\b": "sen",
            r"\bmauritanie\b|\bmau\b": "mau",
            r"\bgabon\b|\bgab\b": "gab",
            r"\bguin[eé]e\b|\bgui\b": "gui",
            r"\bc[oô]te\s*d['’]?ivoire\b|\bivc\b": "ivc",
            r"\bmadagascar\b|\bmad\b": "mad",
            r"\bb[eé]nin\b|\bben\b": "ben",
            r"\btogo\b|\btog\b": "tog",
            r"\bcomores\b|\bcom\b": "com",
            r"\bcameroun\b|\bcmr\b": "cmr",
            r"\bdjibouti\b|\bdji\b": "dji",
            r"\bcongo\b|\bcng\b|\bcon\b": "cng",
        }
        
        country_filter = None
        for pattern, code in COUNTRY_CODES.items():
            if re.search(pattern, query_lower):
                country_filter = code
                break

        # ── Détection de catégorie ──
        category_filter = None

        # Compter les matchs par catégorie
        scores = {
            "factual": self._count_matches(query_lower, self.FACTUAL_PATTERNS),
            "legal": self._count_matches(query_lower, self.LEGAL_PATTERNS),
            "exploratory": self._count_matches(query_lower, self.EXPLORATORY_PATTERNS),
            "existence": self._count_matches(query_lower, self.EXISTENCE_PATTERNS),
            "sanction_penale": self._count_matches(query_lower, self.SANCTION_PENALE_PATTERNS),
            "sanction_financiere": self._count_matches(query_lower, self.SANCTION_FINANCIERE_PATTERNS),
            "condition_temporelle": self._count_matches(query_lower, self.CONDITION_TEMPORELLE_PATTERNS),
            "condition_spatiale": self._count_matches(query_lower, self.CONDITION_SPATIALE_PATTERNS),
            "controle_institution": self._count_matches(query_lower, self.CONTROLE_INSTITUTION_PATTERNS),
            "exception": self._count_matches(query_lower, self.EXCEPTION_PATTERNS),
        }

        # Intentions prioritaires (complexes) classées par ordre d'importance
        # L'index 0 a la plus haute priorité en cas d'égalité de score.
        priority_intents = [
            "controle_institution", "exception", "sanction_penale", "sanction_financiere", 
            "condition_temporelle", "condition_spatiale", "exploratory"
        ]

        max_score = max(scores.values())
        if max_score == 0:
            intent = "default"
        else:
            priority_matches = {k: v for k, v in scores.items() if k in priority_intents and v > 0}
            if priority_matches:
                # Priorité 1: Le score (plus grand = meilleur) -> -priority_matches[k]
                # Priorité 2: L'ordre dans la liste (plus petit index = meilleur) -> priority_intents.index(k)
                intent = min(priority_matches.keys(), key=lambda k: (-priority_matches[k], priority_intents.index(k)))
            else:
                intent = max(scores, key=lambda k: scores[k])

        weights = QUERY_ANALYZER_CONFIG.get(
            f"{intent}_weights",
            QUERY_ANALYZER_CONFIG["default_weights"]
        )

        logger.info(
            f"  QueryAnalyzer: intent='{intent}' "
            f"(scores: {scores}) -> weights={weights} | country='{country_filter}' | cat='{category_filter}'"
        )

        return intent, weights, country_filter, category_filter

    @staticmethod
    def _count_matches(text: str, patterns: list) -> int:
        """Compte le nombre de patterns matchant dans le texte."""
        count = 0
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                count += 1
        return count
    def get_cleaned_query(self, query: str) -> str:
        """Supprime le bruit et les formules de politesse/méta-discours."""
        q = query.lower()
        
        # Supprimer les expressions courantes de questions
        noise = [
            r"est-ce qu'il existe", r"est-ce que", r"y a-t-il", r"existe-t-il",
            r"un article portant sur", r"des articles sur", r"le texte juridique",
            r"précise les types d'activités concernées par",
            r"pourriez-vous me dire si", r"je voudrais savoir si",
            r"concernant l'interdiction de", r"au sujet de",
            r"dans le domaine de", r"relativement à"
        ]
        
        for pattern in noise:
            q = re.sub(pattern, "", q)
            
        # Nettoyer les doubles espaces et ponctuation
        q = re.sub(r'[^\w\s]', ' ', q)
        q = " ".join(q.split())
        
        logger.info(f"[Analyzer] Requête nettoyée : '{q}'")
        return q

if __name__ == "__main__":
    analyzer = QueryAnalyzer()
    test_q = "Est-ce que le texte juridique précise les types d'activités concernées par l'interdiction du chalutage de fond au bénin ?"
    print(f"Original: {test_q}")
    print(f"Cleaned: {analyzer.get_cleaned_query(test_q)}")

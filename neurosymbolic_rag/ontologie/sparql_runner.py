"""
sparql_runner.py — Questions de compétence SPARQL pour l'ontologie maritime.

Les 10 questions de compétence couvrent :
  CQ1  : Quelles interdictions existent ?
  CQ2  : Dans quelles zones s'applique une interdiction ?
  CQ3  : Quelles activités sont interdites ?
  CQ4  : Quels acteurs sont concernés par une interdiction ?
  CQ5  : Quelles exceptions existent pour une interdiction ?
  CQ6  : Quelles espèces sont protégées par la chasse à la baleine ?
  CQ7  : Quelle est la base juridique de chaque interdiction ?
  CQ8  : Quels contrôles s'appliquent à l'interdiction du chalutage ?
  CQ9  : Pendant quelle période s'applique l'interdiction ?
  CQ10 : Quels concepts lexicaux sont définis dans l'ontologie ?
"""

import logging
from rdflib import Graph

logger = logging.getLogger(__name__)

NS_PREFIXES = """
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
PREFIX mar:  <http://www.maritime-ontology.org/mar#>
PREFIX lkif: <http://www.estrellaproject.org/lkif-core/lkif-core.owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
"""

COMPETENCY_QUESTIONS = {

    "CQ1_liste_interdictions": {
        "description": "Quelles interdictions sont définies dans l'ontologie ?",
        "sparql": NS_PREFIXES + """
SELECT ?interdiction ?label ?deonticType ?legalLayer WHERE {
    ?interdiction rdf:type mar:Interdiction ;
                  rdfs:label ?label .
    OPTIONAL { ?interdiction mar:deonticType ?deonticType }
    OPTIONAL { ?interdiction mar:legalLayer  ?legalLayer }
    FILTER (lang(?label) = 'fr')
}
ORDER BY ?label
"""
    },

    "CQ2_zones_par_interdiction": {
        "description": "Dans quelles zones géographiques s'applique chaque interdiction ?",
        "sparql": NS_PREFIXES + """
SELECT ?interdiction ?iLabel ?zone ?zLabel ?zType WHERE {
    ?interdiction rdf:type mar:Interdiction ;
                  rdfs:label ?iLabel ;
                  mar:appliesInZone ?zone .
    ?zone rdfs:label ?zLabel .
    OPTIONAL { ?zone rdf:type ?zType . FILTER(?zType != owl:NamedIndividual) }
    FILTER (lang(?iLabel) = 'fr')
    FILTER (lang(?zLabel) = 'fr')
}
ORDER BY ?interdiction
"""
    },

    "CQ3_activites_interdites": {
        "description": "Quelles activités sont concernées par des interdictions ?",
        "sparql": NS_PREFIXES + """
SELECT ?interdiction ?iLabel ?activite ?aLabel ?aType WHERE {
    ?interdiction rdf:type mar:Interdiction ;
                  rdfs:label ?iLabel ;
                  mar:concerneActivite ?activite .
    ?activite rdfs:label ?aLabel .
    OPTIONAL { ?activite rdf:type ?aType . FILTER(?aType != owl:NamedIndividual) }
    FILTER (lang(?iLabel) = 'fr')
    FILTER (lang(?aLabel) = 'fr')
}
"""
    },

    "CQ4_acteurs_concernes": {
        "description": "Quels acteurs sont soumis à chaque interdiction ?",
        "sparql": NS_PREFIXES + """
SELECT ?interdiction ?iLabel ?acteur ?aLabel ?aType WHERE {
    ?interdiction rdf:type mar:Interdiction ;
                  rdfs:label ?iLabel ;
                  mar:concerneActeur ?acteur .
    ?acteur rdfs:label ?aLabel .
    OPTIONAL { ?acteur rdf:type ?aType . FILTER(?aType != owl:NamedIndividual) }
    FILTER (lang(?iLabel) = 'fr')
    FILTER (lang(?aLabel) = 'fr')
}
ORDER BY ?interdiction
"""
    },

    "CQ5_exceptions": {
        "description": "Quelles exceptions existent pour les interdictions ?",
        "sparql": NS_PREFIXES + """
SELECT ?interdiction ?iLabel ?exception ?eLabel WHERE {
    ?interdiction rdf:type mar:Interdiction ;
                  rdfs:label ?iLabel ;
                  mar:aException ?exception .
    ?exception rdfs:label ?eLabel .
    FILTER (lang(?iLabel) = 'fr')
    FILTER (lang(?eLabel) = 'fr')
}
ORDER BY ?interdiction
"""
    },

    "CQ6_especes_protegees": {
        "description": "Quelles espèces marines sont protégées et sous quelle interdiction ?",
        "sparql": NS_PREFIXES + """
SELECT ?interdiction ?iLabel ?espece ?eLabel ?nomSci ?statut WHERE {
    ?interdiction rdf:type mar:Interdiction ;
                  rdfs:label ?iLabel ;
                  mar:protegeEspece ?espece .
    ?espece rdfs:label ?eLabel .
    OPTIONAL { ?espece mar:nomScientifique ?nomSci }
    OPTIONAL { ?espece mar:statutProtection ?statut }
    FILTER (lang(?iLabel) = 'fr')
    FILTER (lang(?eLabel) = 'fr')
}
ORDER BY ?statut ?eLabel
"""
    },

    "CQ7_sources_juridiques": {
        "description": "Quelles sont les sources juridiques fondatrices de chaque interdiction ?",
        "sparql": NS_PREFIXES + """
SELECT ?interdiction ?iLabel ?source ?sLabel ?sRef ?sYear WHERE {
    ?interdiction rdf:type mar:Interdiction ;
                  rdfs:label ?iLabel ;
                  mar:fondeeSur ?source .
    ?source rdfs:label ?sLabel .
    OPTIONAL { ?source rdfs:comment ?sRef }
    OPTIONAL { ?source mar:sourceYear ?sYear }
    FILTER (lang(?iLabel) = 'fr')
}
ORDER BY ?interdiction ?sYear
"""
    },

    "CQ8_controles": {
        "description": "Quels mécanismes de contrôle s'appliquent à chaque interdiction ?",
        "sparql": NS_PREFIXES + """
SELECT ?interdiction ?iLabel ?controle ?cLabel WHERE {
    ?interdiction rdf:type mar:Interdiction ;
                  rdfs:label ?iLabel ;
                  mar:soumisAControle ?controle .
    ?controle rdfs:label ?cLabel .
    FILTER (lang(?iLabel) = 'fr')
    FILTER (lang(?cLabel) = 'fr')
}
ORDER BY ?interdiction
"""
    },

    "CQ9_periodes": {
        "description": "Pendant quelle(s) période(s) s'appliquent les interdictions ?",
        "sparql": NS_PREFIXES + """
SELECT ?interdiction ?iLabel ?periode ?pLabel ?pType WHERE {
    ?interdiction rdf:type mar:Interdiction ;
                  rdfs:label ?iLabel ;
                  mar:appliesDuring ?periode .
    ?periode rdfs:label ?pLabel .
    OPTIONAL { ?periode rdf:type ?pType . FILTER(?pType != owl:NamedIndividual) }
    FILTER (lang(?iLabel) = 'fr')
    FILTER (lang(?pLabel) = 'fr')
}
"""
    },

    "CQ10_concepts_lexicaux": {
        "description": "Quels concepts lexicaux sont définis dans l'ontologie ?",
        "sparql": NS_PREFIXES + """
SELECT ?concept ?label ?definition ?nomSci WHERE {
    ?concept rdf:type mar:ConceptLexical ;
             rdfs:label ?label .
    OPTIONAL { ?concept skos:definition ?definition }
    OPTIONAL { ?concept mar:nomScientifique ?nomSci }
}
ORDER BY ?label
LIMIT 50
"""
    },

    "CQ11_hierarchie_zones": {
        "description": "Quelle est la hiérarchie des zones maritimes ?",
        "sparql": NS_PREFIXES + """
SELECT ?zone ?label ?type WHERE {
    ?zone rdf:type owl:NamedIndividual ;
          rdfs:label ?label .
    ?zone rdf:type ?type .
    ?type rdfs:subClassOf* mar:Zone .
    FILTER(?type != owl:NamedIndividual)
    FILTER(lang(?label) = 'fr')
}
ORDER BY ?type ?label
"""
    },

    "CQ12_graph_stats": {
        "description": "Statistiques globales du graphe de connaissances",
        "sparql": NS_PREFIXES + """
SELECT
    (COUNT(DISTINCT ?interdiction) AS ?nbInterdictions)
    (COUNT(DISTINCT ?zone)         AS ?nbZones)
    (COUNT(DISTINCT ?activite)     AS ?nbActivites)
    (COUNT(DISTINCT ?acteur)       AS ?nbActeurs)
    (COUNT(DISTINCT ?espece)       AS ?nbEspeces)
    (COUNT(DISTINCT ?concept)      AS ?nbConcepts)
WHERE {
    OPTIONAL { ?interdiction rdf:type mar:Interdiction }
    OPTIONAL { ?zone         rdf:type/rdfs:subClassOf* mar:Zone . ?zone rdf:type owl:NamedIndividual }
    OPTIONAL { ?activite     rdf:type/rdfs:subClassOf* mar:Activite . ?activite rdf:type owl:NamedIndividual }
    OPTIONAL { ?acteur       rdf:type/rdfs:subClassOf* mar:Acteur . ?acteur rdf:type owl:NamedIndividual }
    OPTIONAL { ?espece       rdf:type/rdfs:subClassOf* mar:EspeceMarine . ?espece rdf:type owl:NamedIndividual }
    OPTIONAL { ?concept      rdf:type mar:ConceptLexical }
}
"""
    },
}


def run_all_competency_questions(g: Graph) -> dict:
    """
    Exécute toutes les questions de compétence et retourne les résultats.
    """
    results = {}
    for cq_id, cq in COMPETENCY_QUESTIONS.items():
        try:
            qres = list(g.query(cq["sparql"]))
            results[cq_id] = {
                "description": cq["description"],
                "results": [
                    {str(var): (str(row[i]) if row[i] is not None else None)
                     for i, var in enumerate(qres[0].labels)}
                    for row in qres
                ] if qres else [],
                "count": len(qres)
            }
            logger.info(f"  ✅ {cq_id} : {len(qres)} résultats")
        except Exception as e:
            logger.error(f"  ❌ {cq_id} : {e}")
            results[cq_id] = {"description": cq["description"], "error": str(e), "results": []}
    return results


def format_results_report(results: dict) -> str:
    """Formate les résultats en rapport lisible."""
    lines = [
        "═" * 70,
        "  RAPPORT DES QUESTIONS DE COMPÉTENCE — Ontologie Maritime",
        "═" * 70, ""
    ]
    for cq_id, res in results.items():
        lines.append(f"  {cq_id}")
        lines.append(f"  {res['description']}")
        lines.append(f"  {'─' * 60}")
        if "error" in res:
            lines.append(f"  ❌ Erreur : {res['error']}")
        elif res["results"]:
            for row in res["results"][:10]:  # max 10 lignes
                row_str = " | ".join(f"{k}={v}" for k, v in row.items() if v)
                lines.append(f"    • {row_str}")
            if res["count"] > 10:
                lines.append(f"    ... ({res['count'] - 10} résultats supplémentaires)")
        else:
            lines.append("  (aucun résultat)")
        lines.append("")
    return "\n".join(lines)

"""
neo4j_export.py — Export du graphe de connaissances vers Neo4j.

Stratégie de modélisation :
  - Chaque individu OWL  →  Nœud Neo4j avec labels issus des classes OWL
  - Chaque propriété objet →  Relation Neo4j typée
  - Les propriétés de données → Attributs du nœud
  - Les labels RDFS → propriété .label du nœud
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from rdflib import Graph, URIRef, Literal, RDF, RDFS, OWL
from rdflib.namespace import SKOS

logger = logging.getLogger(__name__)

NS_MAR  = "http://www.maritime-ontology.org/mar#"
NS_LKIF = "http://www.estrellaproject.org/lkif-core/lkif-core.owl#"

# Mapping propriété OWL → type de relation Neo4j (sans doublons)
PREDICATE_TO_RELATION = {
    f"{NS_MAR}appliesInZone":       "APPLIES_IN_ZONE",
    f"{NS_MAR}concerneActivite":    "CONCERNE_ACTIVITE",
    f"{NS_MAR}concerneActeur":      "CONCERNE_ACTEUR",
    f"{NS_MAR}appliesDuring":       "APPLIES_DURING",
    f"{NS_MAR}aException":          "A_EXCEPTION",
    f"{NS_MAR}soumisAControle":     "SOUMIS_A_CONTROLE",
    f"{NS_MAR}entraineSanction":    "ENTRAINE_SANCTION",
    f"{NS_MAR}fondeeSur":           "FONDEE_SUR",
    f"{NS_MAR}protegeEspece":       "PROTEGE_ESPECE",
    f"{NS_MAR}hasConcept":          "HAS_CONCEPT",
    f"{NS_MAR}estSoumisA":          "EST_SOUMIS_A",
    f"{NS_MAR}soumisA":             "SOUMIS_A",
    f"{NS_MAR}beneficieA":          "BENEFICIE_A",
    f"{NS_MAR}institueNorme":       "INSTITUE_NORME",
    f"{NS_MAR}couvreZone":          "COUVRE_ZONE",
    f"{NS_MAR}concerneStock":       "CONCERNE_STOCK",
    f"{NS_MAR}hasDerogation":       "HAS_DEROGATION",
    f"{NS_MAR}entraineConsequence":  "ENTRAINE_CONSEQUENCE",
    f"{NS_MAR}aExceptionSpecifique": "A_EXCEPTION_SPECIFIQUE",
    f"{NS_MAR}conditionneePar":     "CONDITIONNEE_PAR",
    f"{NS_MAR}estMenacePar":        "EST_MENACE_PAR",
    f"{NS_MAR}habiteDans":          "HABITE_DANS",
    f"{NS_MAR}pratiqueActivite":    "PRATIQUE_ACTIVITE",
    f"{NS_MAR}opereDans":           "OPERE_DANS",
    f"{NS_MAR}modifieSource":       "MODIFIE_SOURCE",
    f"{NS_MAR}commandeNavire":      "COMMANDE_NAVIRE",
    f"{NS_MAR}possèdeNavire":       "POSSEDE_NAVIRE",
    f"{NS_MAR}estSousZoneDe":       "EST_SOUS_ZONE_DE",
    f"{NS_MAR}bordeZone":           "BORDE_ZONE",
    f"{NS_MAR}contientSousZone":    "CONTIENT_SOUS_ZONE",
    f"{NS_MAR}estZoneDe":           "EST_ZONE_DE",
    f"{NS_MAR}estActiviteDe":       "EST_ACTIVITE_DE",
    f"{NS_MAR}estActeurConcernePar": "EST_ACTEUR_CONCERNE_PAR",
    f"{NS_MAR}estExceptionDe":      "EST_EXCEPTION_DE",
    f"{NS_MAR}estSanctionDe":       "EST_SANCTION_DE",
    str(SKOS.broader):              "BROADER_THAN",
    str(SKOS.narrower):             "NARROWER_THAN",
    str(SKOS.related):              "RELATED_TO",
}

# Mapping classe OWL locale → label Neo4j
CLASS_TO_NEO4J_LABEL = {
    # Normes
    "Interdiction":                "Interdiction",
    "Permission":                  "Permission",
    "Obligation":                  "Obligation",
    "NormeJuridique":              "Norme",
    "NormeInternationale":         "Norme:NormeInternationale",
    # Zones
    "Zone":                        "Zone",
    "ZoneHauteMer":                "Zone:ZoneHauteMer",
    "ZoneEconomiqueExclusive":     "Zone:ZoneEEZ",
    "ZoneMerTerritoriale":         "Zone:ZoneMerTerritoriale",
    "ZoneContigüe":                "Zone:ZoneContigue",
    "PlateauContinental":          "Zone:PlateauContinental",
    "ZoneSanctuaireMarin":         "Zone:ZoneSanctuaire",
    "ZoneEcosystemeVulnerable":    "Zone:ZoneEcosystemeVulnerable",
    "ZoneSpecialeMARPOL":          "Zone:ZoneSpecialeMARPOL",
    "ZoneCotiere":                 "Zone:ZoneCotiere",
    "AireMarineProtegee":          "Zone:AireMarineProtegee",
    "ZoneInterdite":               "Zone:ZoneInterdite",
    # Activités
    "Activite":                    "Activite",
    "ActivitePeche":               "Activite:ActivitePeche",
    "ChalutageFond":               "Activite:ChalutageFond",
    "PecheINN":                    "Activite:PecheINN",
    "PecheProfonde":               "Activite:PecheProfonde",
    "ActiviteChasse":              "Activite:ActiviteChasse",
    "ChasseBaleine":               "Activite:ChasseBaleine",
    "ChasseCommercialeBaleine":    "Activite:ChasseCommerciale",
    "ChasseScientifiqueBaleine":   "Activite:ChasseScientifique",
    "ChasseSubsistanceAutochtone": "Activite:ChasseSubsistance",
    "ActiviteExtraction":          "Activite:ActiviteExtraction",
    "ExtractionSable":             "Activite:ExtractionSable",
    "ExtractionHydrocarbures":     "Activite:ExtractionHydrocarbures",
    "ActiviteConstruction":        "Activite:ActiviteConstruction",
    "ConstructionLittorale":       "Activite:ConstructionLittorale",
    "ConstructionPortuaire":       "Activite:ConstructionPortuaire",
    "ActiviteRejets":              "Activite:ActiviteRejets",
    "RejetsHydrocarbures":         "Activite:RejetsHydrocarbures",
    "RejetsDechetsMenagers":       "Activite:RejetsDechetsMenagers",
    "RejetsEauxUsees":             "Activite:RejetsEauxUsees",
    "ActiviteCapture":             "Activite:ActiviteCapture",
    "CaptureOiseauxMarins":        "Activite:CaptureOiseauxMarins",
    "ActiviteIllicite":            "Activite:ActiviteIllicite",
    # Acteurs
    "Acteur":                      "Acteur",
    "EtatSouverain":               "Acteur:EtatSouverain",
    "EtatPavillon":                "Acteur:EtatPavillon",
    "EtatCotier":                  "Acteur:EtatCotier",
    "EtatPortuaire":               "Acteur:EtatPortuaire",
    "OrganisationInternationale":  "Acteur:OrganisationInternationale",
    "OrganismeRegionalGestionPeche": "Acteur:ORGP",
    "CommissionBaleiniereInternationale": "Acteur:IWC",
    "OrganisationMaritimeInternationale": "Acteur:IMO",
    "OrganisationFAO":             "Acteur:FAO",
    "SecretariatCDB":              "Acteur:SecretariatCDB",
    "NavirePeche":                 "Acteur:NavirePeche",
    "NavireUsine":                 "Acteur:NavireUsine",
    "NavirePetrolier":             "Acteur:NavirePetrolier",
    "NavireMarchand":              "Acteur:NavireMarchand",
    "OperateurEconomique":         "Acteur:OperateurEconomique",
    "Armateur":                    "Acteur:Armateur",
    "Capitaine":                   "Acteur:Capitaine",
    "OperateurOffshore":           "Acteur:OperateurOffshore",
    "PromoteurCotier":             "Acteur:PromoteurCotier",
    "CommunauteAutochtone":        "Acteur:CommunauteAutochtone",
    # Espèces
    "EspeceMarine":                "EspeceMarine",
    "Cetace":                      "EspeceMarine:Cetace",
    "BaleineMysticete":            "EspeceMarine:BaleineMysticete",
    "BaleineOdontocete":           "EspeceMarine:BaleineOdontocete",
    "OiseauMarin":                 "EspeceMarine:OiseauMarin",
    "OiseauMarinMigrateur":        "EspeceMarine:OiseauMarinMigrateur",
    "TortueMarine":                "EspeceMarine:TortueMarine",
    "PoissonEauxProfondes":        "EspeceMarine:PoissonEauxProfondes",
    "EspeceVulnerable":            "EspeceMarine:EspeceVulnerable",
    "EspeceProtegee":              "EspeceMarine:EspeceProtegee",
    # Sources juridiques
    "SourceJuridique":             "SourceJuridique",
    "ConventionInternationale":    "SourceJuridique:Convention",
    "ResolutionAGONU":             "SourceJuridique:Resolution",
    "Reglement":                   "SourceJuridique:Reglement",
    "ProtocoleInternational":      "SourceJuridique:Protocole",
    "DecisionOMI":                 "SourceJuridique:DecisionOMI",
    # Temporel
    "Periode":                     "Periode",
    "PeriodeConditionnelle":       "Periode:PeriodeConditionnelle",
    "PeriodePermanente":           "Periode:PeriodePermanente",
    # Exceptions & Conséquences
    "ExceptionJuridique":          "ExceptionJuridique",
    "ExceptionGenerale":           "ExceptionJuridique:ExceptionGenerale",
    "ExceptionSpecifique":         "ExceptionJuridique:ExceptionSpecifique",
    "ConsequenceException":        "ConsequenceException",
    # Contrôle & Sanction
    "Controle":                    "Controle",
    "ControleEtatPavillon":        "Controle:ControleEtatPavillon",
    "ControleEtatPort":            "Controle:ControleEtatPort",
    "ControleOrgRegional":         "Controle:ControleOrgRegional",
    "Sanction":                    "Sanction",
    "SanctionPenale":              "Sanction:SanctionPenale",
    "SanctionAdministrative":      "Sanction:SanctionAdministrative",
    # Divers
    "ConditionApplication":        "ConditionApplication",
    "Stock":                       "Stock",
    "StockSurexploite":            "Stock:StockSurexploite",
    "ConceptLexical":              "ConceptLexical",
    "ActeurEnInfraction":          "Acteur:ActeurEnInfraction",
}

# Propriétés de données à extraire
DATA_PROPS = {
    f"{NS_MAR}deonticType":       "deonticType",
    f"{NS_MAR}confidence":        "confidence",
    f"{NS_MAR}legalLayer":        "legalLayer",
    f"{NS_MAR}normText":          "normText",
    f"{NS_MAR}needsReview":       "needsReview",
    f"{NS_MAR}sourceConvention":  "sourceConvention",
    f"{NS_MAR}nomScientifique":   "nomScientifique",
    f"{NS_MAR}statutProtection":  "statutProtection",
    f"{NS_MAR}sourceYear":        "sourceYear",
    f"{NS_MAR}distanceNM":        "distanceNM",
    f"{NS_MAR}surfaceKm2":        "surfaceKm2",
    f"{NS_MAR}codeZoneIMO":       "codeZoneIMO",
    f"{NS_MAR}typeActivite":      "typeActivite",
    f"{NS_MAR}concentrationPPM":  "concentrationPPM",
    f"{NS_MAR}sourceArticle":     "sourceArticle",
    f"{NS_MAR}isZoneSpecific":    "isZoneSpecific",
    str(SKOS.definition):         "definition",
    str(SKOS.prefLabel):          "prefLabel",
    str(SKOS.altLabel):           "synonym",
    str(RDFS.comment):            "comment",
}


def build_graph_data(g: Graph) -> Tuple[List[dict], List[dict]]:
    """
    Extrait les nœuds et relations depuis le graphe RDFLib.

    Retourne:
        nodes: List[{id, labels, properties}]
        edges: List[{source, target, type, properties}]
    """
    nodes: Dict[str, dict] = {}
    edges: List[dict] = []

    # ── 1. Collecter les classes de chaque individu ──────────────
    ind_classes: Dict[str, set] = {}
    for s, p, o in g.triples((None, RDF.type, OWL.NamedIndividual)):
        if isinstance(s, URIRef):
            ind_classes.setdefault(str(s), set())

    # Prefixes à nettoyer pour extraire le nom local
    _URI_PREFIXES = [
        NS_MAR, NS_LKIF,
        str(SKOS),
        str(OWL),
        str(RDFS),
        str(RDF),
        "http://www.w3.org/2001/XMLSchema#",
    ]
    def _local_name(uri_str: str) -> str:
        for pfx in _URI_PREFIXES:
            if uri_str.startswith(pfx):
                return uri_str[len(pfx):]
        if "#" in uri_str:
            return uri_str.split("#")[-1]
        if "/" in uri_str:
            return uri_str.rsplit("/", 1)[-1]
        return uri_str

    for s, p, o in g.triples((None, RDF.type, None)):
        if isinstance(s, URIRef) and str(s) in ind_classes:
            local = _local_name(str(o))
            # Ignorer les types OWL/RDF de base
            if local in ("NamedIndividual", "Thing", "Class", "Resource",
                         "ObjectProperty", "DatatypeProperty", "AnnotationProperty"):
                continue
            ind_classes[str(s)].add(local)

    # ── 2. Construire les nœuds ──────────────────────────────────
    for uri_str, classes in ind_classes.items():
        local_id = _local_name(uri_str)

        # Labels Neo4j : résoudre les noms de classes
        neo4j_labels = set()
        for c in classes:
            # Filtrer les URIs complètes non résolues
            if "://" in c:
                continue
            mapped = CLASS_TO_NEO4J_LABEL.get(c)
            if mapped:
                for lbl in mapped.split(":"):
                    neo4j_labels.add(lbl)
            else:
                neo4j_labels.add(c)

        if not neo4j_labels:
            neo4j_labels = {"OntologyNode"}

        # Propriétés
        props: Dict[str, Any] = {"uri": uri_str, "id": local_id}

        # Labels RDFS
        labels_fr = [str(o) for _, p, o in g.triples((URIRef(uri_str), RDFS.label, None))
                     if isinstance(o, Literal) and (o.language == "fr" or not o.language)]
        labels_en = [str(o) for _, p, o in g.triples((URIRef(uri_str), RDFS.label, None))
                     if isinstance(o, Literal) and o.language == "en"]
        if labels_fr:
            props["label"] = labels_fr[0]
        elif labels_en:
            props["label"] = labels_en[0]
        else:
            props["label"] = local_id

        if labels_en:
            props["label_en"] = labels_en[0]

        # Propriétés de données
        for prop_uri, prop_name in DATA_PROPS.items():
            values = [str(o) for _, p, o in g.triples((URIRef(uri_str), URIRef(prop_uri), None))]
            if values:
                props[prop_name] = values[0] if len(values) == 1 else values

        nodes[uri_str] = {
            "id": local_id,
            "labels": sorted(neo4j_labels),
            "properties": props
        }

    # ── 3. Construire les relations dynamiquement ─────────
    seen_edges = set()

    for s, p, o in g.triples((None, None, None)):
        if isinstance(o, URIRef) and str(s) in nodes and str(o) in nodes:
            pred_uri = str(p)

            if NS_MAR in pred_uri or str(SKOS) in pred_uri or str(RDFS) in pred_uri:
                if pred_uri in [str(RDF.type), str(RDFS.label), str(OWL.sameAs)]:
                    continue

                rel_type = PREDICATE_TO_RELATION.get(pred_uri)
                if not rel_type:
                    local_p = pred_uri.replace(NS_MAR, "").replace(str(SKOS), "").replace(str(RDFS), "")
                    rel_type = re.sub(r'(?<!^)(?=[A-Z])', '_', local_p).upper()

                edge_sig = (str(s), rel_type, str(o))

                if edge_sig not in seen_edges:
                    seen_edges.add(edge_sig)
                    edges.append({
                        "source": str(s).replace(NS_MAR, ""),
                        "target": str(o).replace(NS_MAR, ""),
                        "source_uri": str(s),
                        "target_uri": str(o),
                        "type": rel_type,
                        "properties": {}
                    })

    logger.info(f"  📊 Graphe extrait : {len(nodes)} nœuds, {len(edges)} relations")

    # ── 4. Traitement Spécial des Synonymes (Transformés en Nœuds) ──
    for uri_str, node_info in list(nodes.items()):
        synonyms = [str(o) for _, p, o in g.triples((URIRef(uri_str), SKOS.altLabel, None))]

        for syn_text in synonyms:
                syn_id = "Syn_" + re.sub(r'\W+', '_', syn_text)

                if syn_id not in nodes:
                    nodes[syn_id] = {
                        "id": syn_id,
                        "labels": ["Synonyme"],
                        "properties": {
                            "id": syn_id,
                            "label": syn_text,
                            "uri": f"synonym:{syn_id}"
                        }
                    }

                edges.append({
                    "source": syn_id,
                    "target": node_info["id"],
                    "source_uri": f"synonym:{syn_id}",
                    "target_uri": uri_str,
                    "type": "SYNONYME_DE",
                    "properties": {}
                })

    return list(nodes.values()), edges


def generate_cypher_script(nodes: List[dict], edges: List[dict]) -> str:
    """Génère un script Cypher complet pour import dans Neo4j."""

    lines = [
        "// ═══════════════════════════════════════════════════════════",
        "// Ontologie Maritime — Import Cypher Neo4j v2.0",
        "// 6 interdictions | LKIF-Core | Parité OWL complète",
        "// ═══════════════════════════════════════════════════════════",
        "",
        "// ── Contraintes d'unicité ──────────────────────────────────",
    ]

    seen_labels = set()
    for node in nodes:
        primary_label = node["labels"][0] if node["labels"] else "Node"
        if primary_label not in seen_labels:
            lines.append(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{primary_label}) REQUIRE n.id IS UNIQUE;")
            seen_labels.add(primary_label)

    lines += ["", "// ── Création des nœuds ────────────────────────────────────"]

    for node in nodes:
        label_str = ":".join(node["labels"])
        props = node["properties"]
        props_cypher_parts = []
        for k, v in props.items():
            if isinstance(v, bool):
                props_cypher_parts.append(f"{k}: {'true' if v else 'false'}")
            elif isinstance(v, str):
                escaped = v.replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ")
                props_cypher_parts.append(f"{k}: '{escaped}'")
            elif isinstance(v, (int, float)):
                props_cypher_parts.append(f"{k}: {v}")
            elif isinstance(v, list):
                if k == "confidence":
                    try:
                        max_conf = max(float(i) for i in v)
                        props_cypher_parts.append(f"{k}: {max_conf}")
                        node["properties"][k] = max_conf
                    except ValueError:
                        props_cypher_parts.append(f"{k}: '{v[0]}'")
                        node["properties"][k] = v[0]
                else:
                    escaped_items = [f"'{str(i)[:100].replace(chr(39), chr(92) + chr(39))}'" for i in v[:5]]
                    items = ", ".join(escaped_items)
                    props_cypher_parts.append(f"{k}: [{items}]")
        props_str = ", ".join(props_cypher_parts)
        lines.append(f"MERGE (n:{label_str} {{id: '{node['id']}'}}) SET n += {{{props_str}}};")

    lines += ["", "// ── Création des relations ───────────────────────────────"]
    for edge in edges:
        src_escaped = edge['source'].replace("'", "\\'")
        tgt_escaped = edge['target'].replace("'", "\\'")
        lines.append(
            f"MATCH (a {{id: '{src_escaped}'}}) "
            f"MATCH (b {{id: '{tgt_escaped}'}}) "
            f"MERGE (a)-[:{edge['type']}]->(b);"
        )

    lines += [
        "",
        "// ── Index fulltext pour la recherche ─────────────────────",
        "CREATE FULLTEXT INDEX maritimeSearch IF NOT EXISTS",
        "FOR (n:Interdiction|Zone|Activite|Acteur|EspeceMarine|ConceptLexical|SourceJuridique|Synonyme|ExceptionJuridique|Sanction|Controle|ConsequenceException)",
        "ON EACH [n.label, n.label_en, n.definition, n.nomScientifique, n.comment];",
        "",
        "// ═══════════════════════════════════════════════════════════",
        f"// Total : {len(nodes)} nœuds | {len(edges)} relations",
        "// ═══════════════════════════════════════════════════════════",
    ]

    return "\n".join(lines)


def export_to_neo4j(g: Graph, neo4j_config: dict) -> bool:
    """
    Export live vers une instance Neo4j via le driver Python.
    Retourne True si succès, False si Neo4j non disponible (sans crash).
    """
    try:
        from neo4j import GraphDatabase, exceptions as neo4j_exc
    except ImportError:
        logger.warning("  ⚠️  Package 'neo4j' non installé. Export Cypher uniquement.")
        return False

    uri      = neo4j_config.get("uri", "bolt://localhost:7687")
    user     = neo4j_config.get("user", "neo4j")
    password = neo4j_config.get("password", "maritime2024")
    database = neo4j_config.get("database", "neo4j")

    nodes, edges = build_graph_data(g)

    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        logger.info(f"  🔌 Connecté à Neo4j : {uri}")
    except Exception as e:
        logger.warning(f"  ⚠️  Neo4j non accessible ({e}). Export Cypher généré uniquement.")
        return False

    try:
        with driver.session(database=database) as session:
            # Optionnel : Nettoyer la base de données avant l'export
            clear_db = neo4j_config.get("clear_before_export", True)
            if clear_db:
                logger.info("  🧹 Nettoyage de la base de données Neo4j...")
                session.run("MATCH (n) DETACH DELETE n")

            # Nœuds
            batch_size = neo4j_config.get("batch_size", 500)
            for i in range(0, len(nodes), batch_size):
                batch = nodes[i:i + batch_size]
                session.execute_write(_create_nodes_batch, batch)
            logger.info(f"  ✅ {len(nodes)} nœuds créés dans Neo4j")

            # Relations
            for i in range(0, len(edges), batch_size):
                batch = edges[i:i + batch_size]
                session.execute_write(_create_edges_batch, batch)
            logger.info(f"  ✅ {len(edges)} relations créées dans Neo4j")

            # Index fulltext
            session.execute_write(_create_fulltext_index)

    except Exception as e:
        logger.error(f"  ❌ Erreur Neo4j : {e}")
        return False
    finally:
        driver.close()

    return True


def _create_nodes_batch(tx, nodes: List[dict]):
    for node in nodes:
        labels_escaped = [f"`{lbl}`" for lbl in node["labels"] if lbl]
        if not labels_escaped:
            labels_escaped = ["`OntologyNode`"]
        label_str = ":".join(labels_escaped)

        # Nettoyer les props pour Neo4j (pas de listes imbriquées complexes)
        clean_props = {}
        for k, v in node["properties"].items():
            if isinstance(v, list):
                # Neo4j accepte les listes homogènes de scalaires
                clean_props[k] = [str(i) for i in v[:10]]
            else:
                clean_props[k] = v

        query = f"""
        MERGE (n:{label_str} {{id: $id}})
        SET n += $props
        """
        tx.run(query, id=node["id"], props=clean_props)


def _create_edges_batch(tx, edges: List[dict]):
    for edge in edges:
        edge_type = edge['type'].replace(" ", "_").replace("-", "_")
        query = f"""
        MATCH (a {{id: $src}})
        MATCH (b {{id: $tgt}})
        MERGE (a)-[:`{edge_type}`]->(b)
        """
        tx.run(query, src=edge["source"], tgt=edge["target"])


def _create_fulltext_index(tx):
    tx.run("""
    CREATE FULLTEXT INDEX maritimeSearch IF NOT EXISTS
    FOR (n:Interdiction|Zone|Activite|Acteur|EspeceMarine|ConceptLexical|SourceJuridique|Synonyme|ExceptionJuridique|Sanction|Controle|ConsequenceException)
    ON EACH [n.label, n.label_en, n.definition, n.nomScientifique, n.comment]
    """)

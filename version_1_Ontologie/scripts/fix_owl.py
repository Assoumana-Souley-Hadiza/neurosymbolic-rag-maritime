"""
fix_owl.py — Correction complète de maritime_ontology.owl

5 corrections :
  1. Labels bruts 'mar:XXX_YYY' → texte français lisible
  2. Faux acteurs (conditions typées EtatSouverain) → ConditionApplication
  3. Déduplication entités (Espèces, Activités, Zones)
  4. xml:lang incorrects (français tagué 'en')
  5. Hyperonymes surabondants (limiter à ~7 par interdiction)
"""

import logging
import re
import sys
from pathlib import Path
from collections import defaultdict

from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD, BNode
from rdflib.namespace import SKOS

logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
log = logging.getLogger(__name__)

# ── Namespaces ──
MAR  = Namespace("http://www.maritime-ontology.org/mar#")
LKIF = Namespace("http://www.estrellaproject.org/lkif-core/lkif-core.owl#")
DCT  = Namespace("http://purl.org/dc/terms/")

OWL_IN  = Path(__file__).parent.parent / "output" / "ontologie" / "maritime_ontology.owl"
OWL_OUT = Path(__file__).parent.parent / "output" / "ontologie" / "maritime_ontology_fixed.owl"
OWL_BAK = Path(__file__).parent.parent / "output" / "ontologie" / "maritime_ontology_backup.owl"


# ═══════════════════════════════════════════════════════════════════
# FIX 1 — Labels bruts  mar:XXX_YYY → texte lisible
# ═══════════════════════════════════════════════════════════════════

def fix_labels(g: Graph) -> int:
    """Remplace les rdfs:label commençant par 'mar:' par du texte lisible."""
    count = 0
    to_remove = []
    to_add = []

    for s, p, o in g.triples((None, RDFS.label, None)):
        text = str(o)
        if not text.startswith("mar:"):
            continue

        # Retirer le préfixe mar: et le type (Activity_, Espece_, etc.)
        clean = text.replace("mar:", "")
        # Retirer le préfixe de type
        for prefix in ["Activity_", "Activite_", "Actor_", "Acteur_",
                        "Espece_", "Etat_", "Zone_", "Controle_",
                        "Exception_", "Sanction_", "Periode_",
                        "Stock_", "Concept_"]:
            if clean.startswith(prefix):
                clean = clean[len(prefix):]
                break

        # Convertir UPPER_SNAKE_CASE → phrase lisible
        clean = clean.replace("_", " ")
        # Capitaliser comme une phrase
        if clean == clean.upper():
            clean = clean.capitalize()

        lang = o.language if hasattr(o, "language") and o.language else "fr"
        to_remove.append((s, p, o))
        to_add.append((s, p, Literal(clean, lang=lang)))
        count += 1

    for triple in to_remove:
        g.remove(triple)
    for triple in to_add:
        g.add(triple)

    log.info(f"  [Fix 1] Labels nettoyés : {count}")
    return count


# ═══════════════════════════════════════════════════════════════════
# FIX 2 — Faux acteurs → ConditionApplication
# ═══════════════════════════════════════════════════════════════════

# URIs qui sont des conditions, pas des acteurs
FALSE_ACTOR_FRAGMENTS = [
    "CONFORMEMENT", "MELANGE_NON", "ABSENCE_ORGANISME", "ADOPTION_ET_MISE",
    "DUEMENT_AUTORISE", "PROTECTION_STOCK", "STOCK_AT_OR_ABOVE",
    "STOCK_BELOW_MSY", "MESURES_NATIONALES_PLUS", "OBJECTION_TO_PARAGRAPH",
    "TITULAIRE_PERMIS", "CONTRACTING_GOVERNMENT_NO_OBJECTION",
    "GOUVERNEMENTS_AYANT_OBJECTION", "LOCAL_CONSUMPTION_ONLY",
    "WHALE_CATCHERS_UNDER", "UNDER_THE_JURISDICTION",
    "ETRE_PARTIE_CONTRACTANTE",
]


def fix_false_actors(g: Graph) -> int:
    """Reclassifie les faux EtatSouverain en ConditionApplication."""
    # Créer la classe ConditionApplication si elle n'existe pas
    cond_cls = MAR.ConditionApplication
    if (cond_cls, RDF.type, OWL.Class) not in g:
        g.add((cond_cls, RDF.type, OWL.Class))
        g.add((cond_cls, RDFS.subClassOf, OWL.Thing))
        g.add((cond_cls, RDFS.label, Literal("Condition d'Application", lang="fr")))
        g.add((cond_cls, RDFS.label, Literal("Application Condition", lang="en")))
        g.add((cond_cls, SKOS.definition, Literal(
            "Condition factuelle ou juridique sous laquelle une norme s'applique ou ne s'applique pas.",
            lang="fr")))
        log.info("  [Fix 2] Classe ConditionApplication créée")

    count = 0
    to_remove = []
    to_add = []

    for s, _, _ in g.triples((None, RDF.type, MAR.EtatSouverain)):
        local = str(s).split("#")[-1]
        if any(frag in local for frag in FALSE_ACTOR_FRAGMENTS):
            to_remove.append((s, RDF.type, MAR.EtatSouverain))
            to_add.append((s, RDF.type, cond_cls))
            count += 1

    for t in to_remove:
        g.remove(t)
    for t in to_add:
        g.add(t)

    log.info(f"  [Fix 2] Faux acteurs reclassifiés : {count}")
    return count


# ═══════════════════════════════════════════════════════════════════
# FIX 3 — Déduplication entités (Espèces prioritaire)
# ═══════════════════════════════════════════════════════════════════

# Mapping : canonical URI local → list of duplicate URI locals
SPECIES_DEDUP = {
    "Espece_BaleineBleue": ["Espece_BALEINE_BLEUE", "Espece_RORQUAL_BLEU_BALAENOPTERA_MUSCULUS"],
    "Espece_BaleineBoreal": ["Espece_BOWHEAD_WHALES", "Espece_BaleineBoreal"],
    "Espece_BaleineABosse": ["Espece_BALEINE_A_BOSSE", "Espece_BALEINE_BOSSE_MEGAPTERA_NOVAEANGLIAE", "Espece_HUMPBACK_WHALES"],
    "Espece_BaleineGrise": ["Espece_BALEINE_GRISE", "Espece_BALEINE_GRISE_ESCHRICHTIUS_ROBUSTUS", "Espece_GRAY_WHALES"],
    "Espece_BaleineDeBryde": ["Espece_BRYDES_WHALE", "Espece_BRYDES_WHALES", "Espece_RORQUAL_DE_BRYDE"],
    "Espece_Cachalot": ["Espece_SPERM_WHALE", "Espece_SPERM_WHALES"],
    "Espece_Orque": ["Espece_KILLER_WHALES"],
    "Espece_PetitRorqual": ["Espece_PETIT_RORQUAL", "Espece_PETIT_RORQUAL_BALAENOPTERA_ACUTOROSTRATA",
                             "Espece_MINKE_WHALE", "Espece_MINKE_WHALES"],
    "Espece_RorqualBoreal": ["Espece_RORQUAL_BOREAL", "Espece_SEI_WHALE", "Espece_SEI_WHALES"],
    "Espece_RorqualCommun": ["Espece_RORQUAL_COMMUN", "Espece_RORQUAL_COMMUN_BALAENOPTERA_PHYSALUS", "Espece_FIN_WHALES"],
    "Espece_BaleineABec": ["Espece_BALEINE_A_BEC", "Espece_BALEINE_A_BEC_DE_BAIRD_ET_AUTRES",
                            "Espece_BALEINE_DENTEE_BEAKED_WHALE_MESOPLODON"],
}

# Canonical labels for merged species
SPECIES_LABELS = {
    "Espece_BaleineBleue":   ("Baleine bleue (Balaenoptera musculus)", "Blue Whale"),
    "Espece_BaleineBoreal":  ("Baleine boréale (Balaena mysticetus)", "Bowhead Whale"),
    "Espece_BaleineABosse":  ("Baleine à bosse (Megaptera novaeangliae)", "Humpback Whale"),
    "Espece_BaleineGrise":   ("Baleine grise (Eschrichtius robustus)", "Gray Whale"),
    "Espece_BaleineDeBryde": ("Baleine de Bryde (Balaenoptera edeni)", "Bryde's Whale"),
    "Espece_Cachalot":       ("Cachalot (Physeter macrocephalus)", "Sperm Whale"),
    "Espece_Orque":          ("Orque (Orcinus orca)", "Killer Whale"),
    "Espece_PetitRorqual":   ("Petit rorqual (Balaenoptera acutorostrata)", "Minke Whale"),
    "Espece_RorqualBoreal":  ("Rorqual boréal (Balaenoptera borealis)", "Sei Whale"),
    "Espece_RorqualCommun":  ("Rorqual commun (Balaenoptera physalus)", "Fin Whale"),
    "Espece_BaleineABec":    ("Baleine à bec (Mesoplodon spp.)", "Beaked Whale"),
}


def fix_deduplication(g: Graph) -> int:
    """Fusionne les doublons d'espèces : redirige les relations vers le canonical."""
    total_merged = 0

    for canonical_local, dup_locals in SPECIES_DEDUP.items():
        canonical_uri = MAR[canonical_local]

        # S'assurer que le canonical existe
        if (canonical_uri, RDF.type, None) not in g:
            # Le canonical n'existe pas encore, on le crée
            g.add((canonical_uri, RDF.type, MAR.EspeceMarine))
            g.add((canonical_uri, RDF.type, OWL.NamedIndividual))

        # Mettre les bons labels sur le canonical
        if canonical_local in SPECIES_LABELS:
            fr_label, en_label = SPECIES_LABELS[canonical_local]
            # Retirer les anciens labels
            for _, _, old_label in list(g.triples((canonical_uri, RDFS.label, None))):
                g.remove((canonical_uri, RDFS.label, old_label))
            g.add((canonical_uri, RDFS.label, Literal(fr_label, lang="fr")))
            g.add((canonical_uri, RDFS.label, Literal(en_label, lang="en")))

        # Fusionner chaque doublon
        for dup_local in dup_locals:
            dup_uri = MAR[dup_local]
            if (dup_uri, None, None) not in g and (None, None, dup_uri) not in g:
                continue

            # Collecter les labels du doublon comme altLabels du canonical
            for _, _, label_val in g.triples((dup_uri, RDFS.label, None)):
                text = str(label_val)
                if not text.startswith("mar:"):
                    g.add((canonical_uri, SKOS.altLabel, label_val))
            for _, _, label_val in g.triples((dup_uri, SKOS.altLabel, None)):
                g.add((canonical_uri, SKOS.altLabel, label_val))

            # Rediriger toutes les relations entrantes (?, rel, dup) → (?, rel, canonical)
            for s, p, _ in list(g.triples((None, None, dup_uri))):
                g.remove((s, p, dup_uri))
                g.add((s, p, canonical_uri))

            # Rediriger toutes les relations sortantes (dup, rel, ?) → (canonical, rel, ?)
            for _, p, o in list(g.triples((dup_uri, None, None))):
                g.remove((dup_uri, p, o))
                # Ne pas dupliquer rdf:type si déjà présent
                if p == RDF.type and (canonical_uri, RDF.type, o) in g:
                    continue
                g.add((canonical_uri, p, o))

            total_merged += 1

    log.info(f"  [Fix 3] Entités dédupliquées : {total_merged}")
    return total_merged


# ═══════════════════════════════════════════════════════════════════
# FIX 4 — xml:lang incorrects (français tagué 'en')
# ═══════════════════════════════════════════════════════════════════

FRENCH_INDICATORS = [
    " de ", " des ", " du ", " en ", " le ", " la ", " les ", " une ", " un ",
    " aux ", " au ", " dans ", " par ", " sur ", " pour ", " avec ",
    "chalut", "dragage", "pêche", "rejet", "filet", "interdiction",
    "zone ", "espèce", "navire", "marin", "côtier", "littoral",
    "exploitation", "extraction", "protection",
]


def fix_xml_lang(g: Graph) -> int:
    """Corrige les altLabels en français tagués 'en'."""
    count = 0
    to_remove = []
    to_add = []

    for s, p, o in g.triples((None, SKOS.altLabel, None)):
        if not hasattr(o, "language") or o.language != "en":
            continue
        text = str(o).lower()
        if any(indicator in text for indicator in FRENCH_INDICATORS):
            to_remove.append((s, p, o))
            to_add.append((s, p, Literal(str(o), lang="fr")))
            count += 1

    for t in to_remove:
        g.remove(t)
    for t in to_add:
        g.add(t)

    log.info(f"  [Fix 4] xml:lang corrigés : {count}")
    return count


# ═══════════════════════════════════════════════════════════════════
# FIX 5 — Hyperonymes surabondants (garder max 7 par interdiction)
# ═══════════════════════════════════════════════════════════════════

# Les hyperonymes prioritaires à conserver (les plus discriminants)
PRIORITY_HYPERNYMS = {
    "I001": [
        "Exploitation halieutique démersale",
        "Destruction des habitats benthiques",
        "Pêche non durable",
        "Surexploitation des stocks halieutiques",
        "Dégradation des écosystèmes marins vulnérables",
        "Pêche INN",
        "Pratiques de pêche destructrices",
    ],
    "I002": [
        "Chasse commerciale aux cétacés",
        "Exploitation des mammifères marins",
        "Commerce international d'espèces menacées",
        "Capture délibérée de cétacés",
        "Violation du moratoire IWC",
        "Atteinte à la biodiversité marine",
        "Prises accessoires de cétacés",
    ],
    "I003": [
        "Urbanisation du littoral",
        "Artificialisation de la zone côtière",
        "Construction en zone sensible",
        "Occupation du domaine public maritime",
        "Destruction des habitats côtiers",
        "Imperméabilisation des sols littoraux",
        "Non-respect du recul de 100 mètres",
    ],
    "I004": [
        "Extraction de sable marin",
        "Dragage des fonds marins",
        "Érosion côtière",
        "Dégradation des écosystèmes benthiques",
        "Prélèvement de matériaux marins",
        "Exploitation non durable du plateau continental",
        "Perte de biodiversité marine",
    ],
    "I005": [
        "Destruction de la faune ornithologique littorale",
        "Capture d'oiseaux marins migrateurs",
        "Perturbation d'espèces protégées",
        "Prises accessoires d'oiseaux marins",
        "Atteinte aux espèces migratrices",
        "Commerce d'oiseaux marins protégés",
        "Destruction de nids et d'habitats",
    ],
    "I006": [
        "Dégradation de l'environnement marin",
        "Pollution par hydrocarbures",
        "Rejet illicite en mer",
        "Violation MARPOL",
        "Contamination des eaux marines",
        "Pollution opérationnelle des navires",
        "Déversement accidentel d'hydrocarbures",
    ],
}


def fix_hyperonyms(g: Graph) -> int:
    """Limite les hyperonymes à ~7 prioritaires par interdiction."""
    total_removed = 0

    for icode in ["I001", "I002", "I003", "I004", "I005", "I006"]:
        i_uri = MAR[icode]
        priority_labels = [p.lower() for p in PRIORITY_HYPERNYMS.get(icode, [])]

        # Collecter tous les skos:broader actuels
        broaders = list(g.triples((i_uri, SKOS.broader, None)))

        for s, p, o in broaders:
            # Vérifier si c'est un hyperonyme prioritaire
            concept_labels = [
                str(l).lower()
                for _, _, l in g.triples((o, SKOS.prefLabel, None))
            ]
            is_priority = any(
                any(pl in cl for pl in priority_labels)
                for cl in concept_labels
            )

            if not is_priority:
                # Retirer le lien broader (mais garder le concept lui-même s'il est utilisé ailleurs)
                g.remove((s, p, o))
                total_removed += 1

    log.info(f"  [Fix 5] Hyperonymes retirés : {total_removed}")
    return total_removed


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    log.info("=" * 60)
    log.info("  CORRECTION OWL — maritime_ontology.owl")
    log.info("=" * 60)

    log.info(f"\n📂 Chargement : {OWL_IN}")
    g = Graph()
    g.parse(str(OWL_IN), format="xml")
    initial_triples = len(g)
    log.info(f"   Triples initiaux : {initial_triples}")

    # Backup
    import shutil
    shutil.copy2(OWL_IN, OWL_BAK)
    log.info(f"   Backup créé : {OWL_BAK}")

    log.info("\n── Corrections ──")
    n1 = fix_labels(g)
    n2 = fix_false_actors(g)
    n3 = fix_deduplication(g)
    n4 = fix_xml_lang(g)
    n5 = fix_hyperonyms(g)

    final_triples = len(g)

    log.info(f"\n── Résultat ──")
    log.info(f"   Triples avant : {initial_triples}")
    log.info(f"   Triples après : {final_triples}")
    log.info(f"   Delta : {final_triples - initial_triples:+d}")

    # Sérialiser
    log.info(f"\n💾 Sauvegarde : {OWL_OUT}")
    g.bind("mar", MAR)
    g.bind("lkif", LKIF)
    g.bind("skos", SKOS)
    g.bind("dct", DCT)
    g.serialize(str(OWL_OUT), format="xml")
    log.info(f"   Taille : {OWL_OUT.stat().st_size / 1024:.0f} KB")

    # Aussi écraser l'original
    g.serialize(str(OWL_IN), format="xml")
    log.info(f"   Original mis à jour : {OWL_IN}")

    log.info("\n✅ Toutes les corrections appliquées avec succès !")


if __name__ == "__main__":
    main()

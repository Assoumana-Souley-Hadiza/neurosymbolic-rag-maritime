"""
tests/test_ontology.py — Tests de validation de l'ontologie.

Couvre :
  - Présence des individus clés (I001, I002)
  - Cohérence des relations obligatoires
  - Questions de compétence (résultats non vides)
  - Intégrité référentielle
  - Statistiques minimales
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rdflib import Graph, Namespace, URIRef, RDF, RDFS, OWL
from rdflib.namespace import SKOS

NS_MAR  = "http://www.maritime-ontology.org/mar#"
NS_LKIF = "http://www.estrellaproject.org/lkif-core/lkif-core.owl#"
MAR = Namespace(NS_MAR)


def build_test_graph():
    """Construit le graphe de test (pipeline complet)."""
    import yaml
    from ontologie.pipeline import MaritimeOntologyPipeline
    pipeline = MaritimeOntologyPipeline("data/config/settings.yaml")
    # Exécuter les premières étapes manuellement pour obtenir un graphe non inféré (optionnel) ou utiliser run()
    pipeline.step_build_schema()
    data = pipeline.step_load_data()
    pipeline.step_populate(data)
    pipeline.step_inject(data)
    pipeline.step_enrich_lexical(data)
    return pipeline.g


# Partager le graphe entre les tests (construire une seule fois)
_SHARED_GRAPH = None

def get_shared_graph():
    global _SHARED_GRAPH
    if _SHARED_GRAPH is None:
        _SHARED_GRAPH = build_test_graph()
    return _SHARED_GRAPH


class TestSchemaIntegrity(unittest.TestCase):
    """Tests de la structure du schéma OWL."""

    def setUp(self):
        self.g = get_shared_graph()

    def test_owl_classes_exist(self):
        """Les classes principales doivent exister."""
        expected_classes = [
            "Interdiction", "Permission", "Obligation", "NormeJuridique",
            "Zone", "ZoneHauteMer", "ZoneSanctuaireMarin",
            "Activite", "ChalutageFond", "ChasseBaleine",
            "Acteur", "EtatPavillon", "NavirePeche",
            "Periode", "ExceptionJuridique", "Controle",
            "EspeceMarine", "BaleineMysticete", "ConceptLexical", "SourceJuridique"
        ]
        missing = []
        for cls in expected_classes:
            uri = MAR[cls]
            if (uri, RDF.type, OWL.Class) not in self.g:
                missing.append(cls)
        self.assertEqual([], missing, f"Classes manquantes : {missing}")

    def test_lkif_alignment(self):
        """Interdiction doit être sous-classe de lkif:Prohibition."""
        lkif_prohibition = URIRef(f"{NS_LKIF}Prohibition")
        self.assertIn(
            (MAR.Interdiction, RDFS.subClassOf, lkif_prohibition),
            self.g,
            "mar:Interdiction doit être rdfs:subClassOf lkif:Prohibition"
        )

    def test_object_properties_exist(self):
        """Les propriétés objet essentielles doivent exister."""
        props = [
            "appliesInZone", "concerneActivite", "concerneActeur",
            "appliesDuring", "aException", "fondeeSur", "protegeEspece"
        ]
        for p in props:
            uri = MAR[p]
            self.assertIn(
                (uri, RDF.type, OWL.ObjectProperty), self.g,
                f"Propriété objet manquante : {p}"
            )

    def test_data_properties_exist(self):
        """Les propriétés de données essentielles doivent exister."""
        props = ["deonticType", "confidence", "legalLayer", "nomScientifique"]
        for p in props:
            uri = MAR[p]
            self.assertIn(
                (uri, RDF.type, OWL.DatatypeProperty), self.g,
                f"Propriété de données manquante : {p}"
            )

    def test_disjoint_norms(self):
        """Interdiction, Permission, Obligation doivent être disjointes."""
        self.assertIn(
            (MAR.Interdiction, OWL.disjointWith, MAR.Permission), self.g,
            "Interdiction et Permission doivent être disjointes"
        )


class TestIndividuals(unittest.TestCase):
    """Tests de la population des individus."""

    def setUp(self):
        self.g = get_shared_graph()

    def test_i001_exists(self):
        """L'interdiction I001 (Chalutage de Fond) doit exister."""
        i001 = MAR["I001"]
        self.assertIn((i001, RDF.type, OWL.NamedIndividual), self.g)
        self.assertIn((i001, RDF.type, MAR.Interdiction), self.g)

    def test_i002_exists(self):
        """L'interdiction I002 (Chasse Baleine) doit exister."""
        i002 = MAR["I002"]
        self.assertIn((i002, RDF.type, OWL.NamedIndividual), self.g)
        self.assertIn((i002, RDF.type, MAR.Interdiction), self.g)

    def test_i001_has_activity(self):
        """I001 doit être lié à une activité de chalutage."""
        i001 = MAR["I001"]
        activities = list(self.g.objects(i001, MAR.concerneActivite))
        self.assertGreater(len(activities), 0, "I001 doit avoir au moins une activité")

    def test_i001_has_zones(self):
        """I001 doit s'appliquer dans au moins une zone."""
        i001 = MAR["I001"]
        zones = list(self.g.objects(i001, MAR.appliesInZone))
        self.assertGreater(len(zones), 0, "I001 doit avoir au moins une zone")

    def test_i002_protects_species(self):
        """I002 doit protéger des espèces baleinières."""
        i002 = MAR["I002"]
        species = list(self.g.objects(i002, MAR.protegeEspece))
        self.assertGreater(len(species), 0, "I002 doit protéger au moins une espèce")

    def test_i001_has_exceptions(self):
        """I001 doit avoir des exceptions définies."""
        i001 = MAR["I001"]
        exceptions = list(self.g.objects(i001, MAR.aException))
        self.assertGreater(len(exceptions), 0, "I001 doit avoir au moins une exception")

    def test_i002_has_legal_sources(self):
        """I002 doit être fondé sur des sources juridiques."""
        i002 = MAR["I002"]
        sources = list(self.g.objects(i002, MAR.fondeeSur))
        self.assertGreater(len(sources), 0, "I002 doit avoir des sources juridiques")

    def test_zones_are_typed(self):
        """Toutes les zones doivent avoir un type OWL."""
        zones_triples = list(self.g.subjects(MAR.appliesInZone.__class__, MAR.appliesInZone))
        zone_uris = set(self.g.objects(MAR["I001"], MAR.appliesInZone))
        zone_uris |= set(self.g.objects(MAR["I002"], MAR.appliesInZone))
        for z_uri in zone_uris:
            types = list(self.g.objects(z_uri, RDF.type))
            self.assertGreater(len(types), 0, f"Zone {z_uri} doit être typée")

    def test_lexical_concepts_exist(self):
        """Des concepts lexicaux doivent être créés."""
        concepts = list(self.g.subjects(RDF.type, MAR.ConceptLexical))
        self.assertGreater(len(concepts), 5, "Moins de 5 concepts lexicaux trouvés")

    def test_whale_species_have_scientific_names(self):
        """Les espèces baleinières doivent avoir des noms scientifiques."""
        species = list(self.g.subjects(RDF.type, MAR.BaleineMysticete))
        species_with_names = [
            s for s in species
            if list(self.g.objects(s, MAR.nomScientifique))
        ]
        self.assertGreater(len(species_with_names), 0,
                           "Au moins une espèce doit avoir un nom scientifique")


class TestSPARQL(unittest.TestCase):
    """Tests des questions de compétence SPARQL."""

    def setUp(self):
        self.g = get_shared_graph()

    def test_cq1_interdictions(self):
        """CQ1 : Doit retourner les interdictions I001 et I002."""
        results = list(self.g.query("""
            PREFIX mar: <http://www.maritime-ontology.org/mar#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT ?i WHERE { ?i rdf:type mar:Interdiction }
        """))
        self.assertGreaterEqual(len(results), 2, "Doit y avoir au moins 2 interdictions")

    def test_cq2_zones_i001(self):
        """CQ2 : I001 doit s'appliquer dans des zones."""
        results = list(self.g.query("""
            PREFIX mar: <http://www.maritime-ontology.org/mar#>
            SELECT ?z WHERE { mar:I001 mar:appliesInZone ?z }
        """))
        self.assertGreater(len(results), 0, "I001 doit avoir des zones")

    def test_cq6_protected_species(self):
        """CQ6 : I002 doit protéger des espèces."""
        results = list(self.g.query("""
            PREFIX mar: <http://www.maritime-ontology.org/mar#>
            SELECT ?e WHERE { mar:I002 mar:protegeEspece ?e }
        """))
        self.assertGreater(len(results), 0, "I002 doit protéger des espèces")

    def test_cq7_sources_juridiques(self):
        """CQ7 : Les interdictions doivent avoir des sources juridiques."""
        results = list(self.g.query("""
            PREFIX mar: <http://www.maritime-ontology.org/mar#>
            SELECT ?i ?s WHERE { ?i mar:fondeeSur ?s }
        """))
        self.assertGreater(len(results), 0, "Doit y avoir des sources juridiques")


class TestStatistics(unittest.TestCase):
    """Tests statistiques minimaux."""

    def setUp(self):
        self.g = get_shared_graph()

    def test_minimum_triples(self):
        """Le graphe doit contenir un minimum de triplets."""
        self.assertGreater(len(self.g), 200, "Graphe trop petit (<200 triplets)")

    def test_minimum_individuals(self):
        """Doit y avoir un minimum d'individus."""
        count = sum(1 for _, p, o in self.g if p == RDF.type and o == OWL.NamedIndividual)
        self.assertGreater(count, 30, f"Trop peu d'individus: {count}")

    def test_minimum_classes(self):
        """Doit y avoir un minimum de classes."""
        count = sum(1 for _, p, o in self.g if p == RDF.type and o == OWL.Class)
        self.assertGreater(count, 20, f"Trop peu de classes: {count}")


if __name__ == "__main__":
    unittest.main(verbosity=2)

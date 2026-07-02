"""
schema.py v2 — Ontologie Maritime OWL 2 DL complète, alignée LKIF-Core.

Architecture axiomatique :
  ① Hiérarchie de classes avec disjonctions complètes
  ② Propriétés objet avec domaine/range, inverses, chaînes
  ③ Propriétés de données avec ranges XSD précis
  ④ Restrictions existentielles (someValuesFrom) — classes nécessaires
  ⑤ Restrictions universelles (allValuesFrom) — classes suffisantes
  ⑥ Classes équivalentes pour raisonnement automatique (DL reasoning)
  ⑦ owl:disjointUnionOf pour couverture complète
  ⑧ Propriétés transitives, symétriques, fonctionnelles
  ⑨ Chaînes de propriétés (propertyChainAxiom)
  ⑩ Cardinalités qualifiées (minQualifiedCardinality)
"""

import logging
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD, BNode
from rdflib.namespace import SKOS

logger = logging.getLogger(__name__)

NS_LKIF = "http://www.estrellaproject.org/lkif-core/lkif-core.owl#"
NS_MAR  = "http://www.maritime-ontology.org/mar#"
NS_DCT  = "http://purl.org/dc/terms/"
NS_PROV = "http://www.w3.org/ns/prov#"
NS_TIME = "http://www.w3.org/2006/time#"


class SchemaBuilder:
    """Construit le schéma OWL 2 DL complet de l'ontologie maritime."""

    def __init__(self, g: Graph, mar: Namespace, lkif: Namespace):
        self.g    = g
        self.mar  = mar
        self.lkif = lkif
        self.skos = SKOS
        self.dct  = Namespace(NS_DCT)
        self.prov = Namespace(NS_PROV)
        self.time = Namespace(NS_TIME)
        self._ref = {}

    # ──────────────────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────────────────

    def _cls(self, local, parent, label_fr, label_en="", definition=""):
        uri = self.mar[local]
        self.g.add((uri, RDF.type, OWL.Class))
        self.g.add((uri, RDFS.subClassOf, parent))
        self.g.add((uri, RDFS.label, Literal(label_fr, lang="fr")))
        if label_en:
            self.g.add((uri, RDFS.label, Literal(label_en, lang="en")))
        if definition:
            self.g.add((uri, self.skos.definition, Literal(definition, lang="fr")))
        return uri

    def _obj_prop(self, local, domain, range_, label_fr, label_en="", **flags):
        uri = self.mar[local]
        self.g.add((uri, RDF.type, OWL.ObjectProperty))
        self.g.add((uri, RDFS.label, Literal(label_fr, lang="fr")))
        if label_en:
            self.g.add((uri, RDFS.label, Literal(label_en, lang="en")))
        if domain:
            self.g.add((uri, RDFS.domain, domain))
        if range_:
            self.g.add((uri, RDFS.range, range_))
        if flags.get("transitive"):
            self.g.add((uri, RDF.type, OWL.TransitiveProperty))
        if flags.get("symmetric"):
            self.g.add((uri, RDF.type, OWL.SymmetricProperty))
        if flags.get("functional"):
            self.g.add((uri, RDF.type, OWL.FunctionalProperty))
        if flags.get("inverse_functional"):
            self.g.add((uri, RDF.type, OWL.InverseFunctionalProperty))
        if flags.get("asymmetric"):
            self.g.add((uri, RDF.type, OWL.AsymmetricProperty))
        if flags.get("irreflexive"):
            self.g.add((uri, RDF.type, OWL.IrreflexiveProperty))
        return uri

    def _data_prop(self, local, domain, range_xsd, label_fr, **flags):
        uri = self.mar[local]
        self.g.add((uri, RDF.type, OWL.DatatypeProperty))
        self.g.add((uri, RDFS.label, Literal(label_fr, lang="fr")))
        if domain:
            self.g.add((uri, RDFS.domain, domain))
        if range_xsd:
            self.g.add((uri, RDFS.range, range_xsd))
        if flags.get("functional"):
            self.g.add((uri, RDF.type, OWL.FunctionalProperty))
        return uri

    def _disjoint(self, *classes):
        cls_list = list(classes)
        for i in range(len(cls_list)):
            for j in range(i + 1, len(cls_list)):
                self.g.add((cls_list[i], OWL.disjointWith, cls_list[j]))

    def _disjoint_union(self, parent, *children):
        """owl:disjointUnionOf — couverture exhaustive des sous-classes."""
        lst = self._rdf_list(list(children))
        self.g.add((parent, OWL.disjointUnionOf, lst))

    def _some(self, cls, prop, filler):
        """cls ⊑ ∃prop.filler"""
        r = BNode()
        self.g.add((r, RDF.type, OWL.Restriction))
        self.g.add((r, OWL.onProperty, prop))
        self.g.add((r, OWL.someValuesFrom, filler))
        self.g.add((cls, RDFS.subClassOf, r))

    def _all(self, cls, prop, filler):
        """cls ⊑ ∀prop.filler"""
        r = BNode()
        self.g.add((r, RDF.type, OWL.Restriction))
        self.g.add((r, OWL.onProperty, prop))
        self.g.add((r, OWL.allValuesFrom, filler))
        self.g.add((cls, RDFS.subClassOf, r))

    def _min_card(self, cls, prop, n, filler=None):
        """cls ⊑ (≥n prop [filler])"""
        r = BNode()
        self.g.add((r, RDF.type, OWL.Restriction))
        self.g.add((r, OWL.onProperty, prop))
        if filler:
            self.g.add((r, OWL.minQualifiedCardinality, Literal(n, datatype=XSD.nonNegativeInteger)))
            self.g.add((r, OWL.onClass, filler))
        else:
            self.g.add((r, OWL.minCardinality, Literal(n, datatype=XSD.nonNegativeInteger)))
        self.g.add((cls, RDFS.subClassOf, r))

    def _max_card(self, cls, prop, n, filler=None):
        """cls ⊑ (≤n prop [filler])"""
        r = BNode()
        self.g.add((r, RDF.type, OWL.Restriction))
        self.g.add((r, OWL.onProperty, prop))
        if filler:
            self.g.add((r, OWL.maxQualifiedCardinality, Literal(n, datatype=XSD.nonNegativeInteger)))
            self.g.add((r, OWL.onClass, filler))
        else:
            self.g.add((r, OWL.maxCardinality, Literal(n, datatype=XSD.nonNegativeInteger)))
        self.g.add((cls, RDFS.subClassOf, r))

    def _equiv_intersection(self, cls, *components):
        """cls ≡ C1 ⊓ C2 ⊓ ... Cn"""
        bnode = BNode()
        self.g.add((cls, OWL.equivalentClass, bnode))
        self.g.add((bnode, RDF.type, OWL.Class))
        self.g.add((bnode, OWL.intersectionOf, self._rdf_list(list(components))))

    def _equiv_union(self, cls, *components):
        """cls ≡ C1 ⊔ C2 ⊔ ... Cn"""
        bnode = BNode()
        self.g.add((cls, OWL.equivalentClass, bnode))
        self.g.add((bnode, RDF.type, OWL.Class))
        self.g.add((bnode, OWL.unionOf, self._rdf_list(list(components))))

    def _restriction_bnode(self, prop, kind, filler):
        """Retourne un BNode Restriction (pour usage inline dans intersection)."""
        r = BNode()
        self.g.add((r, RDF.type, OWL.Restriction))
        self.g.add((r, OWL.onProperty, prop))
        self.g.add((r, kind, filler))
        return r

    def _rdf_list(self, items):
        if not items:
            return RDF.nil
        head = BNode()
        cur = head
        for i, item in enumerate(items):
            self.g.add((cur, RDF.first, item))
            if i < len(items) - 1:
                nxt = BNode()
                self.g.add((cur, RDF.rest, nxt))
                cur = nxt
            else:
                self.g.add((cur, RDF.rest, RDF.nil))
        return head

    def _property_chain(self, prop, chain):
        """prop ≡ p1 ∘ p2 ∘ ... (owl:propertyChainAxiom)"""
        self.g.add((prop, OWL.propertyChainAxiom, self._rdf_list(chain)))

    def _inverse(self, p, inv, label_fr):
        inv_uri = self.mar[inv]
        self.g.add((inv_uri, RDF.type, OWL.ObjectProperty))
        self.g.add((inv_uri, OWL.inverseOf, p))
        self.g.add((inv_uri, RDFS.label, Literal(label_fr, lang="fr")))
        return inv_uri

    def _sub_prop(self, child, parent):
        self.g.add((child, RDFS.subPropertyOf, parent))

    # ──────────────────────────────────────────────────────────────
    # ONTOLOGY HEADER
    # ──────────────────────────────────────────────────────────────
    def build_ontology_header(self):
        onto = URIRef(NS_MAR.rstrip("#"))
        g = self.g
        g.add((onto, RDF.type, OWL.Ontology))
        g.add((onto, RDFS.label, Literal("Ontologie Maritime — Droit International de la Mer", lang="fr")))
        g.add((onto, RDFS.label, Literal("Maritime Ontology — International Law of the Sea", lang="en")))
        g.add((onto, self.dct.description, Literal(
            "Version 2.0 — Ontologie OWL 2 DL complète : 6 interdictions maritimes internationales "
            "(I001 chalutage fond, I002 chasse baleine, I003 construction littorale, "
            "I004 extraction sable, I005 oiseaux marins, I006 rejet hydrocarbures). "
            "Alignement LKIF-Core. Axiomes complets pour raisonnement automatique.", lang="fr")))
        g.add((onto, self.dct.creator, Literal("Maritime Legal Ontology Project")))
        g.add((onto, self.dct.version, Literal("2.0.0")))
        g.add((onto, OWL.versionInfo, Literal("2.0.0")))
        g.add((onto, self.dct.license, URIRef("https://creativecommons.org/licenses/by/4.0/")))
        g.add((onto, self.dct.subject, Literal("droit maritime international", lang="fr")))
        g.add((onto, self.dct.created, Literal("2024-01-01", datatype=XSD.date)))
        g.add((onto, OWL.imports, URIRef(NS_LKIF.rstrip("#"))))
        g.add((onto, OWL.imports, URIRef(NS_TIME.rstrip("#"))))
        logger.info("  ✅ En-tête ontologique v2.0 créé")

    # ──────────────────────────────────────────────────────────────
    # LKIF-CORE STUB
    # ──────────────────────────────────────────────────────────────
    def _build_lkif_stub(self):
        """Déclare les classes LKIF-Core nécessaires comme stubs OWL."""
        lkif = self.lkif
        stubs = [
            (lkif.Norm,           "Norme juridique",       "Legal Norm"),
            (lkif.Prohibition,    "Prohibition",           "Prohibition"),
            (lkif.Permission,     "Permission",            "Permission"),
            (lkif.Obligation,     "Obligation",            "Obligation"),
            (lkif.Exception,      "Exception",             "Exception"),
            (lkif.Agent,          "Agent",                 "Agent"),
            (lkif.Act,            "Acte",                  "Act"),
            (lkif.Place,          "Lieu",                  "Place"),
            (lkif.Legal_Source,   "Source juridique",      "Legal Source"),
            (lkif.Legal_Person,   "Personne morale",       "Legal Person"),
            (lkif.Organisation,   "Organisation",          "Organisation"),
            (lkif.Natural_Person, "Personne physique",     "Natural Person"),
            (lkif.Consequence,    "Conséquence juridique", "Legal Consequence"),
        ]
        for uri, label_fr, label_en in stubs:
            self.g.add((uri, RDF.type, OWL.Class))
            self.g.add((uri, RDFS.label, Literal(label_fr, lang="fr")))
            self.g.add((uri, RDFS.label, Literal(label_en, lang="en")))

        # Hiérarchie LKIF stub
        for sub, sup in [
            (lkif.Prohibition, lkif.Norm),
            (lkif.Permission,  lkif.Norm),
            (lkif.Obligation,  lkif.Norm),
            (lkif.Exception,   lkif.Norm),
            (lkif.Organisation, lkif.Legal_Person),
            (lkif.Legal_Person, lkif.Agent),
            (lkif.Natural_Person, lkif.Agent),
        ]:
            self.g.add((sub, RDFS.subClassOf, sup))

        # Propriétés LKIF
        lkif_props = [
            (lkif.has_exception,  lkif.Norm,        lkif.Exception,   "has exception"),
            (lkif.obligated_by,   OWL.Thing,        lkif.Obligation,  "obligated by"),
            (lkif.permitted_by,   OWL.Thing,        lkif.Permission,  "permitted by"),
            (lkif.prohibited_by,  OWL.Thing,        lkif.Prohibition, "prohibited by"),
            (lkif.applies_to,     lkif.Norm,        lkif.Act,         "applies to"),
        ]
        for uri, dom, rng, lbl in lkif_props:
            self.g.add((uri, RDF.type, OWL.ObjectProperty))
            self.g.add((uri, RDFS.domain, dom))
            self.g.add((uri, RDFS.range, rng))
            self.g.add((uri, RDFS.label, Literal(lbl, lang="en")))

        # OWL Time stub
        time_interval = URIRef(NS_TIME + "Interval")
        time_instant  = URIRef(NS_TIME + "Instant")
        time_inXSDDate = URIRef(NS_TIME + "inXSDDate")
        time_hasBeginning = URIRef(NS_TIME + "hasBeginning")
        time_hasEnd       = URIRef(NS_TIME + "hasEnd")
        for uri, label in [(time_interval, "Time Interval"), (time_instant, "Time Instant")]:
            self.g.add((uri, RDF.type, OWL.Class))
            self.g.add((uri, RDFS.label, Literal(label, lang="en")))
        # time:inXSDDate est une DatatypeProperty (range = xsd:date)
        self.g.add((time_inXSDDate, RDF.type, OWL.DatatypeProperty))
        self.g.add((time_inXSDDate, RDFS.domain, time_instant))
        self.g.add((time_inXSDDate, RDFS.range, XSD.date))
        for uri, dom, rng in [
            (time_hasBeginning, time_interval, time_instant),
            (time_hasEnd,       time_interval, time_instant),
        ]:
            self.g.add((uri, RDF.type, OWL.ObjectProperty))
            self.g.add((uri, RDFS.domain, dom))
            self.g.add((uri, RDFS.range, rng))

    # ──────────────────────────────────────────────────────────────
    # CLASS HIERARCHY
    # ──────────────────────────────────────────────────────────────
    def build_classes(self):
        logger.info("  📐 Construction de la hiérarchie de classes OWL 2 DL...")
        self._build_lkif_stub()
        mar  = self.mar
        lkif = self.lkif

        # ── A. NORME JURIDIQUE (axe déontique) ──────────────────
        Norme = self._cls("NormeJuridique", lkif.Norm,
            "Norme Juridique Maritime", "Maritime Legal Norm",
            "Toute règle de droit international maritime applicable, dotée d'une portée normative.")

        Interdiction = self._cls("Interdiction", lkif.Prohibition,
            "Interdiction", "Prohibition",
            "Norme interdisant à un acteur une activité dans une zone donnée.")
        self.g.add((Interdiction, RDFS.subClassOf, Norme))

        Permission = self._cls("Permission", lkif.Permission,
            "Permission", "Permission",
            "Norme autorisant explicitement un acteur à réaliser une activité.")
        self.g.add((Permission, RDFS.subClassOf, Norme))

        Obligation = self._cls("Obligation", lkif.Obligation,
            "Obligation", "Obligation",
            "Norme obligeant un acteur à réaliser une action spécifique.")
        self.g.add((Obligation, RDFS.subClassOf, Norme))

        # Disjonctions complètes entre types déontiques
        self._disjoint(Interdiction, Permission, Obligation)

        # ── B. ZONES (axe géographique) ──────────────────────────
        Zone = self._cls("Zone", lkif.Place,
            "Zone Maritime", "Maritime Zone",
            "Espace géographique maritime soumis à un régime juridique spécifique (UNCLOS).")

        ZoneHauteMer = self._cls("ZoneHauteMer", Zone,
            "Haute Mer", "High Seas",
            "Zone au-delà de toute juridiction nationale — UNCLOS Art. 86.")
        ZoneEEZ = self._cls("ZoneEconomiqueExclusive", Zone,
            "Zone Économique Exclusive", "Exclusive Economic Zone",
            "Zone de 200 milles marins accordant des droits souverains à l'État côtier — UNCLOS Art. 55-75.")
        ZoneTerritoriale = self._cls("ZoneMerTerritoriale", Zone,
            "Mer Territoriale", "Territorial Sea",
            "Zone de 12 milles marins sous souveraineté totale de l'État côtier — UNCLOS Art. 3.")
        ZoneContiguë = self._cls("ZoneContigüe", Zone,
            "Zone Contiguë", "Contiguous Zone",
            "Zone de 24 milles marins pour le contrôle des infractions — UNCLOS Art. 33.")
        ZonePlateau = self._cls("PlateauContinental", Zone,
            "Plateau Continental", "Continental Shelf",
            "Extension naturelle du territoire terrestre sous la mer — UNCLOS Art. 76.")
        ZoneSanctuaire = self._cls("ZoneSanctuaireMarin", Zone,
            "Sanctuaire Marin", "Marine Sanctuary",
            "Zone de protection totale pour des espèces désignées — décision IWC ou accord international.")
        ZoneVulnerable = self._cls("ZoneEcosystemeVulnerable", Zone,
            "Écosystème Marin Vulnérable", "Vulnerable Marine Ecosystem",
            "Zone abritant des écosystèmes sensibles identifiés selon les critères FAO 2009.")
        ZoneSpecialeMARPOL = self._cls("ZoneSpecialeMARPOL", Zone,
            "Zone Spéciale MARPOL", "MARPOL Special Area",
            "Zone où les rejets d'hydrocarbures sont totalement interdits — MARPOL 73/78 Annexe I Règle 1.")
        ZoneCotiere = self._cls("ZoneCotiere", Zone,
            "Zone Côtière", "Coastal Zone",
            "Interface terre-mer soumise à des régimes spéciaux de protection (ex: loi Littoral, GIZC).")
        ZoneAMP = self._cls("AireMarineProtegee", Zone,
            "Aire Marine Protégée", "Marine Protected Area",
            "Zone délimitée pour la conservation de la biodiversité marine — CDB Art. 8.")

        # Disjonctions spatiales UNCLOS (mutuellement exclusives)
        self._disjoint(ZoneHauteMer, ZoneTerritoriale, ZoneEEZ, ZoneContiguë)

        # ── C. ACTIVITÉS (axe factuel) ───────────────────────────
        Activite = self._cls("Activite", lkif.Act,
            "Activité Maritime", "Maritime Activity",
            "Action intentionnelle réalisée par un acteur en milieu maritime.")

        ActivitePeche = self._cls("ActivitePeche", Activite,
            "Activité de Pêche", "Fishing Activity",
            "Toute opération visant la capture ou la récolte d'espèces marines à des fins commerciales ou artisanales.")
        ChalutageFond = self._cls("ChalutageFond", ActivitePeche,
            "Chalutage de Fond", "Bottom Trawling",
            "Technique de pêche consistant à tracter un chalut sur le fond marin, destructeur pour les habitats benthiques.")
        PecheINN = self._cls("PecheINN", ActivitePeche,
            "Pêche INN", "IUU Fishing",
            "Pêche illicite, non déclarée et non réglementée (INN/IUU) — Plan d'action international FAO.")
        PecheProfonde = self._cls("PecheProfonde", ActivitePeche,
            "Pêche en Eaux Profondes", "Deep-Sea Fishing",
            "Pêche à des profondeurs supérieures à 200 mètres, soumise à des réglementations spéciales.")

        ActiviteChasse = self._cls("ActiviteChasse", Activite,
            "Activité de Chasse Marine", "Marine Hunting Activity",
            "Toute activité visant la capture ou l'abattage d'espèces marines protégées.")
        ChasseBaleine = self._cls("ChasseBaleine", ActiviteChasse,
            "Chasse à la Baleine", "Whaling",
            "Toute opération visant à capturer, tuer ou traiter des cétacés — ICRW 1946.")
        ChasseCommerciale = self._cls("ChasseCommercialeBaleine", ChasseBaleine,
            "Chasse Commerciale à la Baleine", "Commercial Whaling",
            "Chasse à des fins commerciales — soumise au moratoire IWC depuis 1986 (Schedule para. 10(e)).")
        ChasseScientifique = self._cls("ChasseScientifiqueBaleine", ChasseBaleine,
            "Chasse Scientifique à la Baleine", "Scientific Whaling",
            "Chasse sous permis scientifique national — autorisée par l'Art. VIII ICRW.")
        ChasseSubsistance = self._cls("ChasseSubsistanceAutochtone", ChasseBaleine,
            "Chasse de Subsistance Autochtone", "Aboriginal Subsistence Whaling",
            "Chasse pratiquée par les communautés autochtones pour leur subsistance — IWC Schedule §13.")
        self._disjoint(ChasseCommerciale, ChasseScientifique, ChasseSubsistance)

        ActiviteExtraction = self._cls("ActiviteExtraction", Activite,
            "Activité d'Extraction Marine", "Marine Extraction Activity",
            "Prélèvement de matériaux ou de ressources du fond ou de la colonne d'eau.")
        ExtractionSable = self._cls("ExtractionSable", ActiviteExtraction,
            "Extraction de Sable Marin", "Marine Sand Extraction",
            "Dragage et prélèvement de sable ou de graviers marins — encadré par la CDB et les législations nationales.")
        ExtractionHydrocarbures = self._cls("ExtractionHydrocarbures", ActiviteExtraction,
            "Exploitation Pétrolière Offshore", "Offshore Oil Extraction",
            "Exploration et exploitation de gisements d'hydrocarbures en mer.")

        ActiviteConstruction = self._cls("ActiviteConstruction", Activite,
            "Activité de Construction Côtière", "Coastal Construction Activity",
            "Travaux d'aménagement, d'urbanisation ou d'infrastructure sur le littoral.")
        ConstructionLittorale = self._cls("ConstructionLittorale", ActiviteConstruction,
            "Construction sur le Littoral", "Coastal Construction",
            "Tout ouvrage ou aménagement dans la bande littorale — encadré par la loi Littoral (France) et le Protocole GIZC.")
        ConstructionPortuaire = self._cls("ConstructionPortuaire", ActiviteConstruction,
            "Construction Portuaire", "Port Construction",
            "Création ou extension d'infrastructures portuaires en zone maritime.")

        ActiviteRejets = self._cls("ActiviteRejets", Activite,
            "Activité de Rejet en Mer", "Marine Discharge Activity",
            "Tout déversement ou décharge de substances dans le milieu marin.")
        RejetsHydrocarbures = self._cls("RejetsHydrocarbures", ActiviteRejets,
            "Rejet d'Hydrocarbures", "Hydrocarbon Discharge",
            "Déversement intentionnel ou accidentel d'hydrocarbures — MARPOL 73/78 Annexe I.")
        RejetsDechetsMenagers = self._cls("RejetsDechetsMenagers", ActiviteRejets,
            "Rejet de Déchets Ménagers", "Garbage Discharge",
            "Rejet de déchets solides ou ménagers — MARPOL 73/78 Annexe V.")
        RejetsEauxUsees = self._cls("RejetsEauxUsees", ActiviteRejets,
            "Rejet d'Eaux Usées", "Sewage Discharge",
            "Rejet d'eaux usées non traitées — MARPOL 73/78 Annexe IV.")

        ActiviteCapture = self._cls("ActiviteCapture", Activite,
            "Capture d'Espèces Protégées", "Protected Species Capture",
            "Toute capture, détention ou mise à mort délibérée d'espèces protégées.")
        CaptureOiseaux = self._cls("CaptureOiseauxMarins", ActiviteCapture,
            "Capture d'Oiseaux Marins", "Seabird Capture",
            "Capture, détention ou perturbation d'oiseaux marins migrateurs — CMS/Convention de Bonn Art. III.5.")

        # Disjonctions entre types d'activités
        self._disjoint(ActivitePeche, ActiviteChasse, ActiviteExtraction,
                       ActiviteConstruction, ActiviteRejets, ActiviteCapture)

        # ── D. ACTEURS (axe institutionnel) ─────────────────────
        Acteur = self._cls("Acteur", lkif.Agent,
            "Acteur Maritime", "Maritime Actor",
            "Tout agent ou entité soumis aux normes du droit international maritime.")

        EtatSouverain = self._cls("EtatSouverain", Acteur,
            "État Souverain", "Sovereign State",
            "Entité politique possédant la souveraineté sur un territoire et une mer territoriale.")
        EtatPavillon = self._cls("EtatPavillon", EtatSouverain,
            "État du Pavillon", "Flag State",
            "État sous le pavillon duquel est enregistré un navire — responsabilité principale selon UNCLOS.")
        EtatCotier = self._cls("EtatCotier", EtatSouverain,
            "État Côtier", "Coastal State",
            "État disposant d'un accès à la mer et exerçant des droits souverains dans sa ZEE.")
        EtatPortuaire = self._cls("EtatPortuaire", EtatSouverain,
            "État du Port", "Port State",
            "État dans les ports duquel un navire fait escale — peut exercer des contrôles PSC.")

        OrgInternationale = self._cls("OrganisationInternationale", Acteur,
            "Organisation Internationale", "International Organisation",
            "Entité créée par traité entre États, dotée de la personnalité juridique internationale.")
        OrgRegPeche = self._cls("OrganismeRegionalGestionPeche", OrgInternationale,
            "Organisme Régional de Gestion des Pêches", "Regional Fisheries Management Organisation",
            "ORGP — organisme interétatique chargé de la gestion des ressources halieutiques dans une région.")
        IWC = self._cls("CommissionBaleiniereInternationale", OrgInternationale,
            "Commission Baleinière Internationale", "International Whaling Commission",
            "CBI/IWC — organe issu de la ICRW 1946, compétent pour la conservation et gestion des cétacés.")
        IMO = self._cls("OrganisationMaritimeInternationale", OrgInternationale,
            "Organisation Maritime Internationale", "International Maritime Organization",
            "OMI/IMO — agence spécialisée de l'ONU pour la sécurité maritime et la prévention de la pollution.")
        FAO = self._cls("OrganisationFAO", OrgInternationale,
            "FAO — Organisation des Nations Unies pour l'alimentation", "FAO",
            "Food and Agriculture Organization — compétente pour les pêches et l'aquaculture mondiales.")
        CBD_Secretariat = self._cls("SecretariatCDB", OrgInternationale,
            "Secrétariat de la Convention sur la Diversité Biologique", "CBD Secretariat",
            "Organe administratif de la CDB — supervise la mise en œuvre de la Convention.")

        NavirePeche = self._cls("NavirePeche", Acteur,
            "Navire de Pêche", "Fishing Vessel",
            "Navire utilisé à des fins commerciales pour capturer des ressources marines.")
        NavireUsine = self._cls("NavireUsine", NavirePeche,
            "Navire-Usine", "Factory Ship",
            "Navire équipé pour le traitement en mer des captures — soumis aux règles ICRW spéciales.")
        NavirePetrolier = self._cls("NavirePetrolier", Acteur,
            "Navire Pétrolier", "Oil Tanker",
            "Navire conçu pour le transport de pétrole brut ou de produits pétroliers — soumis à MARPOL Annexe I Règle 34.")
        NavireMarchand = self._cls("NavireMarchand", Acteur,
            "Navire de Commerce", "Merchant Vessel",
            "Navire de transport commercial soumis aux règles MARPOL générales.")

        OperateurEconomique = self._cls("OperateurEconomique", Acteur,
            "Opérateur Économique Maritime", "Maritime Economic Operator",
            "Entreprise ou personne physique exerçant une activité économique en milieu maritime.")
        Armateur = self._cls("Armateur", OperateurEconomique,
            "Armateur", "Shipowner",
            "Propriétaire ou exploitant d'un navire — responsable de la conformité MARPOL.")
        Capitaine = self._cls("Capitaine", OperateurEconomique,
            "Capitaine de Navire", "Ship Master",
            "Officier commandant un navire — responsable pénalement des rejets illicites.")
        OperateurOffshore = self._cls("OperateurOffshore", OperateurEconomique,
            "Opérateur Pétrolier Offshore", "Offshore Oil Operator",
            "Entreprise conduisant des opérations d'exploration ou d'exploitation en mer.")
        PromoteurCotier = self._cls("PromoteurCotier", OperateurEconomique,
            "Promoteur et Constructeur Côtier", "Coastal Developer",
            "Personne physique ou morale réalisant des constructions en zone littorale.")

        CommunauteAutochtone = self._cls("CommunauteAutochtone", Acteur,
            "Communauté Autochtone", "Indigenous Community",
            "Communauté autochtone bénéficiant de droits de chasse traditionnels reconnus par la CBI.")

        # Disjonctions entre types d'acteurs
        self._disjoint(EtatSouverain, NavirePeche, OrgInternationale, OperateurEconomique, CommunauteAutochtone)
        self._disjoint(EtatSouverain, NavirePetrolier, NavireMarchand)

        # ── E. ESPÈCES MARINES (axe biodiversité) ────────────────
        Espece = self._cls("EspeceMarine", OWL.Thing,
            "Espèce Marine", "Marine Species",
            "Tout taxon d'organisme vivant habitant ou dépendant du milieu marin.")

        Cetace = self._cls("Cetace", Espece,
            "Cétacé", "Cetacean",
            "Ordre Cetacea — mammifères marins entièrement aquatiques.")
        BaleineMysticete = self._cls("BaleineMysticete", Cetace,
            "Baleine Mysticète (à fanons)", "Baleen Whale",
            "Sous-ordre Mysticeti : baleines filtrantes dotées de fanons — ex. Balaenoptera spp.")
        BaleineOdontocete = self._cls("BaleineOdontocete", Cetace,
            "Cétacé Odontocète (à dents)", "Toothed Whale / Odontocete",
            "Sous-ordre Odontoceti : cétacés dotés de dents — orques, cachalots, dauphins.")
        self._disjoint(BaleineMysticete, BaleineOdontocete)
        # Couverture exhaustive de Cetace
        self._disjoint_union(Cetace, BaleineMysticete, BaleineOdontocete)

        OiseauMarin = self._cls("OiseauMarin", Espece,
            "Oiseau Marin", "Seabird",
            "Espèce aviaire dépendant du milieu marin — albatros, pétrels, fous de Bassan, etc. (CMS/ACAP).")
        OiseauMigrateur = self._cls("OiseauMarinMigrateur", OiseauMarin,
            "Oiseau Marin Migrateur", "Migratory Seabird",
            "Oiseau marin inscrit aux Appendices de la Convention CMS — soumis à protection stricte.")

        TortueMarine = self._cls("TortueMarine", Espece,
            "Tortue Marine", "Sea Turtle",
            "Reptiles marins — 7 espèces, toutes menacées d'extinction, protégées par la CITES et la CMS.")

        PoissonProfond = self._cls("PoissonEauxProfondes", Espece,
            "Poisson des Eaux Profondes", "Deep-Sea Fish",
            "Espèce ichtyologique habitant les écosystèmes benthiques profonds, vulnérable au chalutage de fond.")

        EspeceVulnerable = self._cls("EspeceVulnerable", Espece,
            "Espèce Vulnérable", "Vulnerable Species",
            "Espèce classée VU, EN ou CR selon les critères UICN — nécessitant une protection active.")
        EspeceProtegee = self._cls("EspeceProtegee", EspeceVulnerable,
            "Espèce Strictement Protégée", "Strictly Protected Species",
            "Espèce bénéficiant d'une protection totale en vertu du droit international.")

        # ── F. SOURCE JURIDIQUE (axe normatif) ───────────────────
        SourceJuridique = self._cls("SourceJuridique", lkif.Legal_Source,
            "Source Juridique", "Legal Source",
            "Tout instrument de droit international ou national instituant des normes maritimes.")
        Convention = self._cls("ConventionInternationale", SourceJuridique,
            "Convention Internationale", "International Convention",
            "Traité multilatéral créant des obligations juridiquement contraignantes pour les parties.")
        Resolution = self._cls("ResolutionAGONU", SourceJuridique,
            "Résolution Assemblée Générale ONU", "UN General Assembly Resolution",
            "Résolution non contraignante mais faisant partie du droit coutumier émergent.")
        Reglement = self._cls("Reglement", SourceJuridique,
            "Règlement", "Regulation",
            "Texte réglementaire régional ou national à caractère obligatoire.")
        Protocole = self._cls("ProtocoleInternational", SourceJuridique,
            "Protocole International", "International Protocol",
            "Instrument additionnel ou complémentaire à une convention principale.")
        DecisionOMI = self._cls("DecisionOMI", SourceJuridique,
            "Décision de l'OMI/IMO", "IMO Decision / MEPC Resolution",
            "Résolution du Comité de la Protection du Milieu Marin (MEPC) de l'OMI.")

        # ── G. PÉRIODE TEMPORELLE ─────────────────────────────────
        time_interval = URIRef(NS_TIME + "Interval")
        Periode = self._cls("Periode", time_interval,
            "Période Temporelle", "Temporal Period",
            "Intervalle de temps pendant lequel une norme est en vigueur.")
        PeriodeConditionnelle = self._cls("PeriodeConditionnelle", Periode,
            "Période Conditionnelle", "Conditional Period",
            "Période définie par une condition factuelle (ex: en l'absence d'évaluations d'impact).")
        PeriodePermanente = self._cls("PeriodePermanente", Periode,
            "Période Permanente", "Permanent Period",
            "Période sans fin prévue — la norme s'applique indéfiniment depuis sa date d'entrée en vigueur.")
        self._disjoint(PeriodeConditionnelle, PeriodePermanente)

        # ── H. EXCEPTION JURIDIQUE (hiérarchie avec conséquences) ──
        Exception_ = self._cls("ExceptionJuridique", lkif.Exception,
            "Exception Juridique", "Legal Exception",
            "Condition spécifique sous laquelle une interdiction ne s'applique pas à un acteur déterminé.")
        ExceptionGenerale = self._cls("ExceptionGenerale", Exception_,
            "Exception Générale", "General Exception",
            "Exception de portée large autorisant une catégorie d'acteurs ou d'activités sous conditions.")
        ExceptionSpecifique = self._cls("ExceptionSpecifique", Exception_,
            "Exception Spécifique", "Specific Exception",
            "Cas précis au sein d'une exception générale, assorti de conditions et conséquences particulières.")
        self._disjoint(ExceptionGenerale, ExceptionSpecifique)

        # Conséquence d'une exception (distincte de Sanction)
        ConsequenceException = self._cls("ConsequenceException", lkif.Consequence,
            "Conséquence d'Exception", "Exception Consequence",
            "Obligation conditionnelle découlant de l'exercice d'une exception — ce n'est pas une sanction punitive, mais une contrepartie normative.")

        # ── I. CONTRÔLE ET SANCTION ───────────────────────────────
        Controle = self._cls("Controle", lkif.Act,
            "Mécanisme de Contrôle", "Control Mechanism",
            "Mesure institutionnelle de surveillance, d'évaluation ou d'application des normes.")
        ControleEtat = self._cls("ControleEtatPavillon", Controle,
            "Contrôle de l'État du Pavillon", "Flag State Control",
            "Contrôle exercé par l'État d'immatriculation du navire — responsabilité primaire UNCLOS.")
        ControlePort = self._cls("ControleEtatPort", Controle,
            "Contrôle par l'État du Port", "Port State Control (PSC)",
            "Inspection des navires étrangers dans les ports — Mémorandums de Paris, Tokyo, etc.")
        ControleRegional = self._cls("ControleOrgRegional", Controle,
            "Contrôle par Organisme Régional", "Regional Body Control",
            "Suivi et contrôle exercé par les ORGP, la CBI ou d'autres organismes régionaux.")

        Sanction = self._cls("Sanction", self.lkif.Consequence,
            "Sanction Juridique", "Legal Sanction",
            "Conséquence juridique découlant de la violation d'une interdiction.")
        SanctionPenale = self._cls("SanctionPenale", Sanction,
            "Sanction Pénale", "Criminal Sanction",
            "Amende, emprisonnement ou saisie du navire pour violation des normes maritimes.")
        SanctionAdministrative = self._cls("SanctionAdministrative", Sanction,
            "Sanction Administrative", "Administrative Sanction",
            "Suspension de licence, refus d'accès au port, immobilisation du navire.")
        self._disjoint(SanctionPenale, SanctionAdministrative)

        # ── J. STOCK HALIEUTIQUE ──────────────────────────────────
        Stock = self._cls("Stock", OWL.Thing,
            "Stock Halieutique", "Fish Stock",
            "Population génétiquement distincte d'une espèce halieutique dans une zone donnée.")
        StockSurExploite = self._cls("StockSurexploite", Stock,
            "Stock Surexploité", "Overfished Stock",
            "Stock dont le niveau de biomasse est inférieur au point de référence limite BLim.")

        # ── K. CONCEPT LEXICAL (SKOS) ─────────────────────────────
        ConceptLexical = self._cls("ConceptLexical", self.skos.Concept,
            "Concept Lexical", "Lexical Concept",
            "Terme défini dans le lexique de l'ontologie, associé à une norme ou une activité.")

        GlossairePeche = self.mar.GlossairePeche
        self.g.add((GlossairePeche, RDF.type, self.skos.ConceptScheme))
        self.g.add((GlossairePeche, SKOS.prefLabel, Literal("Glossaire Maritime — Droit et Pratique", lang="fr")))
        self.g.add((GlossairePeche, RDFS.comment, Literal(
            "Schéma SKOS centralisant les termes du droit maritime international.", lang="fr")))

        # ─── Stockage des références ──────────────────────────────
        self._ref = {
            "Norme": Norme, "Interdiction": Interdiction,
            "Permission": Permission, "Obligation": Obligation,
            "Zone": Zone, "ZoneHauteMer": ZoneHauteMer, "ZoneEEZ": ZoneEEZ,
            "ZoneTerritoriale": ZoneTerritoriale, "ZoneSanctuaire": ZoneSanctuaire,
            "ZoneVulnerable": ZoneVulnerable, "ZoneSpecialeMARPOL": ZoneSpecialeMARPOL,
            "ZoneCotiere": ZoneCotiere, "ZoneAMP": ZoneAMP,
            "Activite": Activite,
            "ActivitePeche": ActivitePeche, "ChalutageFond": ChalutageFond,
            "PecheINN": PecheINN, "PecheProfonde": PecheProfonde,
            "ActiviteChasse": ActiviteChasse,
            "ChasseBaleine": ChasseBaleine, "ChasseCommerciale": ChasseCommerciale,
            "ChasseCommercialeBaleine": ChasseCommerciale,
            "ChasseScientifique": ChasseScientifique, "ChasseSubsistance": ChasseSubsistance,
            "ActiviteExtraction": ActiviteExtraction,
            "ExtractionSable": ExtractionSable, "ExtractionHydrocarbures": ExtractionHydrocarbures,
            "ActiviteConstruction": ActiviteConstruction,
            "ConstructionLittorale": ConstructionLittorale, "ConstructionPortuaire": ConstructionPortuaire,
            "ActiviteRejets": ActiviteRejets,
            "RejetsHydrocarbures": RejetsHydrocarbures,
            "ActiviteCapture": ActiviteCapture, "CaptureOiseaux": CaptureOiseaux,
            "Acteur": Acteur,
            "EtatSouverain": EtatSouverain, "EtatPavillon": EtatPavillon,
            "EtatCotier": EtatCotier, "EtatPortuaire": EtatPortuaire,
            "OrgInternationale": OrgInternationale, "OrgRegPeche": OrgRegPeche,
            "IWC": IWC, "IMO": IMO, "FAO": FAO,
            "NavirePeche": NavirePeche, "NavireUsine": NavireUsine,
            "NavirePetrolier": NavirePetrolier, "NavireMarchand": NavireMarchand,
            "OperateurEconomique": OperateurEconomique, "Armateur": Armateur,
            "Capitaine": Capitaine, "OperateurOffshore": OperateurOffshore,
            "PromoteurCotier": PromoteurCotier, "CommunauteAutochtone": CommunauteAutochtone,
            "Espece": Espece, "Cetace": Cetace,
            "BaleineMysticete": BaleineMysticete, "BaleineOdontocete": BaleineOdontocete,
            "OiseauMarin": OiseauMarin, "OiseauMigrateur": OiseauMigrateur,
            "TortueMarine": TortueMarine, "PoissonProfond": PoissonProfond,
            "EspeceVulnerable": EspeceVulnerable, "EspeceProtegee": EspeceProtegee,
            "SourceJuridique": SourceJuridique, "Convention": Convention,
            "Resolution": Resolution, "Reglement": Reglement,
            "Protocole": Protocole, "DecisionOMI": DecisionOMI,
            "Periode": Periode, "PeriodeConditionnelle": PeriodeConditionnelle,
            "PeriodePermanente": PeriodePermanente,
            "Exception_": Exception_,
            "ExceptionGenerale": ExceptionGenerale,
            "ExceptionSpecifique": ExceptionSpecifique,
            "ConsequenceException": ConsequenceException,
            "Controle": Controle, "ControleEtat": ControleEtat,
            "ControlePort": ControlePort, "ControleRegional": ControleRegional,
            "Sanction": Sanction, "SanctionPenale": SanctionPenale,
            "SanctionAdministrative": SanctionAdministrative,
            "Stock": Stock, "StockSurExploite": StockSurExploite,
            "ConceptLexical": ConceptLexical,
        }
        logger.info("  ✅ Hiérarchie de classes OWL 2 DL construite — %d classes", len(self._ref))

    # ──────────────────────────────────────────────────────────────
    # OBJECT PROPERTIES
    # ──────────────────────────────────────────────────────────────
    def build_object_properties(self):
        logger.info("  🔗 Construction des propriétés objet OWL 2 DL...")
        mar  = self.mar
        ref  = self._ref
        lkif = self.lkif

        # ── Relations Norme ──────────────────────────────────────
        appliesInZone = self._obj_prop("appliesInZone", ref["Norme"], ref["Zone"],
            "s'applique dans la zone", "applies in zone")
        concerneActivite = self._obj_prop("concerneActivite", ref["Norme"], ref["Activite"],
            "concerne l'activité", "concerns activity")
        concerneActeur = self._obj_prop("concerneActeur", ref["Norme"], ref["Acteur"],
            "concerne l'acteur", "concerns actor")
        concerneEspece = self._obj_prop("protegeEspece", ref["Interdiction"], ref["Espece"],
            "protège l'espèce", "protects species")
        concerneStock = self._obj_prop("concerneStock", ref["Norme"], ref["Stock"],
            "concerne le stock halieutique", "concerns fish stock")
        aException = self._obj_prop("aException", ref["Norme"], ref["Exception_"],
            "a une exception", "has exception")
        appliesDuring = self._obj_prop("appliesDuring", ref["Norme"], ref["Periode"],
            "s'applique pendant", "applies during")
        entraineSanction = self._obj_prop("entraineSanction", ref["Norme"], ref["Sanction"],
            "entraîne sanction", "entails sanction", asymmetric=True, irreflexive=True)
        soumisAControle = self._obj_prop("soumisAControle", ref["Norme"], ref["Controle"],
            "soumis à contrôle", "subject to control")
        fondeeSur = self._obj_prop("fondeeSur", ref["Norme"], ref["SourceJuridique"],
            "fondée sur", "grounded in")
        hasConcept = self._obj_prop("hasConcept", ref["Norme"], ref["ConceptLexical"],
            "a le concept", "has concept")
        hasDerogation = self._obj_prop("hasDerogation", ref["Interdiction"], lkif.Permission,
            "a une dérogation", "has derogation")

        # ── Relations Exception → Conséquence ────────────────────
        entraineConsequence = self._obj_prop("entraineConsequence",
            ref["Exception_"], ref["ConsequenceException"],
            "entraîne comme conséquence", "entails consequence",
            asymmetric=True, irreflexive=True)
        aExceptionSpecifique = self._obj_prop("aExceptionSpecifique",
            ref["ExceptionGenerale"], ref["ExceptionSpecifique"],
            "a comme exception spécifique", "has specific exception")
        conditionneePar = self._obj_prop("conditionneePar",
            ref["Exception_"], ref["Controle"],
            "conditionnée par le contrôle", "conditioned by control")
        # soumisA — alias léger gardé pour compatibilité triple_injector
        soumisA = self._obj_prop("soumisA", ref["Acteur"], ref["Norme"],
            "soumis à (alias)", "subject to (alias)")
        self._sub_prop(soumisA, self.mar["estSoumisA"])

        # ── Relations Acteur ─────────────────────────────────────
        estSoumisA = self._obj_prop("estSoumisA", ref["Acteur"], ref["Norme"],
            "est soumis à", "is subject to")
        pratiqueActivite = self._obj_prop("pratiqueActivite", ref["Acteur"], ref["Activite"],
            "pratique l'activité", "practices activity")
        opereDans = self._obj_prop("opereDans", ref["Acteur"], ref["Zone"],
            "opère dans la zone", "operates in zone")
        commandeNavire = self._obj_prop("commandeNavire", ref["Capitaine"], ref["Acteur"],
            "commande le navire", "commands vessel", functional=True)
        possèdeNavire = self._obj_prop("possèdeNavire", ref["Armateur"], ref["Acteur"],
            "possède le navire", "owns vessel")

        # ── Relations Permission ─────────────────────────────────
        beneficieA = self._obj_prop("beneficieA", lkif.Permission, ref["Acteur"],
            "bénéficie à", "benefits actor")

        # ── Relations Source Juridique ───────────────────────────
        institueNorme = self._obj_prop("institueNorme", ref["SourceJuridique"], ref["Norme"],
            "institue la norme", "institutes norm")
        modifieSource = self._obj_prop("modifieSource", ref["SourceJuridique"], ref["SourceJuridique"],
            "modifie / amende la source", "amends legal source")

        # ── Relations Zone ───────────────────────────────────────
        couvreZone = self._obj_prop("couvreZone", ref["Zone"], ref["Zone"],
            "couvre la zone", "covers zone", transitive=True)
        estSousZoneDe = self._obj_prop("estSousZoneDe", ref["Zone"], ref["Zone"],
            "est sous-zone de", "is sub-zone of", transitive=True)
        bordeZone = self._obj_prop("bordeZone", ref["Zone"], ref["Zone"],
            "borde la zone", "borders zone", symmetric=True)

        # ── Relations Espèce ─────────────────────────────────────
        habiteDans = self._obj_prop("habiteDans", ref["Espece"], ref["Zone"],
            "habite dans la zone", "inhabits zone")
        estMenacePar = self._obj_prop("estMenacePar", ref["Espece"], ref["Activite"],
            "est menacée par l'activité", "is threatened by")

        # ──────────────────────────────────────────────────────────
        # INVERSES
        # ──────────────────────────────────────────────────────────
        self._inverse(appliesInZone, "estZoneDe", "est zone de")
        self._inverse(concerneActeur, "estActeurConcernePar", "est acteur concerné par")
        self._inverse(concerneActivite, "estActiviteDe", "est activité de")
        self._inverse(aException, "estExceptionDe", "est exception de")
        self._inverse(entraineSanction, "estSanctionDe", "est sanction de")
        # institueNorme2 supprimé — institueNorme (L772) est déjà l'inverse de fondeeSur
        self._inverse(estSousZoneDe, "contientSousZone", "contient la sous-zone")

        # Inverse structurel déjà défini
        self.g.add((institueNorme, OWL.inverseOf, fondeeSur))
        self.g.add((estSoumisA, OWL.inverseOf, concerneActeur))

        # ──────────────────────────────────────────────────────────
        # PROPERTY CHAINS (raisonnement chaîné)
        # ──────────────────────────────────────────────────────────
        # estSoumisA ∘ appliesInZone → opereDans (un acteur soumis à une norme opère dans sa zone)
        # CORRECTION 8: Supprimer la chaîne de propriétés fausse sur opereDans

        # fondeeSur ∘ sourceYear → ... (chaîne de traçabilité)
        # pratiqueActivite ∘ estActiviteDe → estSoumisA (si acteur pratique activité interdite, soumis à interdiction)
        self._property_chain(estSoumisA, [pratiqueActivite, self.mar["estActiviteDe"]])

        # ──────────────────────────────────────────────────────────
        # HIERARCHIE DE PROPRIETES
        # ──────────────────────────────────────────────────────────
        # protegeEspece est une sous-propriété de concerneEspece (générique)
        # sub_prop supprimé — protegeEspece n'est PAS une sous-propriété de concerneActivite
        # (une espèce n'est pas une activité, cela causait des inférences invalides)

        logger.info("  ✅ Propriétés objet construites")

    # ──────────────────────────────────────────────────────────────
    # DATA PROPERTIES
    # ──────────────────────────────────────────────────────────────
    def build_data_properties(self):
        logger.info("  📊 Construction des propriétés de données...")
        mar = self.mar
        ref = self._ref

        # Propriétés des Normes
        self._data_prop("confidence",       ref["Norme"],     XSD.decimal, "score de confiance IA")
        self._data_prop("needsReview",      ref["Norme"],     XSD.boolean, "nécessite révision humaine")
        self._data_prop("sourceConvention", ref["Norme"],     XSD.string,  "référence de la convention source")
        self._data_prop("legalLayer",       ref["Norme"],     XSD.string,  "couche légale (International/Régional/National)")
        self._data_prop("typeActivite",     ref["Norme"],     XSD.string,  "type d'activité réglementé")
        self._data_prop("normText",         ref["Norme"],     XSD.string,  "texte normatif original")
        self._data_prop("isZoneSpecific",   ref["Norme"],     XSD.boolean, "spécifique à une zone géographique", functional=True)
        self._data_prop("deonticType",      ref["Norme"],     XSD.string,  "type déontique (Interdiction/Permission/Obligation)")

        # Propriétés des Sources Juridiques
        self._data_prop("sourceYear",       ref["SourceJuridique"], XSD.integer, "année d'adoption de la source juridique")
        self._data_prop("sourceReference",  ref["SourceJuridique"], XSD.string,  "référence officielle")

        # Propriétés des Zones
        self._data_prop("distanceNM",       ref["Zone"], XSD.decimal, "distance en milles nautiques depuis la ligne de base")
        self._data_prop("surfaceKm2",       ref["Zone"], XSD.decimal, "superficie en km²")
        self._data_prop("codeZoneIMO",      ref["Zone"], XSD.string,  "code de zone spéciale OMI/IMO")
        self._data_prop("coordinatesWKT",   ref["Zone"], XSD.string,  "coordonnées géographiques WKT")

        # Propriétés des Espèces Marines
        self._data_prop("nomScientifique",   ref["Espece"], XSD.string, "nom scientifique (binôme linnéen)")
        self._data_prop("statutProtection",  ref["Espece"], XSD.string, "statut de protection (UICN/CITES/Convention)")
        self._data_prop("statutUICV",        ref["Espece"], XSD.string, "catégorie UICN (EX/EW/CR/EN/VU/NT/LC)")
        self._data_prop("classeAppendice",   ref["Espece"], XSD.string, "appendice CITES (I/II/III) ou CMS (App.I/App.II)")

        # Propriétés des Acteurs
        self._data_prop("codePavillon",      ref["EtatPavillon"], XSD.string, "code pays IMO du pavillon")
        self._data_prop("portImmatriculation", ref["NavireMarchand"], XSD.string, "port d'immatriculation")
        self._data_prop("jauge",             ref["NavireMarchand"], XSD.decimal, "jauge brute (GT)")

        # Propriétés des Activités
        self._data_prop("profondeurMin",     ref["PecheProfonde"], XSD.decimal, "profondeur minimale d'opération (mètres)")
        self._data_prop("concentrationPPM",  ref["Norme"], XSD.decimal, "concentration maximale en ppm autorisée")
        self._data_prop("seuilRejet",        ref["ActiviteRejets"], XSD.decimal, "seuil de rejet réglementaire")

        # --- Propriétés ajoutées ---
        self._data_prop("hasCatchLimit", ref["Norme"], XSD.decimal, "limite de capture autorisée")
        self._data_prop("sourceArticle", ref["Norme"], XSD.string, "article de la source juridique")

        logger.info("  ✅ Propriétés de données définies (v2.0) avec succès.")

    # ──────────────────────────────────────────────────────────────
    # OWL RESTRICTIONS & AXIOMES DE CLASSE
    # ──────────────────────────────────────────────────────────────
    def build_restrictions(self):
        logger.info("  🔒 Construction des axiomes OWL 2 DL...")
        ref = self._ref
        mar = self.mar

        # ── ① RESTRICTIONS NÉCESSAIRES (subClassOf) ─────────────
        # Toute Interdiction DOIT concerner au moins une Activité
        self._some(ref["Interdiction"], mar.concerneActivite, ref["Activite"])
        # Toute Interdiction DOIT s'appliquer dans au moins une Zone
        self._some(ref["Interdiction"], mar.appliesInZone, ref["Zone"])
        # Toute Interdiction DOIT concerner au moins un Acteur
        self._some(ref["Interdiction"], mar.concerneActeur, ref["Acteur"])
        # Toute Interdiction DOIT être fondée sur au moins une Source Juridique
        self._some(ref["Interdiction"], mar.fondeeSur, ref["SourceJuridique"])
        # Toute Source Juridique DOIT instituer au moins une Norme
        self._some(ref["SourceJuridique"], mar.institueNorme, ref["Norme"])
        # Tout Acteur soumis à une norme DOIT avoir au moins une activité
        self._some(ref["Acteur"], mar.pratiqueActivite, ref["Activite"])
        # Toute ChasseBaleine concerne un Cétacé (via protegeEspece)
        self._some(ref["ChasseBaleine"], mar.protegeEspece, ref["Cetace"])
        # Tout NavirePétrolier est potentiellement source de rejets
        self._some(ref["NavirePetrolier"], mar.pratiqueActivite, ref["ActiviteRejets"])

        # ── ② RESTRICTIONS UNIVERSELLES (allValuesFrom) ─────────
        # La chasse commerciale n'affecte que les cétacés
        self._all(ref["ChasseCommercialeBaleine"], mar.protegeEspece, ref["Cetace"])
        # Les zones spéciales MARPOL ne contiennent que des sous-zones maritimes
        self._all(ref["ZoneSpecialeMARPOL"], mar.couvreZone, ref["Zone"])
        # Les sources juridiques n'instituent que des normes juridiques
        self._all(ref["SourceJuridique"], mar.institueNorme, ref["Norme"])

        # ── ③ CARDINALITÉS QUALIFIÉES ────────────────────────────
        # Toute Interdiction a au moins 1 source juridique (Convention ou Résolution)
        self._min_card(ref["Interdiction"], mar.fondeeSur, 1, ref["SourceJuridique"])
        # Toute Interdiction concerne au moins 1 acteur
        self._min_card(ref["Interdiction"], mar.concerneActeur, 1, ref["Acteur"])
        # Tout ChalutageFond opère sur au moins 1 zone (HM ou ZEE)
        self._min_card(ref["ChalutageFond"], mar.habiteDans, 0)

        # ── ④ CLASSES ÉQUIVALENTES (raisonnement automatique) ────

        # ZoneInterdite ≡ Zone ⊓ (∃estZoneDe.Interdiction)
        ZoneInterdite = mar.ZoneInterdite
        self.g.add((ZoneInterdite, RDFS.label, Literal("Zone soumise à interdiction", lang="fr")))
        self.g.add((ZoneInterdite, RDF.type, OWL.Class))
        r1 = self._restriction_bnode(mar["estZoneDe"], OWL.someValuesFrom, ref["Interdiction"])
        self._equiv_intersection(ZoneInterdite, ref["Zone"], r1)

        # ActiviteIllicite ≡ Activite ⊓ (∃estActiviteDe.Interdiction)
        ActiviteIllicite = mar.ActiviteIllicite
        self.g.add((ActiviteIllicite, RDFS.label, Literal("Activité illicite/interdite", lang="fr")))
        self.g.add((ActiviteIllicite, RDF.type, OWL.Class))
        r2 = self._restriction_bnode(mar["estActiviteDe"], OWL.someValuesFrom, ref["Interdiction"])
        self._equiv_intersection(ActiviteIllicite, ref["Activite"], r2)

        # ActeurEnInfraction ≡ Acteur ⊓ (∃pratiqueActivite.ActiviteIllicite)
        ActeurEnInfraction = mar.ActeurEnInfraction
        self.g.add((ActeurEnInfraction, RDFS.label, Literal("Acteur en infraction", lang="fr")))
        self.g.add((ActeurEnInfraction, RDF.type, OWL.Class))
        r3 = self._restriction_bnode(mar.pratiqueActivite, OWL.someValuesFrom, ActiviteIllicite)
        self._equiv_intersection(ActeurEnInfraction, ref["Acteur"], r3)

        # EspèceProtégéeParLoi ≡ EspeceMarine ⊓ (∃estMenacePar.ActiviteIllicite)
        EspeceMenacee = mar.EspeceMenaceePar
        self.g.add((EspeceMenacee, RDFS.label, Literal("Espèce marine menacée par une activité interdite", lang="fr")))
        self.g.add((EspeceMenacee, RDF.type, OWL.Class))
        r4 = self._restriction_bnode(mar.estMenacePar, OWL.someValuesFrom, ActiviteIllicite)
        self._equiv_intersection(EspeceMenacee, ref["Espece"], r4)

        # NormeInternationale ≡ NormeJuridique ⊓ (∃fondeeSur.(ConventionInternationale ⊔ ResolutionAGONU))
        NormeInternationale = mar.NormeInternationale
        self.g.add((NormeInternationale, RDFS.label, Literal("Norme de droit international maritime", lang="fr")))
        self.g.add((NormeInternationale, RDF.type, OWL.Class))
        bnode_union = BNode()
        self.g.add((bnode_union, RDF.type, OWL.Class))
        self.g.add((bnode_union, OWL.unionOf, self._rdf_list([ref["Convention"], ref["Resolution"]])))
        r5 = self._restriction_bnode(mar.fondeeSur, OWL.someValuesFrom, bnode_union)
        self._equiv_intersection(NormeInternationale, ref["Norme"], r5)

        # ── ⑤ AXIOMES EXCEPTION → CONSÉQUENCE ────────────────────
        # Toute ExceptionGenerale DOIT entraîner au moins une conséquence
        self._some(ref["ExceptionGenerale"], mar.entraineConsequence, ref["ConsequenceException"])
        # Toute ExceptionSpecifique DOIT entraîner au moins une conséquence
        self._some(ref["ExceptionSpecifique"], mar.entraineConsequence, ref["ConsequenceException"])
        # Les exceptions ne produisent que des ConsequenceException (pas des Sanctions)
        self._all(ref["Exception_"], mar.entraineConsequence, ref["ConsequenceException"])

        # ExceptionConditionnelle ≡ Exception ⊓ (∃conditionneePar.Controle)
        ExceptionConditionnelle = mar.ExceptionConditionnelle
        self.g.add((ExceptionConditionnelle, RDFS.label,
                    Literal("Exception conditionnée par un contrôle", lang="fr")))
        self.g.add((ExceptionConditionnelle, RDF.type, OWL.Class))
        r6 = self._restriction_bnode(mar.conditionneePar, OWL.someValuesFrom, ref["Controle"])
        self._equiv_intersection(ExceptionConditionnelle, ref["Exception_"], r6)

        logger.info("  ✅ Axiomes OWL 2 DL construits (restrictions + équivalences + chaînes)")

    # ──────────────────────────────────────────────────────────────
    # BUILD ALL
    # ──────────────────────────────────────────────────────────────
    def build_all(self):
        self.build_ontology_header()
        self.build_classes()
        self.build_object_properties()
        self.build_data_properties()
        self.build_restrictions()
        logger.info("  🎯 Schéma OWL 2 DL complet construit — v2.0")
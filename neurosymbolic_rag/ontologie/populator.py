"""
populator.py v2 — Population OWL complète des 6 interdictions maritimes.

Responsabilités :
  - Zones statiques UNCLOS + MARPOL + CMS
  - Sources juridiques avec enrichissement SKOS
  - Individus pour I001 à I006 (complets, tous triplets)
  - Espèces marines (baleines, oiseaux marins, tortues)
  - Acteurs institutionnels (IWC, IMO, FAO, ORGP, etc.)
  - Couche lexicale SKOS (glossaire)
  - Contrôles et sanctions associés
  - Périodes temporelles
  - Exceptions et permissions
"""

import logging
import re
import unicodedata
from typing import Any, Dict, List, Optional

from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD, BNode
from rdflib.namespace import SKOS

logger = logging.getLogger(__name__)

NS_MAR  = "http://www.maritime-ontology.org/mar#"
NS_LKIF = "http://www.estrellaproject.org/lkif-core/lkif-core.owl#"
NS_TIME = "http://www.w3.org/2006/time#"


def slugify(value: str) -> str:
    clean = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    clean = re.sub(r"[^A-Za-z0-9]+", "_", clean).strip("_")
    return clean or "Unknown"


class OntologyPopulator:
    """Peuple le graphe RDF avec les 6 interdictions maritimes complètes."""

    def __init__(self, g: Graph, mar: Namespace, lkif: Namespace, skos: Any):
        self.g    = g
        self.mar  = mar
        self.lkif = lkif
        self.skos = skos
        self._seen = set()

    def _exists(self, uri: URIRef) -> bool:
        return (uri, RDF.type, OWL.NamedIndividual) in self.g

    def _ind(self, local: str, class_uri: URIRef, label_fr: str,
             label_en: str = "", comment: str = "",
             definition: str = "", skos_label: bool = False) -> URIRef:
        uri = self.mar[local]
        if not self._exists(uri):
            self.g.add((uri, RDF.type, class_uri))
            self.g.add((uri, RDF.type, OWL.NamedIndividual))
            self.g.add((uri, RDFS.label, Literal(label_fr, lang="fr")))
            if label_en:
                self.g.add((uri, RDFS.label, Literal(label_en, lang="en")))
            if comment:
                self.g.add((uri, RDFS.comment, Literal(comment, lang="fr")))
            if definition:
                self.g.add((uri, self.skos.definition, Literal(definition, lang="fr")))
            if skos_label:
                self.g.add((uri, self.skos.prefLabel, Literal(label_fr, lang="fr")))
                if label_en:
                    self.g.add((uri, self.skos.prefLabel, Literal(label_en, lang="en")))
        return uri

    def _link(self, s: URIRef, p: URIRef, o: URIRef):
        self.g.add((s, p, o))

    def _data(self, s: URIRef, p: URIRef, val: Any, datatype=XSD.string):
        if val is not None:
            self.g.add((s, p, Literal(val, datatype=datatype)))

    # ══════════════════════════════════════════════════════════════
    # 1. ZONES
    # ══════════════════════════════════════════════════════════════
    def populate_zones(self):
        logger.info("  🌍 Population des zones maritimes...")
        mar = self.mar

        # Zones UNCLOS
        HM = self._ind("HM", mar.ZoneHauteMer, "Haute Mer", "High Seas",
            "Zone au-delà des juridictions nationales — UNCLOS Art. 86.")
        self._data(HM, mar.surfaceKm2, 230000000.0, XSD.decimal)

        EEZ = self._ind("EEZ", mar.ZoneEconomiqueExclusive,
            "Zone Économique Exclusive", "Exclusive Economic Zone",
            "Zone de 200 milles marins — UNCLOS Art. 55-75.")
        self._data(EEZ, mar.distanceNM, 200.0, XSD.decimal)

        MT = self._ind("MT", mar.ZoneMerTerritoriale, "Mer Territoriale", "Territorial Sea",
            "Zone de 12 milles marins — UNCLOS Art. 3.")
        self._data(MT, mar.distanceNM, 12.0, XSD.decimal)

        ZC = self._ind("ZC", mar.ZoneContigüe, "Zone Contiguë", "Contiguous Zone",
            "Zone de 24 milles marins — UNCLOS Art. 33.")
        self._data(ZC, mar.distanceNM, 24.0, XSD.decimal)

        PC = self._ind("PC", mar.PlateauContinental, "Plateau Continental", "Continental Shelf",
            "Prolongement naturel du territoire — UNCLOS Art. 76.")

        # Relations zone hierarchy
        self._link(MT,  mar.estSousZoneDe, EEZ)

        # Zones de protection baleines (IWC)
        SanctuaireAustral = self._ind("SanctuaireOceanAustral", mar.ZoneSanctuaireMarin,
            "Sanctuaire de l'Océan Austral", "Southern Ocean Sanctuary",
            "Sanctuaire baleinier de l'Océan Austral (IWC, 1994) — interdiction totale de chasse commerciale.")
        SanctuaireIndien = self._ind("SanctuaireOceanIndien", mar.ZoneSanctuaireMarin,
            "Sanctuaire de l'Océan Indien", "Indian Ocean Sanctuary",
            "Sanctuaire baleinier de l'Océan Indien (IWC, 1979).")
        HemisphereSud = self._ind("HemisphereSudBaleines", mar.ZoneSanctuaireMarin,
            "Hémisphère Sud — Zone de protection des baleines", "Southern Hemisphere Whale Sanctuary",
            "Zone couvrant l'hémisphère sud pour la protection des cétacés (IWC Schedule).")

        # Zones vulnérables (chalutage fond)
        ZEV = self._ind("ZEV", mar.ZoneEcosystemeVulnerable,
            "Écosystème Marin Vulnérable", "Vulnerable Marine Ecosystem",
            "Zone abritant monts sous-marins, coraux froids, éponges — critères FAO 2009.")

        # Zones spéciales MARPOL
        ZoneMed = self._ind("Zone_MARPOL_Mediterranee", mar.ZoneSpecialeMARPOL,
            "Mer Méditerranée — Zone Spéciale MARPOL", "Mediterranean Sea Special Area",
            "Zone spéciale MARPOL Annexe I — interdiction totale des rejets d'hydrocarbures.")
        self._data(ZoneMed, mar.codeZoneIMO, "MED", XSD.string)

        ZoneBaltique = self._ind("Zone_MARPOL_Baltique", mar.ZoneSpecialeMARPOL,
            "Mer Baltique — Zone Spéciale MARPOL", "Baltic Sea Special Area",
            "Zone spéciale MARPOL Annexe I et Annexe IV — protection maximale.")
        self._data(ZoneBaltique, mar.codeZoneIMO, "BALT", XSD.string)

        ZoneNoire = self._ind("Zone_MARPOL_MerNoire", mar.ZoneSpecialeMARPOL,
            "Mer Noire — Zone Spéciale MARPOL", "Black Sea Special Area")
        ZoneRouge = self._ind("Zone_MARPOL_MerRouge", mar.ZoneSpecialeMARPOL,
            "Mer Rouge — Zone Spéciale MARPOL", "Red Sea Special Area")
        ZoneGolfe = self._ind("Zone_MARPOL_Golfe", mar.ZoneSpecialeMARPOL,
            "Golfe Persique — Zone Spéciale MARPOL", "Gulf Area Special Area")
        ZoneAntarctique = self._ind("Zone_MARPOL_Antarctique", mar.ZoneSpecialeMARPOL,
            "Antarctique — Zone Spéciale MARPOL", "Antarctic Area Special Area",
            "Zone MARPOL Annexe I — interdiction absolue de tout rejet d'hydrocarbures.")

        # Zone côtière
        ZoneCote = self._ind("ZoneCotiere_Generale", mar.ZoneCotiere,
            "Zone Côtière Littorale", "Coastal Zone",
            "Interface terre-mer soumise aux réglementations nationales (Loi Littoral, GIZC).")

        # Stocker les références pour les interdictions
        self._zones = {
            "HM": HM, "EEZ": EEZ, "MT": MT, "ZC": ZC, "PC": PC,
            "ZEV": ZEV,
            "SanctuaireAustral": SanctuaireAustral,
            "SanctuaireIndien": SanctuaireIndien,
            "HemisphereSud": HemisphereSud,
            "ZoneMed": ZoneMed, "ZoneBaltique": ZoneBaltique,
            "ZoneNoire": ZoneNoire, "ZoneRouge": ZoneRouge,
            "ZoneGolfe": ZoneGolfe, "ZoneAntarctique": ZoneAntarctique,
            "ZoneCote": ZoneCote,
        }
        logger.info("    ✅ %d zones créées", len(self._zones))

    # ══════════════════════════════════════════════════════════════
    # 2. ACTEURS
    # ══════════════════════════════════════════════════════════════
    def populate_acteurs(self):
        logger.info("  👥 Population des acteurs...")
        mar = self.mar

        # Organisations internationales
        IWC_org = self._ind("Acteur_IWC", mar.CommissionBaleiniereInternationale,
            "Commission Baleinière Internationale (CBI)", "International Whaling Commission",
            "Organe créé par l'ICRW 1946, compétent pour la conservation des cétacés.")
        IMO_org = self._ind("Acteur_IMO", mar.OrganisationMaritimeInternationale,
            "Organisation Maritime Internationale (OMI)", "International Maritime Organization",
            "Agence spécialisée ONU pour la sécurité maritime et la prévention de la pollution.")
        FAO_org = self._ind("Acteur_FAO", mar.OrganisationFAO,
            "FAO — Organisation des Nations Unies pour l'alimentation et l'agriculture",
            "FAO",
            "Organe coordinateur des pêches mondiales, auteur des Directives internationales pour la gestion des pêches profondes.")
        ORGP = self._ind("Acteur_OrgRegionalPeche", mar.OrganismeRegionalGestionPeche,
            "Organismes régionaux de gestion des pêches (ORGP)", "Regional Fisheries Management Organisations")

        # États
        Etats = self._ind("Acteur_Etats", mar.EtatSouverain, "États membres", "Member States")
        EtatPav = self._ind("Acteur_EtatPavillon", mar.EtatPavillon, "États du Pavillon", "Flag States")
        EtatCot = self._ind("Acteur_EtatCotier", mar.EtatCotier, "États Côtiers", "Coastal States")
        EtatPort = self._ind("Acteur_EtatPort", mar.EtatPortuaire, "États du Port", "Port States")
        MembreIWC = self._ind("Acteur_MembreIWC", mar.EtatSouverain,
            "États membres de la Commission Baleinière Internationale", "IWC Member States")

        # Navires et opérateurs
        NavUsine = self._ind("Acteur_NavireUsine", mar.NavireUsine,
            "Navires-usines (factory ships)", "Factory Ships")
        BateauChasseur = self._ind("Acteur_BateauChasseur", mar.NavirePeche,
            "Bateaux chasseurs de baleines", "Catcher Vessels")
        StationTerrestre = self._ind("Acteur_StationTerrestre", mar.OperateurEconomique,
            "Stations terrestres de traitement", "Land-Based Processing Stations")
        NavPetrolier = self._ind("Acteur_NavirePetrolier", mar.NavirePetrolier,
            "Navires pétroliers (tankers)", "Oil Tankers")
        Armateurs = self._ind("Acteur_Armateur", mar.Armateur,
            "Armateurs et exploitants de navires", "Shipowners and Operators")
        Capitaines = self._ind("Acteur_Capitaine", mar.Capitaine,
            "Capitaines de navires", "Ship Masters")
        OperOffshore = self._ind("Acteur_OperateurOffshore", mar.OperateurOffshore,
            "Opérateurs pétroliers offshore", "Offshore Oil Operators")
        Promoteurs = self._ind("Acteur_PromoteurCotier", mar.PromoteurCotier,
            "Promoteurs et constructeurs côtiers", "Coastal Developers")
        Autochtones = self._ind("Acteur_CommunauteAutochtone", mar.CommunauteAutochtone,
            "Communautés autochtones (chasse traditionnelle)", "Indigenous Peoples (traditional whaling)")

        self._acteurs = {
            "IWC": IWC_org, "IMO": IMO_org, "FAO": FAO_org, "ORGP": ORGP,
            "Etats": Etats, "EtatPavillon": EtatPav, "EtatCotier": EtatCot,
            "EtatPortuaire": EtatPort, "MembreIWC": MembreIWC,
            "NavireUsine": NavUsine, "BateauChasseur": BateauChasseur,
            "StationTerrestre": StationTerrestre, "NavirePetrolier": NavPetrolier,
            "Armateur": Armateurs, "Capitaine": Capitaines,
            "OperateurOffshore": OperOffshore, "Promoteur": Promoteurs,
            "CommunauteAutochtone": Autochtones,
        }
        logger.info("    ✅ %d acteurs créés", len(self._acteurs))

    # ══════════════════════════════════════════════════════════════
    # 3. SOURCES JURIDIQUES
    # ══════════════════════════════════════════════════════════════
    def populate_sources_juridiques(self):
        logger.info("  📚 Population des sources juridiques...")
        mar = self.mar
        skos = self.skos

        def src(local, cls, label, year, fr_def, en_def=""):
            uri = self._ind(local, cls, label)
            self._data(uri, mar.sourceYear, year, XSD.integer)
            self.g.add((uri, skos.definition, Literal(fr_def, lang="fr")))
            if en_def:
                self.g.add((uri, skos.definition, Literal(en_def, lang="en")))
            return uri

        # I001 — Chalutage de fond
        Res61 = src("Res61_105", mar.ResolutionAGONU,
            "A/RES/61/105 — Pêches durables (2006)", 2006,
            "Résolution 61/105 de l'AGNU sur les pêches durables en haute mer, demandant l'évaluation préalable d'impact des EMV.",
            "UNGA Resolution 61/105 on sustainable fisheries, requiring prior impact assessments on VMEs (2006).")
        Res64 = src("Res64_72", mar.ResolutionAGONU,
            "A/RES/64/72 — Océans et droit de la mer (2009)", 2009,
            "Résolution 64/72 de l'AGNU renforçant les mesures de protection des EMV en haute mer.",
            "UNGA Resolution 64/72 on oceans and law of the sea, strengthening VME protections (2009).")
        Res66 = src("Res66_68", mar.ResolutionAGONU,
            "A/RES/66/68 — Océans et droit de la mer (2011)", 2011,
            "Résolution 66/68 de l'AGNU sur les pêches profondes durables en haute mer.",
            "UNGA Resolution 66/68 on sustainable deep-sea fisheries on the high seas (2011).")
        Res71 = src("Res71_123", mar.ResolutionAGONU,
            "A/RES/71/123 — Océans et droit de la mer (2016)", 2016,
            "Résolution 71/123 de l'AGNU réaffirmant les obligations de protection des EMV.",
            "UNGA Resolution 71/123 reaffirming VME protection obligations (2016).")
        DirectivesFAO = src("DirectivesFAO_PechesProfonde", mar.SourceJuridique,
            "Directives internationales FAO pour la gestion des pêches en eaux profondes (2008)", 2008,
            "Directives techniques non contraignantes de la FAO fournissant un cadre pour la gestion des pêches en eaux profondes.")

        # I002 — Chasse Baleine
        ICRW = src("ICRW_Convention", mar.ConventionInternationale,
            "ICRW — Convention internationale pour la réglementation de la chasse à la baleine (1946)", 1946,
            "Convention fondatrice du régime international de gestion des cétacés, instituant la Commission Baleinière Internationale.",
            "International Convention for the Regulation of Whaling (1946) — founding instrument of the IWC.")
        IWC_Sched = src("IWC_Schedule", mar.SourceJuridique,
            "IWC Schedule — Annexe ICRW amendée (1982, mis à jour 2024)", 1946,
            "Annexe de la ICRW contenant le moratoire commercial (para. 10(e), adopté 1982, en vigueur 1986) et les quotas de subsistance autochtone.",
            "Schedule to the ICRW containing the commercial whaling moratorium (para. 10(e), adopted 1982) and ASW quotas.")

        # I003 — Construction littorale
        LoiLittoral = src("LoiLittoral_1986", mar.SourceJuridique,
            "Loi Littoral n°86-2 du 3 janvier 1986 (France)", 1986,
            "Loi française relative à l'aménagement, la protection et la mise en valeur du littoral — codifiée aux art. L.121-1 s. du Code de l'urbanisme.",
            "French Coastal Law (Loi Littoral) on coastal zone management and protection (1986).")
        ProtoGIZC = src("Protocole_GIZC_Mediterranee_2008", mar.ProtocoleInternational,
            "Protocole GIZC de la Méditerranée (2008)", 2008,
            "Protocole relatif à la Gestion Intégrée des Zones Côtières de la Méditerranée, entré en vigueur le 24 mars 2011.",
            "Protocol on Integrated Coastal Zone Management in the Mediterranean (2008), in force 24 March 2011.")
        UNCLOS_Conv = src("UNCLOS_1982", mar.ConventionInternationale,
            "UNCLOS — Convention des Nations Unies sur le droit de la mer (1982)", 1982,
            "Montego Bay Convention — cadre juridique fondamental pour tous les espaces maritimes.",
            "UN Convention on the Law of the Sea — the constitutional framework for maritime law.")

        # I004 — Extraction sable
        CDB_Conv = src("Convention_CBD", mar.ConventionInternationale,
            "Convention sur la Diversité Biologique (Rio, 1992)", 1992,
            "Convention internationale sur la diversité biologique — Articles 7(c), 8, 10, 14 encadrant les activités nuisibles à la biodiversité marine.",
            "Convention on Biological Diversity (Rio 1992) — Articles 7(c), 8, 10, 14 on harmful marine activities.")

        # I005 — Oiseaux marins
        CMS_Conv = src("CMS_Convention", mar.ConventionInternationale,
            "Convention CMS / Convention de Bonn (1979)", 1979,
            "Convention sur la Conservation des Espèces Migratrices appartenant à la Faune Sauvage — Articles III et IV pour les oiseaux marins.",
            "Convention on the Conservation of Migratory Species of Wild Animals (Bonn Convention, 1979).")
        ACAP_Accord = src("ACAP_2004", mar.ProtocoleInternational,
            "ACAP — Accord sur la Conservation des Albatros et des Pétrels (2004)", 2004,
            "Accord spécialisé sous l'égide de la CMS pour la conservation des albatros, pétrels et procellariidés.",
            "Agreement on the Conservation of Albatrosses and Petrels (2004), under CMS.")

        # I006 — Rejet hydrocarbures
        MARPOL = src("MARPOL_73_78", mar.ConventionInternationale,
            "Convention MARPOL 73/78 — Prévention de la pollution par les navires", 1978,
            "Convention internationale pour la prévention de la pollution par les navires — Annexe I sur les hydrocarbures (rév. 2007).",
            "MARPOL 73/78 — International Convention for the Prevention of Pollution from Ships — Annex I on oil (rev. 2007).")
        MEPC117 = src("DecisionMEPC_117_52", mar.DecisionOMI,
            "Résolution MEPC.117(52) — Amendements MARPOL Annexe I (2004, app. 2007)", 2004,
            "Révision de l'Annexe I de MARPOL (MEPC.117(52)) renforçant les limites de rejet et les zones spéciales.",
            "MEPC Resolution 117(52) revising MARPOL Annex I, tightening discharge limits (applicable 2007).")
        self._link(MEPC117, mar.modifieSource, MARPOL)
        UEMOA_Regl = src("Reglement_UEMOA_Hydrocarbures", mar.Reglement,
            "Règlement N°06/2022/CM/UEMOA — Normes environnementales offshore (2022)", 2022,
            "Règlement UEMOA relatif aux normes environnementales applicables aux opérations pétrolières et gazières offshore — adopté 30 septembre 2022.",
            "UEMOA Regulation N°06/2022 on environmental standards for offshore oil and gas operations (30 Sept. 2022).")

        self._sources = {
            "Res61": Res61, "Res64": Res64, "Res66": Res66, "Res71": Res71,
            "FAO_Directives": DirectivesFAO,
            "ICRW": ICRW, "IWC_Schedule": IWC_Sched,
            "LoiLittoral": LoiLittoral, "ProtoGIZC": ProtoGIZC, "UNCLOS": UNCLOS_Conv,
            "CBD": CDB_Conv,
            "CMS": CMS_Conv, "ACAP": ACAP_Accord,
            "MARPOL": MARPOL, "MEPC117": MEPC117, "UEMOA": UEMOA_Regl,
        }
        logger.info("    ✅ %d sources juridiques créées", len(self._sources))

    # ══════════════════════════════════════════════════════════════
    # 4. ESPÈCES
    # ══════════════════════════════════════════════════════════════
    def populate_species(self):
        logger.info("  🐋 Population des espèces marines...")
        mar = self.mar

        def whale(local, label_fr, label_en, nom_sci, statut="Totale", skos_def=""):
            uri = self._ind(local, mar.EspeceMarine, label_fr, label_en,
                skos_label=True)
            self.g.add((uri, RDF.type, mar.Cetace))
            self._data(uri, mar.nomScientifique, nom_sci, XSD.string)
            self._data(uri, mar.statutProtection, statut, XSD.string)
            if skos_def:
                self.g.add((uri, self.skos.definition, Literal(skos_def, lang="en")))
            # ConceptLexical supprimé — les espèces sont des individus biologiques,
            # pas des concepts lexicaux (glossaire). Les ConceptWhaling_* séparés gèrent cela.
            self.g.add((uri, self.skos.inScheme, mar.GlossairePeche))
            return uri

        def bird(local, label_fr, label_en, nom_sci, statut="Totale"):
            uri = self._ind(local, mar.OiseauMarin, label_fr, label_en, skos_label=True)
            self._data(uri, mar.nomScientifique, nom_sci, XSD.string)
            self._data(uri, mar.statutProtection, statut, XSD.string)
            self.g.add((uri, self.skos.inScheme, mar.GlossairePeche))
            return uri

        def turtle(local, label_fr, label_en, nom_sci, statut="Totale"):
            uri = self._ind(local, mar.TortueMarine, label_fr, label_en, skos_label=True)
            self._data(uri, mar.nomScientifique, nom_sci, XSD.string)
            self._data(uri, mar.statutProtection, statut, XSD.string)
            return uri

        # Baleines mysticètes (à fanons)
        BalFranche      = whale("Espece_BaleineFranche",    "Baleine franche",          "Right whale",         "Eubalaena glacialis / E. australis")
        BalBoreal       = whale("Espece_BaleineBoreal",     "Baleine boréale",          "Bowhead whale",       "Balaena mysticetus",
            skos_def="any whale known as bowhead whale, Arctic whale, Greenland right whale, or great polar whale.")
        BalGrise        = whale("Espece_BaleineGrise",      "Baleine grise",            "Gray whale",          "Eschrichtius robustus")
        BalBleue        = whale("Espece_BaleineBleue",      "Baleine bleue",            "Blue whale",          "Balaenoptera musculus")
        BalFin          = whale("Espece_BaleineFin",        "Baleine à nageoires",      "Fin whale",           "Balaenoptera physalus")
        BalBosse        = whale("Espece_BaleineBosse",      "Baleine à bosse",          "Humpback whale",      "Megaptera novaeangliae")
        BalSei          = whale("Espece_BaleineSei",        "Baleine sei",              "Sei whale",           "Balaenoptera borealis")
        BalBreyde       = whale("Espece_BaleineDeBryde",    "Baleine de Bryde",         "Bryde's whale",       "Balaenoptera edeni / B. brydei")
        BalMinke        = whale("Espece_BaleineMinke",      "Baleine de Minke",         "Minke whale",         "Balaenoptera acutorostrata / B. bonaerensis",
            "Totale (exception : chasse limitée)",
            skos_def="any whale known as lesser rorqual, little piked whale, minke whale, or sharp-headed finner.")
        PetBalFranche   = whale("Espece_PetiteBaleineFranche", "Petite baleine franche", "Pygmy right whale",  "Caperea marginata")

        # Baleines odontocètes (à dents)
        Cachalot        = whale("Espece_Cachalot",          "Cachalot",                 "Sperm whale",         "Physeter macrocephalus")
        Orque           = whale("Espece_Orque",             "Orque",                    "Killer whale",        "Orcinus orca")
        Globicephale    = whale("Espece_Globicephale",      "Globicéphale",             "Pilot whale",         "Globicephala melaena / G. macrorhynchus")
        BalABec         = whale("Espece_BaleineABec",       "Baleine à bec",            "Beaked whale",        "Mesoplodon spp. / Ziphius cavirostris")
        BalABecBotNose  = whale("Espece_BaleineABecBottlenose", "Baleine à bec d'Arnoux", "Bottlenose whale",  "Hyperoodon ampullatus / Berardius arnuxii")

        # Sous-classement mysticète / odontocète
        for sp in [BalFranche, BalBoreal, BalGrise, BalBleue, BalFin, BalBosse, BalSei, BalBreyde, BalMinke, PetBalFranche]:
            self.g.add((sp, RDF.type, mar.BaleineMysticete))
        for sp in [Cachalot, Orque, Globicephale, BalABec, BalABecBotNose]:
            self.g.add((sp, RDF.type, mar.BaleineOdontocete))

        # Oiseaux marins
        Albatros    = bird("Espece_Albatros",    "Albatros",         "Albatross",       "Diomedea spp. / Phoebastria spp.")
        Petrel      = bird("Espece_Petrel",      "Pétrel",           "Petrel",          "Pterodroma spp. / Procellaria spp.")
        Manchot     = bird("Espece_Manchot",     "Manchot",          "Penguin",         "Spheniscidae spp.", "Partielle (protégé zones antarctiques)")
        Fou         = bird("Espece_FouBassan",   "Fou de Bassan",    "Northern Gannet", "Morus bassanus")
        FouMasque   = bird("Espece_FouMasque",   "Fou masqué",       "Masked Booby",    "Sula dactylatra")
        Sterne      = bird("Espece_SterneFuligineuse", "Sterne fuligineuse", "Sooty Tern", "Onychoprion fuscatus")

        # Sous-classe migrateur pour les oiseaux CMS
        for sp in [Albatros, Petrel]:
            self.g.add((sp, RDF.type, mar.OiseauMarinMigrateur))

        # Tortues marines
        TortueVerte     = turtle("Espece_TortueVerte",      "Tortue verte",         "Green sea turtle",       "Chelonia mydas")
        TortueCarett    = turtle("Espece_TortueCarett",     "Tortue caouanne",      "Loggerhead sea turtle",  "Caretta caretta")
        TortueLuth      = turtle("Espece_TortueLuth",       "Tortue luth",          "Leatherback sea turtle", "Dermochelys coriacea")
        TortueHawksbill = turtle("Espece_TortueHawksbill",  "Tortue imbriquée",     "Hawksbill sea turtle",   "Eretmochelys imbricata")

        self._species = {
            "baleines": [BalFranche, BalBoreal, BalGrise, BalBleue, BalFin, BalBosse,
                         BalSei, BalBreyde, BalMinke, PetBalFranche,
                         Cachalot, Orque, Globicephale, BalABec, BalABecBotNose],
            "oiseaux": [Albatros, Petrel, Manchot, Fou, FouMasque, Sterne],
            "tortues": [TortueVerte, TortueCarett, TortueLuth, TortueHawksbill],
        }
        logger.info("    ✅ %d espèces marines créées",
                    sum(len(v) for v in self._species.values()))

    # ══════════════════════════════════════════════════════════════
    # 5. INDIVIDUS INTERDICTIONS (I001 – I006)
    # ══════════════════════════════════════════════════════════════
    def populate_interdictions(self):
        logger.info("  ⚖️ Population des 6 interdictions maritimes...")
        self._populate_I001()
        self._populate_I002()
        self._populate_I003()
        self._populate_I004()
        self._populate_I005()
        self._populate_I006()

    # ── I001 : Chalutage de fond ──────────────────────────────────
    def _populate_I001(self):
        mar = self.mar
        I001 = self._ind("I001", mar.Interdiction,
            "Interdiction du chalutage de fond",
            "Prohibition of Deep-Sea Bottom Trawling on the High Seas",
            skos_label=True)
        self.g.add((I001, self.skos.definition, Literal(
            "Norme internationale interdisant le chalutage de fond en l'absence "
            "d'évaluation préalable d'impact sur les Écosystèmes Marins Vulnérables (EMV). "
            "Fondée sur les Résolutions AGNU A/RES/61/105 (2006), A/RES/64/72 (2009), "
            "A/RES/66/68 (2011) et A/RES/71/123 (2016).", lang="fr")))

        # Données
        self._data(I001, mar.legalLayer, "International", XSD.string)
        self._data(I001, mar.typeActivite, "CHALUTAGE_FOND", XSD.string)
        self._data(I001, mar.deonticType, "Interdiction", XSD.string)
        self._data(I001, mar.confidence, 1.0, XSD.decimal)
        self.g.add((I001, mar.needsReview, Literal(False, datatype=XSD.boolean)))
        self._data(I001, mar.sourceConvention, "A/RES/61/105 (2006)", XSD.string)
        self._data(I001, mar.sourceConvention, "A/RES/64/72 (2009)", XSD.string)
        self._data(I001, mar.sourceConvention, "A/RES/66/68 (2011)", XSD.string)
        self._data(I001, mar.sourceConvention, "A/RES/71/123 (2016)", XSD.string)

        # Activité
        activite = self._ind("Activite_CHALUTAGE_FOND", mar.ChalutageFond,
            "Chalutage de fond", "Bottom trawling", skos_label=True)
        self._link(I001, mar.concerneActivite, activite)

        # Zones
        self._link(I001, mar.appliesInZone, self._zones["HM"])
        self._link(I001, mar.appliesInZone, self._zones["ZEV"])
        self._link(I001, mar.appliesInZone, self._zones["EEZ"])

        # Acteurs
        self._link(I001, mar.concerneActeur, self._acteurs["Etats"])
        self._link(I001, mar.concerneActeur, self._acteurs["EtatPavillon"])
        self._link(I001, mar.concerneActeur, self._acteurs["ORGP"])
        self._link(I001, mar.concerneActeur, self._acteurs["FAO"])

        # Sources juridiques
        self._link(I001, mar.fondeeSur, self._sources["Res61"])
        self._link(I001, mar.fondeeSur, self._sources["Res64"])
        self._link(I001, mar.fondeeSur, self._sources["Res66"])
        self._link(I001, mar.fondeeSur, self._sources["Res71"])
        self._link(I001, mar.fondeeSur, self._sources["FAO_Directives"])
        # Inverses
        for s in [self._sources["Res61"], self._sources["Res64"],
                  self._sources["Res66"], self._sources["Res71"]]:
            self._link(s, mar.institueNorme, I001)

        # Exceptions
        exc_dev = self._ind("Exception_EtatsDeveloppement", mar.ExceptionJuridique,
            "Besoins particuliers des États en développement",
            comment="Source : A/RES/61/105 §121")
        exc_mesures = self._ind("Exception_MesuresConservation", mar.ExceptionJuridique,
            "Si mesures de conservation et gestion adoptées par une ORGP compétente",
            comment="Source : A/RES/64/72 §119b")
        exc_artisanal = self._ind("Exception_PecheArtisanale", mar.ExceptionJuridique,
            "Pêche artisanale à petite échelle dans les eaux sous juridiction nationale",
            comment="Exception pour les États côtiers en développement")
        exc_science = self._ind("Exception_RechercheScientiqueI001", mar.ExceptionJuridique,
            "Opérations de recherche scientifique dûment autorisées",
            comment="Autorisation préalable requise")
        for exc in [exc_dev, exc_mesures, exc_artisanal, exc_science]:
            self._link(I001, mar.aException, exc)

        # Périodes
        per_abs_eval = self._ind("Periode_AbsenceEvaluation", mar.PeriodeConditionnelle,
            "En l'absence d'évaluations d'impact scientifiques préalables")
        per_abs_mes = self._ind("Periode_AbsenceMesures", mar.PeriodeConditionnelle,
            "En l'absence de mesures de gestion adoptées par une ORGP")
        self._link(I001, mar.appliesDuring, per_abs_eval)
        self._link(I001, mar.appliesDuring, per_abs_mes)

        # Contrôle
        ctrl = self._ind("Controle_ChalutageFond", mar.ControleOrgRegional,
            "Contrôle des ORGP — évaluation préalable d'impact sur les EMV",
            definition="Les ORGP compétentes doivent procéder à une évaluation d'impact préalable selon les Directives FAO 2008.")
        self._link(I001, mar.soumisAControle, ctrl)

        # Sanction
        sanction = self._ind("Sanction_ChalutageFond", mar.SanctionAdministrative,
            "Suspension des licences de pêche / interdiction d'accès aux zones",
            definition="L'État du pavillon peut retirer les autorisations de pêche pour violation des règles sur les EMV.")
        self._link(I001, mar.entraineSanction, sanction)

        logger.info("    ✅ I001 — Chalutage de fond")

    # ── I002 : Chasse à la Baleine ────────────────────────────────
    def _populate_I002(self):
        mar = self.mar
        I002 = self._ind("I002", mar.Interdiction,
            "Interdiction de la chasse à la baleine",
            "Prohibition of Commercial Whaling",
            skos_label=True)
        self.g.add((I002, self.skos.definition, Literal(
            "Moratoire mondial sur la chasse commerciale à la baleine.", lang="fr")))

        # Données
        self._data(I002, mar.legalLayer, "International", XSD.string)
        self._data(I002, mar.typeActivite, "CHASSE_BALEINE", XSD.string)
        self._data(I002, mar.deonticType, "Interdiction", XSD.string)
        self._data(I002, mar.confidence, 1.0, XSD.decimal)
        self.g.add((I002, mar.needsReview, Literal(False, datatype=XSD.boolean)))
        self._data(I002, mar.sourceConvention, "ICRW 1946", XSD.string)
        self._data(I002, mar.sourceConvention, "IWC Schedule (para. 10(e), amendé 1982)", XSD.string)

        # Activités
        activite = self._ind("Activite_CHASSE_BALEINE", mar.ChasseCommercialeBaleine,
            "Chasse commerciale à la baleine", "Commercial Whaling", skos_label=True)
        self._link(I002, mar.concerneActivite, activite)

        # Zones
        for zone_key in ["HM", "SanctuaireAustral", "SanctuaireIndien", "HemisphereSud"]:
            self._link(I002, mar.appliesInZone, self._zones[zone_key])

        # Acteurs
        for a_key in ["MembreIWC", "NavireUsine", "BateauChasseur", "StationTerrestre"]:
            self._link(I002, mar.concerneActeur, self._acteurs[a_key])

        # Sources
        self._link(I002, mar.fondeeSur, self._sources["ICRW"])
        self._link(I002, mar.fondeeSur, self._sources["IWC_Schedule"])
        self._link(self._sources["ICRW"], mar.institueNorme, I002)
        self._link(self._sources["IWC_Schedule"], mar.institueNorme, I002)

        # Espèces protégées (toutes les baleines)
        for sp in self._species["baleines"]:
            self._link(I002, mar.protegeEspece, sp)
            self._link(sp, mar.estMenacePar, activite)

        # Exceptions
        exc_sci = self._ind("Exception_ChasseScientiqueArticle8", mar.ExceptionJuridique,
            "Chasse à des fins scientifiques (Article VIII ICRW)",
            comment="Source : ICRW Art. VIII — permis délivré par l'État membre, sous contrôle CBI.")
        exc_sub = self._ind("Exception_ChasseSubsistanceAutochtone", mar.ExceptionJuridique,
            "Chasse de subsistance autochtone (Aboriginal Subsistence Whaling)",
            comment="Source : IWC Schedule §13 — quotas négociés quinquennalement par la CBI.")
        for exc in [exc_sci, exc_sub]:
            self._link(I002, mar.aException, exc)

        # Permissions correspondantes
        perm_sci = self._ind("Permission_ChasseScientiqueArticle8", self.lkif.Permission,
            "Permission : Chasse scientifique (Article VIII ICRW)",
            "Permission: Scientific Whaling (Article VIII ICRW)")
        self.g.add((perm_sci, self.skos.definition, Literal(
            "Autorisation de chasse scientifique sous permis national délivré par l'État membre (Art. VIII ICRW). "
            "La CBI peut formuler des recommandations sur les permis mais ne peut pas les annuler.", lang="fr")))
        self._link(perm_sci, mar.beneficieA, self._acteurs["MembreIWC"])
        self._link(I002, mar.hasDerogation, perm_sci)

        perm_sub = self._ind("Permission_ChasseSubsistanceAutochtone", self.lkif.Permission,
            "Permission : Chasse de subsistance autochtone",
            "Permission: Aboriginal Subsistence Whaling")
        self.g.add((perm_sub, self.skos.definition, Literal(
            "Quotas de chasse accordés aux communautés autochtones dont la subsistance dépend "
            "traditionnellement des cétacés — négociés lors de chaque réunion quinquennale de la CBI.", lang="fr")))
        self._link(perm_sub, mar.beneficieA, self._acteurs["CommunauteAutochtone"])
        self._link(I002, mar.hasDerogation, perm_sub)

        # Période
        per_moratoire = self._ind("Periode_Moratoire1986", mar.PeriodePermanente,
            "Depuis l'entrée en vigueur du moratoire (saison 1985/1986)")
        bnode_inst = BNode()
        self.g.add((bnode_inst, RDF.type, URIRef(NS_TIME + "Instant")))
        self.g.add((bnode_inst, URIRef(NS_TIME + "inXSDDate"), Literal("1986-01-01", datatype=XSD.date)))
        self.g.add((per_moratoire, URIRef(NS_TIME + "hasBeginning"), bnode_inst))
        self._link(I002, mar.appliesDuring, per_moratoire)

        # Contrôles
        ctrl_sci = self._ind("Controle_ChasseScientiqueICRW", mar.ControleOrgRegional,
            "Contrôle CBI de la chasse scientifique (ICRW Art. VIII)",
            definition="La CBI examine les permis scientifiques et peut formuler des recommandations. Sous-comité scientifique.")
        ctrl_asa = self._ind("Controle_QuotasSubsistanceAutochtone", mar.ControleOrgRegional,
            "Contrôle CBI des quotas de subsistance autochtone",
            definition="Quotas négociés et approuvés lors des réunions quinquennales de la CBI.")
        for ctrl in [ctrl_sci, ctrl_asa]:
            self._link(I002, mar.soumisAControle, ctrl)

        # Sanction
        sanct = self._ind("Sanction_ChasseBaleine", mar.SanctionPenale,
            "Sanctions pénales et saisie du navire pour chasse illégale à la baleine",
            definition="La violation du moratoire IWC peut entraîner des sanctions pénales selon la législation de l'État du pavillon.")
        self._link(I002, mar.entraineSanction, sanct)

        logger.info("    ✅ I002 — Chasse à la baleine")

    # ── I003 : Construction littorale ────────────────────────────
    def _populate_I003(self):
        mar = self.mar
        I003 = self._ind("I003", mar.Interdiction,
            "Interdiction de construire sur le littoral",
            "Prohibition of Unregulated Coastal Construction",
            skos_label=True)
        self.g.add((I003, self.skos.definition, Literal(
            "Interdiction de toute construction sur le littoral.", lang="fr")))

        self._data(I003, mar.legalLayer, "National/Régional", XSD.string)
        self._data(I003, mar.typeActivite, "CONSTRUCTION_COTIERE", XSD.string)
        self._data(I003, mar.deonticType, "Interdiction", XSD.string)
        self._data(I003, mar.confidence, 0.9, XSD.decimal)
        self.g.add((I003, mar.needsReview, Literal(False, datatype=XSD.boolean)))
        self._data(I003, mar.sourceConvention, "Loi Littoral n°86-2 du 3 janvier 1986", XSD.string)
        self._data(I003, mar.sourceConvention, "Protocole GIZC Méditerranée (2008)", XSD.string)

        # Activité
        activite = self._ind("Activite_CONSTRUCTION_LITTORALE", mar.ConstructionLittorale,
            "Construction et aménagement sur le littoral", "Coastal Construction and Development",
            skos_label=True)
        self._link(I003, mar.concerneActivite, activite)

        # Zones
        self._link(I003, mar.appliesInZone, self._zones["ZoneCote"])
        self._link(I003, mar.appliesInZone, self._zones["MT"])

        # Acteurs
        self._link(I003, mar.concerneActeur, self._acteurs["Promoteur"])
        self._link(I003, mar.concerneActeur, self._acteurs["EtatCotier"])

        # Sources
        self._link(I003, mar.fondeeSur, self._sources["LoiLittoral"])
        self._link(I003, mar.fondeeSur, self._sources["ProtoGIZC"])
        self._link(I003, mar.fondeeSur, self._sources["UNCLOS"])
        self._link(self._sources["LoiLittoral"], mar.institueNorme, I003)
        self._link(self._sources["ProtoGIZC"], mar.institueNorme, I003)

        # (Lien avec les tortues retiré pour fidélité stricte au texte extrait)

        # Exceptions
        exc_agglomeration = self._ind("Exception_AgglomerationExistante", mar.ExceptionJuridique,
            "Constructions dans les agglomérations existantes (extensions limitées)",
            comment="Art. L. 121-16 Code de l'urbanisme — exception pour les agglomérations déjà urbanisées.")
        exc_infrastructure = self._ind("Exception_InfrastructureInteret_Public", mar.ExceptionJuridique,
            "Infrastructures ou équipements publics nécessitant la proximité immédiate de la mer",
            comment="Art. L. 121-17 — ports, ouvrages de protection, etc.")
        for exc in [exc_agglomeration, exc_infrastructure]:
            self._link(I003, mar.aException, exc)

        # Période
        per = self._ind("Periode_LoiLittoral", mar.PeriodePermanente,
            "Depuis l'entrée en vigueur de la Loi Littoral (1986)")
        bnode_inst = BNode()
        self.g.add((bnode_inst, RDF.type, URIRef(NS_TIME + "Instant")))
        self.g.add((bnode_inst, URIRef(NS_TIME + "inXSDDate"), Literal("1986-01-03", datatype=XSD.date)))
        self.g.add((per, URIRef(NS_TIME + "hasBeginning"), bnode_inst))
        self._link(I003, mar.appliesDuring, per)

        # Contrôle
        ctrl = self._ind("Controle_PermisConstruction", mar.ControleEtatPavillon,
            "Contrôle administratif — permis de construire et autorisation littoral",
            definition="L'État côtier contrôle les permis de construire dans la bande littorale protégée.")
        self._link(I003, mar.soumisAControle, ctrl)

        # Sanction
        sanct = self._ind("Sanction_ConstructionIllegale", mar.SanctionPenale,
            "Démolition, amende pénale et remise en état pour construction illicite sur le littoral",
            definition="Art. L. 480-5 Code de l'urbanisme — démolition judiciaire et amende jusqu'à 300 000 €.")
        self._link(I003, mar.entraineSanction, sanct)

        logger.info("    ✅ I003 — Construction littorale")

    # ── I004 : Extraction de Sable ────────────────────────────────
    def _populate_I004(self):
        mar = self.mar
        I004 = self._ind("I004", mar.Interdiction,
            "Interdiction de l'extraction de sable",
            "Prohibition of Unregulated Marine Sand Extraction",
            skos_label=True)
        self.g.add((I004, self.skos.definition, Literal(
            "Interdiction de l'extraction de sable marin non réglementée.", lang="fr")))

        self._data(I004, mar.legalLayer, "International", XSD.string)
        self._data(I004, mar.typeActivite, "EXTRACTION_SABLE", XSD.string)
        self._data(I004, mar.deonticType, "Interdiction", XSD.string)
        self._data(I004, mar.confidence, 0.85, XSD.decimal)
        self.g.add((I004, mar.needsReview, Literal(False, datatype=XSD.boolean)))
        self._data(I004, mar.sourceConvention, "Convention sur la Diversité Biologique (CDB, Rio 1992)", XSD.string)

        # Activité
        activite = self._ind("Activite_EXTRACTION_SABLE", mar.ExtractionSable,
            "Extraction de sable marin (dragage industriel)", "Marine Sand Extraction / Dredging",
            skos_label=True)
        self._link(I004, mar.concerneActivite, activite)

        # Zones
        self._link(I004, mar.appliesInZone, self._zones["EEZ"])
        self._link(I004, mar.appliesInZone, self._zones["ZoneCote"])
        self._link(I004, mar.appliesInZone, self._zones["ZEV"])

        # Acteurs
        self._link(I004, mar.concerneActeur, self._acteurs["Etats"])
        self._link(I004, mar.concerneActeur, self._acteurs["EtatCotier"])

        # Sources
        self._link(I004, mar.fondeeSur, self._sources["CBD"])
        self._link(self._sources["CBD"], mar.institueNorme, I004)

        # (Lien avec les tortues retiré pour fidélité stricte au texte extrait)

        # Exceptions
        exc_artisanal = self._ind("Exception_UsageArtisanalSable", mar.ExceptionJuridique,
            "Utilisation traditionnelle et artisanale du sable marin par les communautés locales",
            comment="Art. 10(c) CDB — utilisation coutumière compatible avec la conservation.")
        exc_eias = self._ind("Exception_EIES_Sable", mar.ExceptionJuridique,
            "Extraction autorisée après évaluation d'impact sur la diversité biologique (EIES/EIE)",
            comment="Art. 14(a) CDB — obligation d'EIE pour les projets susceptibles d'affecter la biodiversité.")
        for exc in [exc_artisanal, exc_eias]:
            self._link(I004, mar.aException, exc)

        # Contrôle
        ctrl = self._ind("Controle_ExtractionSable", mar.ControleEtatPavillon,
            "Contrôle national — autorisation d'extraction et suivi environnemental",
            definition="Les États côtiers doivent soumettre les projets d'extraction à une évaluation préalable d'impact (Art. 14 CDB).")
        self._link(I004, mar.soumisAControle, ctrl)

        # Sanction
        sanct = self._ind("Sanction_ExtractionSableIllicite", mar.SanctionAdministrative,
            "Suspension de l'autorisation d'extraction et remise en état des habitats dégradés",
            definition="Obligation de réhabilitation des habitats marins dégradés par une extraction illicite.")
        self._link(I004, mar.entraineSanction, sanct)

        logger.info("    ✅ I004 — Extraction de sable")

    # ── I005 : Oiseaux Marins ─────────────────────────────────────
    def _populate_I005(self):
        mar = self.mar
        I005 = self._ind("I005", mar.Interdiction,
            "Interdiction de la chasse des oiseaux marins",
            "Prohibition of Capture and Disturbance of Migratory Seabirds",
            skos_label=True)
        self.g.add((I005, self.skos.definition, Literal(
            "Interdiction de la capture et de la perturbation des oiseaux marins.", lang="fr")))

        self._data(I005, mar.legalLayer, "International", XSD.string)
        self._data(I005, mar.typeActivite, "CAPTURE_OISEAUX_MARINS", XSD.string)
        self._data(I005, mar.deonticType, "Interdiction", XSD.string)
        self._data(I005, mar.confidence, 0.9, XSD.decimal)
        self.g.add((I005, mar.needsReview, Literal(False, datatype=XSD.boolean)))
        self._data(I005, mar.sourceConvention, "Convention CMS / Convention de Bonn (1979)", XSD.string)
        self._data(I005, mar.sourceConvention, "Accord ACAP (2004)", XSD.string)

        # Activité
        activite = self._ind("Activite_CAPTURE_OISEAUX_MARINS", mar.CaptureOiseauxMarins,
            "Capture, détention ou perturbation délibérée des oiseaux marins",
            "Seabird Capture, Detention or Deliberate Disturbance",
            skos_label=True)
        self._link(I005, mar.concerneActivite, activite)

        # Zones
        self._link(I005, mar.appliesInZone, self._zones["HM"])
        self._link(I005, mar.appliesInZone, self._zones["EEZ"])
        self._link(I005, mar.appliesInZone, self._zones["ZoneCote"])

        # Acteurs
        self._link(I005, mar.concerneActeur, self._acteurs["Etats"])
        self._link(I005, mar.concerneActeur, self._acteurs["EtatCotier"])

        # Sources
        self._link(I005, mar.fondeeSur, self._sources["CMS"])
        self._link(I005, mar.fondeeSur, self._sources["ACAP"])
        self._link(self._sources["CMS"], mar.institueNorme, I005)
        self._link(self._sources["ACAP"], mar.institueNorme, I005)

        # Espèces protégées (oiseaux marins)
        for sp in self._species["oiseaux"]:
            self._link(I005, mar.protegeEspece, sp)
            self._link(sp, mar.estMenacePar, activite)

        # Exception
        exc_bycatch = self._ind("Exception_PrisesAccessoires_Oiseaux", mar.ExceptionJuridique,
            "Prises accessoires (bycatch) non intentionnelles d'oiseaux marins lors de la pêche",
            comment="Non intentionnel — obligation de minimiser, signaler et libérer vivants si possible.")
        exc_baguing = self._ind("Exception_RechercheBaguage", mar.ExceptionJuridique,
            "Capture scientifique pour baguage ou télémétrie autorisée par permis national",
            comment="Art. III.5(d) CMS — activité de recherche autorisée sous permis.")
        for exc in [exc_bycatch, exc_baguing]:
            self._link(I005, mar.aException, exc)

        # Permission
        perm_sci = self._ind("Permission_RechercheBaguage_Oiseaux", self.lkif.Permission,
            "Permission : Baguage et télémétrie sous permis scientifique national")
        self._link(perm_sci, mar.beneficieA, self._acteurs["Etats"])
        self._link(I005, mar.hasDerogation, perm_sci)

        # Contrôle
        ctrl = self._ind("Controle_OiseauxMarins_CMS", mar.ControleOrgRegional,
            "Contrôle via les mécanismes de la Convention CMS et de l'Accord ACAP",
            definition="Rapports triennaux des États parties à la CMS — surveillance des populations par le Secrétariat.")
        self._link(I005, mar.soumisAControle, ctrl)

        # Sanction
        sanct = self._ind("Sanction_CaptureOiseaux", mar.SanctionPenale,
            "Sanctions pénales nationales pour capture illicite d'oiseaux marins protégés",
            definition="Les États parties à la CMS sont tenus d'adopter des sanctions pénales nationales.")
        self._link(I005, mar.entraineSanction, sanct)

        logger.info("    ✅ I005 — Oiseaux marins")

    # ── I006 : Rejet Hydrocarbures ────────────────────────────────
    def _populate_I006(self):
        mar = self.mar
        I006 = self._ind("I006", mar.Interdiction,
            "Interdiction du rejet d'hydrocarbures",
            "Prohibition of Oil Discharges at Sea (MARPOL)",
            skos_label=True)
        self.g.add((I006, self.skos.definition, Literal(
            "Interdiction de tout rejet dans la mer d'hydrocarbures.", lang="fr")))

        self._data(I006, mar.legalLayer, "International/Régional", XSD.string)
        self._data(I006, mar.typeActivite, "REJET_HYDROCARBURES", XSD.string)
        self._data(I006, mar.deonticType, "Interdiction", XSD.string)
        self._data(I006, mar.confidence, 1.0, XSD.decimal)
        self.g.add((I006, mar.needsReview, Literal(False, datatype=XSD.boolean)))
        self._data(I006, mar.sourceConvention, "MARPOL 73/78 Annexe I", XSD.string)
        self._data(I006, mar.sourceConvention, "Règlement UEMOA N°06/2022", XSD.string)
        self._data(I006, mar.concentrationPPM, 15.0, XSD.decimal)

        # Activité
        activite = self._ind("Activite_REJET_HYDROCARBURES", mar.RejetsHydrocarbures,
            "Rejet d'hydrocarbures et mélanges en mer", "Marine Oil Discharge",
            skos_label=True)
        self.g.add((activite, mar.concentrationPPM, Literal(15.0, datatype=XSD.decimal)))
        self._link(I006, mar.concerneActivite, activite)

        # Zones
        self._link(I006, mar.appliesInZone, self._zones["HM"])
        self._link(I006, mar.appliesInZone, self._zones["EEZ"])
        self._link(I006, mar.appliesInZone, self._zones["MT"])
        for z_key in ["ZoneMed", "ZoneBaltique", "ZoneNoire", "ZoneRouge", "ZoneGolfe", "ZoneAntarctique"]:
            self._link(I006, mar.appliesInZone, self._zones[z_key])

        # Acteurs
        for a_key in ["Armateur", "Capitaine", "NavirePetrolier", "OperateurOffshore", "IMO"]:
            self._link(I006, mar.concerneActeur, self._acteurs[a_key])

        # Sources
        self._link(I006, mar.fondeeSur, self._sources["MARPOL"])
        self._link(I006, mar.fondeeSur, self._sources["MEPC117"])
        self._link(I006, mar.fondeeSur, self._sources["UEMOA"])
        self._link(self._sources["MARPOL"], mar.institueNorme, I006)
        self._link(self._sources["MEPC117"], mar.institueNorme, I006)

        # Exceptions
        exc_urgence = self._ind("Exception_RejetUrgenceSecurite", mar.ExceptionJuridique,
            "Rejet nécessaire pour la sécurité du navire ou la sauvegarde des vies humaines",
            comment="MARPOL Annexe I Règle 4 — dérogation pour raisons de sécurité/urgence.")
        exc_dommage = self._ind("Exception_RejetAccidentelDommage", mar.ExceptionJuridique,
            "Rejet consécutif à un dommage au navire ou à son équipement (si précautions prises)",
            comment="MARPOL Annexe I Règle 4(b) — responsabilité réduite si mesures de prévention prises.")
        exc_reception = self._ind("Exception_ReceptionInstallationsPortuaires", mar.ExceptionJuridique,
            "Impossibilité de déchargement aux installations de réception portuaires (documentation requise)",
            comment="MARPOL — obligation de documentation et signalement en l'absence d'installations adéquates.")
        for exc in [exc_urgence, exc_dommage, exc_reception]:
            self._link(I006, mar.aException, exc)

        # Contrôles
        ctrl_psc = self._ind("Controle_PSC_MARPOL", mar.ControleEtatPort,
            "Contrôle par l'État du Port (Port State Control — Paris MOU, Tokyo MOU)",
            definition="Inspection MARPOL des navires étrangers dans les ports — vérification du registre des hydrocarbures, de l'IOPP.")
        ctrl_flag = self._ind("Controle_EtatPavillon_MARPOL", mar.ControleEtatPavillon,
            "Contrôle de l'État du Pavillon — inspection et certification IOPP",
            definition="L'État du pavillon délivre le Certificat International de Prévention de la Pollution par les Hydrocarbures (IOPP) et inspecte les navires.")
        for ctrl in [ctrl_psc, ctrl_flag]:
            self._link(I006, mar.soumisAControle, ctrl)

        # Sanction
        sanct_pen = self._ind("Sanction_RejetHydrocarbures_Penale", mar.SanctionPenale,
            "Sanctions pénales et poursuite criminelle du capitaine pour rejet illicite",
            definition="Les États signataires MARPOL doivent prévoir des sanctions pénales suffisamment dissuasives — emprisonnement et amende.")
        sanct_adm = self._ind("Sanction_RejetHydrocarbures_Admin", mar.SanctionAdministrative,
            "Immobilisation du navire, refus d'accès au port, retrait de l'IOPP",
            definition="Port State Control peut immobiliser un navire non conforme MARPOL jusqu'à remédiation.")
        for s in [sanct_pen, sanct_adm]:
            self._link(I006, mar.entraineSanction, s)

        # Stock concerné
        Stock_ALL = self._ind("Stock_TOUS_LES_STOCKS", mar.Stock,
            "Tous les stocks halieutiques (pollution impacts indifferenciés)")
        self._link(I006, mar.concerneStock, Stock_ALL)

        logger.info("    ✅ I006 — Rejet d'hydrocarbures")

    # ══════════════════════════════════════════════════════════════
    # 5b. HIÉRARCHIE D'EXCEPTIONS AVEC CONSÉQUENCES
    # ══════════════════════════════════════════════════════════════
    def populate_exception_consequences(self):
        """
        Enrichit les exceptions existantes avec :
        - Classification Générale / Spécifique
        - Conséquences conditionnelles (obligations qui découlent de l'exception)
        - Liens vers les contrôles associés
        """
        logger.info("  ⚖️  Population de la hiérarchie d'exceptions avec conséquences...")
        mar = self.mar

        # ── I001 : Chalutage de fond ──────────────────────────────
        # Exception générale : ORGP a adopté des mesures
        exc_mesures = self.mar["Exception_MesuresConservation"]
        self.g.add((exc_mesures, RDF.type, mar.ExceptionGenerale))
        csq_orgp = self._ind("Consequence_RespectPlanGestionORGP", mar.ConsequenceException,
            "Obligation de respecter le plan de gestion adopté par l'ORGP compétente",
            definition="Le chalutage n'est autorisé que dans le strict cadre des mesures "
                       "de conservation et de gestion adoptées par l'ORGP — tout dépassement "
                       "réactive l'interdiction (Rés. 64/72 §119b).")
        self._link(exc_mesures, mar.entraineConsequence, csq_orgp)

        # Exception spécifique : recherche scientifique
        exc_sci_I001 = self.mar["Exception_RechercheScientiqueI001"]
        self.g.add((exc_sci_I001, RDF.type, mar.ExceptionSpecifique))
        csq_sci_I001 = self._ind("Consequence_AutorisationRechercheChalutage", mar.ConsequenceException,
            "Obligation d'obtenir une autorisation préalable et de partager les résultats",
            definition="La recherche scientifique n'est exemptée que si dûment autorisée — "
                       "les résultats doivent être communiqués à l'ORGP compétente.")
        self._link(exc_sci_I001, mar.entraineConsequence, csq_sci_I001)
        self._link(exc_mesures, mar.aExceptionSpecifique, exc_sci_I001)

        # Exception spécifique : pêche artisanale
        exc_art = self.mar["Exception_PecheArtisanale"]
        self.g.add((exc_art, RDF.type, mar.ExceptionSpecifique))
        csq_art = self._ind("Consequence_PecheZEEUniquement", mar.ConsequenceException,
            "Restriction aux eaux sous juridiction nationale (ZEE) uniquement",
            definition="La pêche artisanale n'est exemptée qu'à l'intérieur de la ZEE "
                       "de l'État côtier — interdiction stricte en haute mer.")
        self._link(exc_art, mar.entraineConsequence, csq_art)
        self._link(exc_mesures, mar.aExceptionSpecifique, exc_art)

        # ── I002 : Chasse à la baleine ────────────────────────────
        # Exception générale : chasse scientifique Art. VIII
        exc_sci = self.mar["Exception_ChasseScientiqueArticle8"]
        self.g.add((exc_sci, RDF.type, mar.ExceptionGenerale))
        csq_sci_rapport = self._ind("Consequence_RapportCBI_Scientifique", mar.ConsequenceException,
            "Obligation de soumettre les résultats au Comité Scientifique de la CBI",
            definition="Art. VIII §2 ICRW : tout permis scientifique oblige l'État "
                       "à transmettre les résultats à la CBI dans un délai raisonnable.")
        csq_sci_produits = self._ind("Consequence_TraitementProduits", mar.ConsequenceException,
            "Obligation de traitement des produits dérivés conformément aux directives CBI",
            definition="Art. VIII §2 ICRW : les produits dérivés de la chasse scientifique "
                       "doivent être traités selon les directives de la Commission.")
        self._link(exc_sci, mar.entraineConsequence, csq_sci_rapport)
        self._link(exc_sci, mar.entraineConsequence, csq_sci_produits)
        # Contrôle conditionnel
        ctrl_sci = self.mar["Controle_ChasseScientiqueICRW"]
        if (ctrl_sci, RDF.type, OWL.NamedIndividual) in self.g:
            self._link(exc_sci, mar.conditionneePar, ctrl_sci)

        # Exception générale : subsistance autochtone
        exc_sub = self.mar["Exception_ChasseSubsistanceAutochtone"]
        self.g.add((exc_sub, RDF.type, mar.ExceptionGenerale))
        csq_quota = self._ind("Consequence_QuotaQuinquennalCBI", mar.ConsequenceException,
            "Respect des quotas quinquennaux fixés par la CBI (IWC Schedule §13)",
            definition="Les quotas de chasse autochtone sont négociés à chaque réunion "
                       "quinquennale de la CBI — tout dépassement est une infraction.")
        csq_non_commercial = self._ind("Consequence_InterdictionVenteCommerciale", mar.ConsequenceException,
            "Interdiction absolue de vente commerciale des produits de chasse autochtone",
            definition="Les produits de la chasse de subsistance ne peuvent être vendus "
                       "sur le marché commercial — usage local et culturel uniquement.")
        self._link(exc_sub, mar.entraineConsequence, csq_quota)
        self._link(exc_sub, mar.entraineConsequence, csq_non_commercial)

        # Exception spécifique sous subsistance : quotas Groenland
        exc_groenland = self._ind("Exception_QuotaGroenland", mar.ExceptionSpecifique,
            "Quota spécifique Groenland — baleine à bosse et baleine de Minke",
            comment="IWC Schedule §13 — quotas par espèce et par an pour le Groenland.")
        csq_groenland = self._ind("Consequence_LimiteCaptures_Groenland", mar.ConsequenceException,
            "Limite annuelle de captures fixée par la CBI pour le Groenland",
            definition="Quotas spécifiques : ex. 164 baleines de Minke/an, "
                       "19 baleines à nageoires/an (révisés quinquennalement).")
        self._link(exc_sub, mar.aExceptionSpecifique, exc_groenland)
        self._link(exc_groenland, mar.entraineConsequence, csq_groenland)

        # ── I004 : Extraction de sable ────────────────────────────
        exc_eias = self.mar["Exception_EIES_Sable"]
        self.g.add((exc_eias, RDF.type, mar.ExceptionGenerale))
        csq_eias = self._ind("Consequence_EIES_Obligatoire", mar.ConsequenceException,
            "Obligation de réaliser une Évaluation d'Impact Environnemental et Social (EIES)",
            definition="CDB Art. 14 — toute extraction autorisée doit être précédée d'une "
                       "EIES démontrant que les impacts sur la biodiversité sont acceptables.")
        csq_compensation = self._ind("Consequence_MesuresCompensatoires", mar.ConsequenceException,
            "Obligation de mettre en œuvre des mesures compensatoires pour les habitats détruits",
            definition="Les dommages aux habitats benthiques doivent être compensés — "
                       "restauration écologique, création d'aires protégées de remplacement.")
        self._link(exc_eias, mar.entraineConsequence, csq_eias)
        self._link(exc_eias, mar.entraineConsequence, csq_compensation)

        exc_artisanal_sable = self.mar["Exception_UsageArtisanalSable"]
        self.g.add((exc_artisanal_sable, RDF.type, mar.ExceptionSpecifique))
        csq_artisanal_sable = self._ind("Consequence_VolumeMinimeSable", mar.ConsequenceException,
            "Limitation à des volumes d'extraction non significatifs pour la dynamique sédimentaire",
            definition="L'usage artisanal est toléré sous réserve que les quantités prélevées "
                       "n'altèrent pas la dynamique sédimentaire côtière.")
        self._link(exc_artisanal_sable, mar.entraineConsequence, csq_artisanal_sable)
        self._link(exc_eias, mar.aExceptionSpecifique, exc_artisanal_sable)

        # ── I003 : Construction littorale ─────────────────────────
        exc_agglo = self.mar["Exception_AgglomerationExistante"]
        self.g.add((exc_agglo, RDF.type, mar.ExceptionGenerale))
        csq_agglo = self._ind("Consequence_ContinuiteUrbaine", mar.ConsequenceException,
            "Construction autorisée uniquement en continuité de l'urbanisation existante",
            definition="Loi Littoral Art. L121-8 — la construction n'est permise que dans "
                       "la continuité des agglomérations et villages existants.")
        self._link(exc_agglo, mar.entraineConsequence, csq_agglo)

        exc_infra = self.mar["Exception_InfrastructureInteret_Public"]
        self.g.add((exc_infra, RDF.type, mar.ExceptionSpecifique))
        csq_infra = self._ind("Consequence_DeclarationInteretGeneral", mar.ConsequenceException,
            "Obligation de déclaration d'intérêt général et d'impossibilité d'implantation ailleurs",
            definition="L'exception n'est recevable que si l'équipement ne peut être "
                       "localisé en dehors de la bande littorale protégée.")
        self._link(exc_infra, mar.entraineConsequence, csq_infra)
        self._link(exc_agglo, mar.aExceptionSpecifique, exc_infra)

        # ── I005 : Oiseaux marins ─────────────────────────────────
        exc_bycatch = self.mar["Exception_PrisesAccessoires_Oiseaux"]
        self.g.add((exc_bycatch, RDF.type, mar.ExceptionGenerale))
        csq_bycatch = self._ind("Consequence_MesuresAttenuation_Bycatch", mar.ConsequenceException,
            "Obligation de mise en œuvre des mesures d'atténuation ACAP/CMS",
            definition="L'activité de pêche est tolérée sous réserve de l'utilisation "
                       "de dispositifs anti-bycatch : hameçons lestés, lignes de dissuasion, "
                       "poses de nuit (ACAP Best Practice Advice).")
        self._link(exc_bycatch, mar.entraineConsequence, csq_bycatch)

        exc_baguage = self.mar["Exception_RechercheBaguage"]
        self.g.add((exc_baguage, RDF.type, mar.ExceptionSpecifique))
        csq_baguage = self._ind("Consequence_PermisCapture_Scientifique", mar.ConsequenceException,
            "Obligation d'obtenir un permis de capture scientifique national",
            definition="La capture pour baguage ou recherche n'est autorisée que "
                       "sous permis délivré par l'autorité nationale compétente.")
        self._link(exc_baguage, mar.entraineConsequence, csq_baguage)
        self._link(exc_bycatch, mar.aExceptionSpecifique, exc_baguage)

        # ── I006 : Rejet d'hydrocarbures ──────────────────────────
        exc_urgence = self.mar["Exception_RejetUrgenceSecurite"]
        self.g.add((exc_urgence, RDF.type, mar.ExceptionGenerale))
        csq_urgence = self._ind("Consequence_Signalement_Immediat", mar.ConsequenceException,
            "Obligation de signalement immédiat à l'État côtier le plus proche",
            definition="MARPOL Règle 4 — tout rejet d'urgence doit être signalé "
                       "immédiatement aux autorités maritimes de l'État côtier le plus proche.")
        csq_documentation = self._ind("Consequence_Documentation_Rejet", mar.ConsequenceException,
            "Obligation de documentation détaillée au registre des hydrocarbures",
            definition="Le registre des hydrocarbures (Oil Record Book) doit consigner "
                       "la raison, les quantités et les circonstances du rejet.")
        self._link(exc_urgence, mar.entraineConsequence, csq_urgence)
        self._link(exc_urgence, mar.entraineConsequence, csq_documentation)

        exc_dommage = self.mar["Exception_RejetAccidentelDommage"]
        self.g.add((exc_dommage, RDF.type, mar.ExceptionSpecifique))
        csq_dommage = self._ind("Consequence_PrecautionsRaisonnables", mar.ConsequenceException,
            "Obligation de prouver que toutes les précautions raisonnables ont été prises",
            definition="MARPOL Règle 4(b) — l'exemption n'est valable que si le propriétaire "
                       "ou le capitaine prouve que des précautions raisonnables ont été prises "
                       "après le dommage pour minimiser le rejet.")
        self._link(exc_dommage, mar.entraineConsequence, csq_dommage)
        self._link(exc_urgence, mar.aExceptionSpecifique, exc_dommage)

        exc_reception = self.mar["Exception_ReceptionInstallationsPortuaires"]
        self.g.add((exc_reception, RDF.type, mar.ExceptionSpecifique))
        csq_reception = self._ind("Consequence_Notification_Etat_Port", mar.ConsequenceException,
            "Obligation de notification à l'État du port de l'inadéquation des installations",
            definition="Le capitaine doit documenter et notifier l'impossibilité de décharger "
                       "aux installations portuaires et conserver la documentation à bord.")
        self._link(exc_reception, mar.entraineConsequence, csq_reception)
        self._link(exc_urgence, mar.aExceptionSpecifique, exc_reception)

        logger.info("    ✅ Hiérarchie d'exceptions avec conséquences peuplée (6 interdictions)")

    # ══════════════════════════════════════════════════════════════
    # 6. COUCHE LEXICALE SKOS
    # ══════════════════════════════════════════════════════════════
    def populate_lexical_layer(self, definitions: Optional[List[Any]] = None, glossary: Optional[List[Any]] = None):
        logger.info("  📖 Population de la couche lexicale SKOS...")
        mar = self.mar

        # Concepts ICRW/IWC
        concepts_icrw = [
            ("ConceptWhaling_Take",           "take",              "prendre (baleine)",
             "to flag, buoy or make fast to a whale."),
            ("ConceptWhaling_Strike",         "strike",            "frapper (baleine)",
             "to penetrate with a weapon used for whaling."),
            ("ConceptWhaling_Lose",           "lose",              "perdre (baleine)",
             "to either strike or take but not to land."),
            ("ConceptWhaling_Land",           "land",              "débarquer (baleine)",
             "to retrieve to a factory ship, land station, or any place where a whale can be treated."),
            ("ConceptWhaling_Dauhval",        "dauhval",           "dauhval",
             "any unclaimed dead whale found floating."),
            ("ConceptWhaling_BaleenWhale",    "baleen whale",      "cétacé à fanons",
             "any whale which has baleen or bone in the mouth."),
            ("ConceptWhaling_ToothedWhale",   "toothed whale",     "cétacé à dents",
             "any whale which has teeth in the jaws."),
            ("ConceptWhaling_LactatingWhale", "lactating whale",   "baleine allaitante",
             "female whale with milk present in a mammary gland."),
            ("ConceptWhaling_SmallTypeWhaling", "small-type whaling", "chasse à petite échelle",
             "catching operations using powered vessels with mounted harpoon guns for small cetaceans."),
        ]

        # Concepts MARPOL
        concepts_marpol = [
            ("ConceptMARPOL_OilyMixture",  "oily mixture",   "mélange d'hydrocarbures",
             "any mixture with any oil content as defined in MARPOL Annex I Rule 1."),
            ("ConceptMARPOL_SpecialArea",  "special area",   "zone spéciale MARPOL",
             "sea area where stricter discharge controls are required for oceanographical and ecological reasons (MARPOL Annex I Rule 1)."),
            ("ConceptMARPOL_IOPP",         "IOPP Certificate", "certificat IOPP",
             "International Oil Pollution Prevention Certificate — mandatory for ships of 400 GT and above (MARPOL Rule 7)."),
            ("ConceptMARPOL_15ppm",        "15 ppm rule",    "règle des 15 ppm",
             "Maximum hydrocarbon content of 15 parts per million allowed for machinery space bilge discharges outside special areas (MARPOL Annex I Rule 15)."),
        ]

        # Concepts CDB/biodiversité
        concepts_cdb = [
            ("ConceptCDB_InSituConservation",   "in-situ conservation",
             "conservation in situ",   "conservation of ecosystems and natural habitats (CBD Art. 8)."),
            ("ConceptCDB_EIES",                 "environmental impact assessment (EIA)",
             "évaluation d'impact environnemental", "procedure to assess environmental effects before project approval (CBD Art. 14)."),
            ("ConceptCDB_Biodiversity",         "biodiversity",
             "diversité biologique", "variability among living organisms from all sources (CBD Art. 2)."),
        ]

        all_concepts = concepts_icrw + concepts_marpol + concepts_cdb

        for local, en_label, fr_label, definition in all_concepts:
            uri = self.mar[local]
            self.g.add((uri, RDF.type, mar.ConceptLexical))
            self.g.add((uri, RDF.type, SKOS.Concept))
            self.g.add((uri, RDF.type, OWL.NamedIndividual))
            self.g.add((uri, SKOS.prefLabel, Literal(en_label, lang="en")))
            self.g.add((uri, SKOS.prefLabel, Literal(fr_label, lang="fr")))
            self.g.add((uri, SKOS.definition, Literal(definition, lang="en")))
            self.g.add((uri, SKOS.inScheme, mar.GlossairePeche))

        # Intégrer les définitions chargées depuis les fichiers JSON
        if definitions:
            n_added = 0
            for entry in definitions[:200]:  # limite raisonnable
                term = entry.get("term") or entry.get("terme")
                definition = entry.get("definition")
                if not term or not definition:
                    continue
                local = "Concept_" + slugify(term)[:60]
                uri = self.mar[local]
                if (uri, RDF.type, OWL.NamedIndividual) not in self.g:
                    self.g.add((uri, RDF.type, mar.ConceptLexical))
                    self.g.add((uri, RDF.type, SKOS.Concept))
                    self.g.add((uri, RDF.type, OWL.NamedIndividual))
                    self.g.add((uri, SKOS.prefLabel, Literal(term, lang="fr")))
                    self.g.add((uri, SKOS.definition, Literal(definition, lang="fr")))
                    self.g.add((uri, SKOS.inScheme, mar.GlossairePeche))
                    # AJOUT DES SYNONYMES (skos:altLabel)
                    for syn in entry.get("synonyms", []):
                        self.g.add((uri, SKOS.altLabel, Literal(syn, lang="fr")))

                    # AJOUT DES HYPERONYMES (skos:broader)
                    for hyp in entry.get("hyperonyms", []):
                        hyp_local = "Concept_" + slugify(hyp)[:60]
                        hyp_uri = self.mar[hyp_local]
                        # Créer le nœud hyperonyme s'il n'existe pas
                        if (hyp_uri, RDF.type, OWL.NamedIndividual) not in self.g:
                            self.g.add((hyp_uri, RDF.type, mar.ConceptLexical))
                            self.g.add((hyp_uri, RDF.type, SKOS.Concept))
                            self.g.add((hyp_uri, RDF.type, OWL.NamedIndividual))
                            self.g.add((hyp_uri, SKOS.prefLabel, Literal(hyp, lang="fr")))
                            self.g.add((hyp_uri, SKOS.inScheme, mar.GlossairePeche))
                        
                        # Relation hiérarchique
                        self.g.add((uri, SKOS.broader, hyp_uri))

                    # Lier le concept à l'interdiction
                    iid = entry.get("interdiction_id")
                    if iid:
                        iid_uri = self.mar[iid]
                        if (iid_uri, RDF.type, OWL.NamedIndividual) in self.g:
                            self.g.add((iid_uri, mar.hasConcept, uri))

                    n_added += 1
            logger.info("    ✅ %d concepts depuis les fichiers JSON ajoutés", n_added)

        logger.info("    ✅ %d concepts SKOS en total", len(all_concepts))

    # ══════════════════════════════════════════════════════════════
    # 7. DEFINITIONS RETENUES (Definitions_retenues/*.json)
    # ══════════════════════════════════════════════════════════════
    def populate_definitions(self, definitions_by_iid: dict):
        """
        Injecte les définitions retenues comme skos:Concept dans l'ontologie.

        Crée un skos:ConceptScheme par interdiction, puis un skos:Concept
        par définition avec :
          - skos:prefLabel  (terme)
          - skos:definition (texte complet)
          - mar:sourceArticle (référence article si disponible)
          - mar:nomScientifique (si disponible)
          - skos:inScheme → le ConceptScheme de l'interdiction
          - skos:broader → mar:GlossairePeche (schéma global)
        """
        if not definitions_by_iid:
            logger.info("  📖 Aucune définition retenue à charger")
            return

        logger.info("  📖 Population des définitions retenues...")
        mar = self.mar

        # Labels des ConceptSchemes par interdiction
        scheme_labels = {
            "I001": ("Glossaire — Chalutage de fond",
                     "Glossary — Bottom Trawling"),
            "I002": ("Glossaire — Chasse à la baleine (ICRW)",
                     "Glossary — Whaling (ICRW)"),
            "I003": ("Glossaire — Construction littorale",
                     "Glossary — Coastal Construction"),
            "I004": ("Glossaire — Extraction de sable (CDB)",
                     "Glossary — Sand Extraction (CBD)"),
            "I005": ("Glossaire — Oiseaux marins (CMS)",
                     "Glossary — Migratory Seabirds (CMS)"),
            "I006": ("Glossaire — Rejets d'hydrocarbures (MARPOL)",
                     "Glossary — Oil Discharge (MARPOL)"),
        }

        total_defs = 0
        seen_terms = set()

        for iid, defs_list in definitions_by_iid.items():
            if not defs_list:
                continue

            # Créer le ConceptScheme pour cette interdiction
            scheme_local = f"Glossaire_{iid}"
            scheme_uri = mar[scheme_local]
            self.g.add((scheme_uri, RDF.type, self.skos.ConceptScheme))
            self.g.add((scheme_uri, RDF.type, OWL.NamedIndividual))
            fr_lab, en_lab = scheme_labels.get(iid,
                (f"Glossaire — {iid}", f"Glossary — {iid}"))
            self.g.add((scheme_uri, RDFS.label, Literal(fr_lab, lang="fr")))
            self.g.add((scheme_uri, RDFS.label, Literal(en_lab, lang="en")))
            # Lier au glossaire global comme top-scheme
            self.g.add((scheme_uri, self.skos.broader, mar.GlossairePeche))

            for entry in defs_list:
                term = entry["term"]
                defn = entry["definition"]
                lang = entry.get("language", "fr")

                # Dédoublonner par terme normalisé
                term_key = (slugify(term), iid)
                if term_key in seen_terms:
                    continue
                seen_terms.add(term_key)

                # Créer le concept avec le préfixe unifié
                local_id = f"Concept_{slugify(term)[:50]}"
                uri = mar[local_id]

                if (uri, RDF.type, OWL.NamedIndividual) not in self.g:
                    self.g.add((uri, RDF.type, mar.ConceptLexical))
                    self.g.add((uri, RDF.type, self.skos.Concept))
                    self.g.add((uri, RDF.type, OWL.NamedIndividual))
                    self.g.add((uri, self.skos.prefLabel, Literal(term, lang=lang)))
                    self.g.add((uri, self.skos.definition, Literal(defn, lang=lang)))
                    self.g.add((uri, self.skos.inScheme, scheme_uri))
                    
                    # LIEN CRUCIAL : Relier l'interdiction au concept
                    iid_uri = mar[iid]
                    if (iid_uri, RDF.type, OWL.NamedIndividual) in self.g:
                        self.g.add((iid_uri, mar.hasConcept, uri))
                    
                    total_defs += 1

                # Métadonnées optionnelles
                art_ref = entry.get("article_reference")
                if art_ref:
                    self._data(uri, mar.sourceArticle, str(art_ref), XSD.string)

                sci_name = entry.get("scientific_name")
                if sci_name:
                    self._data(uri, mar.nomScientifique, sci_name, XSD.string)

                doc_title = entry.get("document_title")
                if doc_title:
                    self.g.add((uri, self.skos.note,
                                Literal(f"Source : {doc_title}", lang="fr")))



            logger.info(f"    ✅ {iid}: {len(defs_list)} définitions → {scheme_local}")

        logger.info(f"  ✅ {total_defs} définitions retenues injectées au total")

    # ══════════════════════════════════════════════════════════════
    # ENTRY POINT
    # ══════════════════════════════════════════════════════════════
    def populate_all(self, data: Optional[Dict[str, Any]] = None, definitions_retenues: Optional[Dict[str, Any]] = None):
        """Population complète de l'ontologie."""
        data = data or {}
        self.populate_zones()
        self.populate_acteurs()
        self.populate_sources_juridiques()
        self.populate_species()
        self.populate_interdictions()
        self.populate_exception_consequences()
        self.populate_lexical_layer(
            definitions=data.get("definitions", []),
            glossary=data.get("glossary", [])
        )
        # Définitions retenues depuis Definitions_retenues/
        if definitions_retenues:
            self.populate_definitions(definitions_retenues)
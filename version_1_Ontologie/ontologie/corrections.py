"""
corrections.py — Post-traitement pour corriger et enrichir l'ontologie.

Applique toutes les corrections manuelles identifiées :
  1. Corriger les références mortes aux individus
  2. Corriger les fautes de frappe dans les URIs
  3. Enrichir les sources juridiques (sourceYear + skos:definition)
  4. Corriger la définition tronquée de Concept_Factory_Ship_Operations
  5. Ajouter rdfs:range à soumisA
  6. Ajouter Permission individuals pour les exceptions
  7. Ajouter skos:inScheme aux espèces marines
"""

import logging
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD
from rdflib.namespace import SKOS

logger = logging.getLogger(__name__)

NS_MAR = "http://www.maritime-ontology.org/mar#"
NS_LKIF = "http://www.estrellaproject.org/lkif-core/lkif-core.owl#"


class OntologyCorrections:
    """Post-traitement des corrections ontologiques."""
    
    def __init__(self, g: Graph, mar: Namespace, lkif: Namespace):
        self.g = g
        self.mar = mar
        self.lkif = lkif
    
    def apply_all_corrections(self):
        """Applique toutes les corrections dans l'ordre."""
        logger.info("\n🔧 CORRECTIONS POST-TRAITEMENT")
        
        self._fix_uri_typos()
        self._enrich_legal_sources()
        self._fix_truncated_definitions()
        self._add_range_to_soumis_a()
        self._add_permission_individuals()
        self._add_skos_in_scheme_to_species()
        self._fix_dead_references()
        self._separate_activity_and_stock_concerns()
        self._remove_redundant_concept_individuals()
        self._fix_malformed_uris()
        
        logger.info("✅ Toutes les corrections appliquées")
    
    # ──────────────────────────────────────────────────────────────
    # CORRECTION 1 : Typos URI
    # ──────────────────────────────────────────────────────────────
    def _fix_uri_typos(self):
        """Corrige les fautes de frappe dans les URIs."""
        logger.info("  [1/10] Correction des typos URI...")
        
        typo_fixes = [
            ("BaeleineSeI", "BaleineSei"),
            ("BaeleineBreyde", "BaleineDeBryde"),
            ("BaeleineMinke", "BaleineMinke"),
            ("chalut_buf_de_fond", "chalut_boeuf_de_fond"),
        ]
        
        for typo, correct in typo_fixes:
            self._replace_uri_references(typo, correct)
    
    def _replace_uri_references(self, old_uri_part: str, new_uri_part: str):
        """Remplace toutes les références à un URI typo."""
        old_uri = URIRef(f"{NS_MAR}{old_uri_part}")
        new_uri = URIRef(f"{NS_MAR}{new_uri_part}")
        
        # Remplacer en tant que sujet
        for p, o in list(self.g.predicate_objects(old_uri)):
            self.g.remove((old_uri, p, o))
            self.g.add((new_uri, p, o))
        
        # Remplacer en tant qu'objet
        for s, p in list(self.g.subject_predicates(old_uri)):
            self.g.remove((s, p, old_uri))
            self.g.add((s, p, new_uri))
        
        logger.info(f"    ✓ {old_uri_part} → {new_uri_part}")
    
    # ──────────────────────────────────────────────────────────────
    # CORRECTION 2 : Enrichir les sources juridiques
    # ──────────────────────────────────────────────────────────────
    def _enrich_legal_sources(self):
        """Enrichit les sources juridiques avec sourceYear et skos:definition."""
        logger.info("  [2/10] Enrichissement des sources juridiques...")
        
        sources = {
            "Res61_105": {
                "year": 2006,
                "fr": "Résolution 61/105 de l'Assemblée générale des Nations unies sur les pêches durables en haute mer, adoptée en 2006.",
                "en": "UN General Assembly Resolution 61/105 on sustainable fishing on the high seas, adopted in 2006.",
            },
            "Res64_72": {
                "year": 2009,
                "fr": "Résolution 64/72 de l'Assemblée générale des Nations unies concernant les océans et le droit de la mer.",
                "en": "UN General Assembly Resolution 64/72 on oceans and law of the sea.",
            },
            "Res66_68": {
                "year": 2011,
                "fr": "Résolution 66/68 de l'Assemblée générale des Nations unies sur les océans et le droit de la mer.",
                "en": "UN General Assembly Resolution 66/68 on oceans and law of the sea.",
            },
            "Res71_123": {
                "year": 2016,
                "fr": "Résolution 71/123 de l'Assemblée générale des Nations unies sur les océans et le droit de la mer.",
                "en": "UN General Assembly Resolution 71/123 on oceans and law of the sea.",
            },
            "ICRW_Convention": {
                "year": 1946,
                "fr": "Convention internationale pour la réglementation de la pêche à la baleine, signée en 1946.",
                "en": "International Convention for the Regulation of Whaling (ICRW), signed in 1946.",
            },
            "IWC_Schedule": {
                "year": 1946,
                "fr": "Protocole annexé à la Convention internationale pour la réglementation de la pêche à la baleine.",
                "en": "Schedule annexed to the International Convention for the Regulation of Whaling.",
            },
        }
        
        for source_id, data in sources.items():
            source_uri = self.mar[source_id]
            
            # Ajouter sourceYear
            self.g.add((source_uri, self.mar.sourceYear, 
                       Literal(data["year"], datatype=XSD.integer)))
            
            # Supprimer les définitions existantes (évite les doublons)
            for o in list(self.g.objects(source_uri, SKOS.definition)):
                self.g.remove((source_uri, SKOS.definition, o))
                
            # Ajouter skos:definition bilingues
            self.g.add((source_uri, SKOS.definition,
                       Literal(data["fr"], lang="fr")))
            self.g.add((source_uri, SKOS.definition,
                       Literal(data["en"], lang="en")))
            
            logger.info(f"    ✓ {source_id} enrichie")
    
    # ──────────────────────────────────────────────────────────────
    # CORRECTION 3 : Définitions tronquées
    # ──────────────────────────────────────────────────────────────
    def _fix_truncated_definitions(self):
        """Corrige les définitions tronquées."""
        logger.info("  [3/10] Correction des définitions tronquées...")
        
        # Concept_Factory_Ship_Operations
        factory_uri = self.mar.Concept_Factory_Ship_Operations
        
        # Supprimer l'ancienne définition tronquée
        for o in list(self.g.objects(factory_uri, SKOS.definition)):
            self.g.remove((factory_uri, SKOS.definition, o))
        
        # Ajouter la définition correcte
        definition = (
            "Factory ship operations refer to whaling activity conducted aboard large processing vessels. "
            "These ships operate under the International Convention for the Regulation of Whaling (ICRW) and are "
            "subject to specific regulations regarding the species they may process, the areas where they operate, "
            "and catch limits imposed by the International Whaling Commission (IWC)."
        )
        self.g.add((factory_uri, SKOS.definition, Literal(definition, lang="en")))
        
        # CORRECTION 3: Concept_Factory_Ship_Operations — individu sans type
        self.g.add((factory_uri, RDF.type, self.mar.ConceptLexical))
        self.g.add((factory_uri, RDF.type, OWL.NamedIndividual))
        self.g.add((factory_uri, SKOS.inScheme, self.mar.GlossairePeche))
        
        logger.info(f"    ✓ Concept_Factory_Ship_Operations corrigée")
    
    # ──────────────────────────────────────────────────────────────
    # CORRECTION 4 : Ajouter rdfs:range à soumisA
    # ──────────────────────────────────────────────────────────────
    def _add_range_to_soumis_a(self):
        """Ajoute rdfs:range à la propriété soumisA."""
        logger.info("  [4/10] Ajout du rdfs:range à soumisA...")
        
        soumis_a = self.mar.soumisA
        
        # Ajouter rdfs:range (Thing - générique)
        self.g.add((soumis_a, RDFS.range, OWL.Thing))
        
        # Ajouter rdfs:comment pour clarifier l'usage
        comment = Literal(
            "Propriété générique indiquant qu'un acteur est soumis à une norme juridique. "
            "Préférer les propriétés plus spécifiques comme soumisAControle ou aException.",
            lang="fr"
        )
        self.g.add((soumis_a, RDFS.comment, comment))
        
        logger.info(f"    ✓ soumisA enrichie avec rdfs:range et rdfs:comment")
    
    # ──────────────────────────────────────────────────────────────
    # CORRECTION 5 : Ajouter Permission individuals
    # ──────────────────────────────────────────────────────────────
    def _add_permission_individuals(self):
        """Ajoute les Permission individuals pour les exceptions."""
        logger.info("  [5/10] Ajout des individus Permission...")
        
        permissions = [
            {
                "id": "Permission_ChasseScientiqueArticle8",
                "label_fr": "Permission : Chasse à des fins scientifiques (Article VIII ICRW)",
                "label_en": "Permission: Scientific Whaling (Article VIII ICRW)",
                "def_fr": "Permission explicite de procéder à la chasse à la baleine à des fins scientifiques, autorisée par l'Article VIII de la Convention internationale pour la réglementation de la pêche à la baleine (ICRW), sous permis scientifique national.",
                "def_en": "Explicit permission to conduct whaling for scientific purposes, authorized under Article VIII of the International Convention for the Regulation of Whaling (ICRW), by national scientific permit.",
                "comment_fr": "Cette permission déroge à l'interdiction I002 et est encadrée par les mécanismes de contrôle scientifique de la CBI.",
                "beneficiary": "Acteur_MembreIWC",
            },
            {
                "id": "Permission_ChasseSubsistanceAutochtone",
                "label_fr": "Permission : Chasse à des fins de subsistance autochtone",
                "label_en": "Permission: Aboriginal Subsistence Whaling",
                "def_fr": "Permission spéciale de chasse à la baleine accordée aux peuples autochtones et aux communautés côtières dont la subsistance dépend traditionnellement de cette pratique, encadrée par le Schedule de la ICRW.",
                "def_en": "Special permission for whaling granted to indigenous peoples and coastal communities whose traditional subsistence depends on this practice, as provided in the ICRW Schedule.",
                "comment_fr": "Cette permission déroge à l'interdiction I002 pour les communautés autochtones reconnues par la CBI.",
                "beneficiary": "Acteur_MembreIWC",
            },
        ]
        
        for perm_data in permissions:
            perm_uri = self.mar[perm_data["id"]]
            
            # Ajouter les types
            self.g.add((perm_uri, RDF.type, self.lkif.Permission))
            self.g.add((perm_uri, RDF.type, OWL.NamedIndividual))
            
            # Ajouter les labels
            self.g.add((perm_uri, RDFS.label, 
                       Literal(perm_data["label_fr"], lang="fr")))
            self.g.add((perm_uri, RDFS.label, 
                       Literal(perm_data["label_en"], lang="en")))
            
            # Supprimer les définitions existantes
            for o in list(self.g.objects(perm_uri, SKOS.definition)):
                self.g.remove((perm_uri, SKOS.definition, o))
                
            # Ajouter les définitions
            self.g.add((perm_uri, SKOS.definition,
                       Literal(perm_data["def_fr"], lang="fr")))
            self.g.add((perm_uri, SKOS.definition,
                       Literal(perm_data["def_en"], lang="en")))
            
            # Ajouter le commentaire
            self.g.add((perm_uri, RDFS.comment,
                       Literal(perm_data["comment_fr"], lang="fr")))
            
            # Ajouter la relation au bénéficiaire
            beneficiary = self.mar[perm_data["beneficiary"]]
            self.g.add((perm_uri, self.mar.beneficieA, beneficiary))
            
            logger.info(f"    ✓ {perm_data['id']} créée")
        
        # Créer les Controle individuals
        controls = [
            {
                "id": "Controle_ChasseScientiqueICRW",
                "label": "Contrôle de la chasse scientifique (ICRW)",
                "def": "Mécanisme de contrôle par la Commission baleinière internationale pour la gestion des permis de chasse scientifique.",
            },
            {
                "id": "Controle_QuotasSubsistanceAutochtone",
                "label": "Contrôle des quotas de subsistance autochtone",
                "def": "Mécanisme de contrôle par la Commission baleinière internationale pour la gestion des quotas de chasse autochtone.",
            },
        ]
        
        for ctrl_data in controls:
            ctrl_uri = self.mar[ctrl_data["id"]]
            self.g.add((ctrl_uri, RDF.type, self.mar.Controle))
            self.g.add((ctrl_uri, RDF.type, OWL.NamedIndividual))
            self.g.add((ctrl_uri, RDFS.label, Literal(ctrl_data["label"], lang="fr")))
            # Supprimer les définitions existantes
            for o in list(self.g.objects(ctrl_uri, SKOS.definition)):
                self.g.remove((ctrl_uri, SKOS.definition, o))
                
            self.g.add((ctrl_uri, SKOS.definition, Literal(ctrl_data["def"], lang="fr")))
            logger.info(f"    ✓ {ctrl_data['id']} créée")
        
        # Lier I002 aux Permission individuals via hasDerogation
        i002_uri = self.mar.I002
        self.g.add((i002_uri, self.mar.hasDerogation,
                   self.mar["Permission_ChasseScientiqueArticle8"]))
        self.g.add((i002_uri, self.mar.hasDerogation,
                   self.mar["Permission_ChasseSubsistanceAutochtone"]))
        logger.info(f"    ✓ I002 liée aux Permissions via hasDerogation")
    
    # ──────────────────────────────────────────────────────────────
    # CORRECTION 6 : Ajouter skos:inScheme aux espèces marines
    # ──────────────────────────────────────────────────────────────
    def _add_skos_in_scheme_to_species(self):
        """Ajoute skos:inScheme à toutes les espèces marines."""
        logger.info("  [6/10] Ajout de skos:inScheme aux espèces marines...")
        
        species = [
            "BaleineFranche", "BaleineBoreal", "BaleineGrise", "BaleineBleue",
            "BaleineFin", "BaleineBosse", "Cachalot", "BaleineSei",
            "BaleineDeBryde", "Orque", "BaleineABec", "Globicephale",
            "PetiteBaleineFranche", "BaleineMinke", "BaleineABecBottlenose"
        ]
        
        glossary_uri = self.mar.GlossairePeche
        
        for sp_name in species:
            species_uri = self.mar[f"Espece_{sp_name}"]
            
            # Ajouter skos:inScheme si l'espèce existe
            if (species_uri, RDF.type, self.mar.EspeceMarine) in self.g:
                # Vérifier que ce lien n'existe pas déjà
                if (species_uri, SKOS.inScheme, glossary_uri) not in self.g:
                    self.g.add((species_uri, SKOS.inScheme, glossary_uri))
        
        logger.info(f"    ✓ skos:inScheme ajoutée à {len(species)} espèces")
    
    # ──────────────────────────────────────────────────────────────
    # CORRECTION 7 : Corriger les références mortes
    # ──────────────────────────────────────────────────────────────
    def _fix_dead_references(self):
        """Corrige les références à des individus qui n'existent pas."""
        logger.info("  [7/10] Correction des références mortes...")
        
        replacements = [
            ("TypeDeNavire_NAVIRE_BATTANT_PAVILLON", "Acteur_EtatPavillon"),
            ("Navire_PAVILLON_NATIONAL", "Acteur_EtatPavillon"),
            ("Acteur_ORGANISME_REGIONAL_GESTION_PÊCHES", "Acteur_OrgRegionalPeche"),
            ("Periode_JusquaMiseEnPlaceEvaluationsMesures", "Periode_Jusqu-mesures-conservation"),
            ("Periode_DEPUIS_1986_SANS_LIMITE_FIXE", "Periode_Moratoire1986"),
        ]
        
        for dead_ref, replacement in replacements:
            dead_uri = self.mar[dead_ref]
            new_uri = self.mar[replacement]
            
            # Remplacer toutes les références
            self._replace_uri_references(dead_ref, replacement)
            logger.info(f"    ✓ {dead_ref} → {replacement}")
    
    # ──────────────────────────────────────────────────────────────
    # CORRECTION 8 : Séparer concerneActivite et concerneStock
    # ──────────────────────────────────────────────────────────────
    def _separate_activity_and_stock_concerns(self):
        """Sépare les activités des stocks : concerneActivite → Activite, concerneStock → Stock."""
        logger.info("  [7.5/10] Séparation concerneActivite/concerneStock...")
        
        # URIs pour identification
        CONCERNEACTIVITE = URIRef(NS_MAR + "concerneActivite")
        CONCERNESTOCK = URIRef(NS_MAR + "concerneStock")
        STOCK_TOUS = self.mar.Stock_TOUS_LES_STOCKS
        
        # Les individus qui ne sont PAS des activités
        non_activity_individuals = [
            "Espece_BALENE_ET_CACHALO",
            "Stock_TOUT_STOCKS_BALENE"
        ]
        
        removed_count = 0
        added_stock_count = 0
        
        # Parcourir tous les triplets concerneActivite
        triples_to_check = list(self.g.triples((None, CONCERNEACTIVITE, None)))
        
        for subject, predicate, obj in triples_to_check:
            obj_str = str(obj).split('#')[-1]  # Extraire le nom local
            
            # Si c'est un non-activité, le retirer et ajouter concerneStock
            for non_act in non_activity_individuals:
                if non_act in obj_str or obj_str == non_act:
                    # Retirer le triplet incorrect
                    self.g.remove((subject, predicate, obj))
                    removed_count += 1
                    
                    # Ajouter une liaison concerneStock → Stock_TOUS_LES_STOCKS
                    self.g.add((subject, CONCERNESTOCK, STOCK_TOUS))
                    added_stock_count += 1
                    
                    logger.info(f"    ✓ Retirée liaison incorrecte : {obj_str} de concerneActivite")
                    break
        
        if removed_count > 0 or added_stock_count > 0:
            logger.info(f"    ✓ {removed_count} liaisons concerneActivite incorrectes retirées")
            logger.info(f"    ✓ {added_stock_count} liaisons concerneStock ajoutées")
    
    # ──────────────────────────────────────────────────────────────
    # CORRECTION 9 : Supprimer les Concept_* redondants
    # ──────────────────────────────────────────────────────────────
    def _remove_redundant_concept_individuals(self):
        """Supprime les Concept_* redondants (remplacés par Espece_*)."""
        logger.info("  [9/10] Suppression des Concept_* redondants...")
        
        # Liste des Concept_ qui sont redondants (doublons des Espece_)
        redundant_concepts = [
            "Concept_beaked_whale",
            "Concept_pilot_whale", 
            "Concept_pygmy_right_whale",
            "Concept_Brydes_whale",
            "Concept_gray_whale",
            "Concept_bottlenose_whale",
            "Concept_killer_whale",
            "Concept_blue_whale",
            "Concept_fin_whale",
            "Concept_right_whale",
            "Concept_humpback_whale",
            "Concept_sei_whale",
            "Concept_sperm_whale",
        ]
        
        removed_count = 0
        for concept_id in redundant_concepts:
            concept_uri = self.mar[concept_id]
            
            # Supprimer tous les triplets associés à ce concept
            triples_to_remove = list(self.g.triples((concept_uri, None, None)))
            for triple in triples_to_remove:
                self.g.remove(triple)
            
            # Supprimer aussi les triplets où ce concept est objet
            triples_to_remove = list(self.g.triples((None, None, concept_uri)))
            for triple in triples_to_remove:
                self.g.remove(triple)
            
            removed_count += 1
        
        logger.info(f"    ✓ {removed_count} Concept_* redondants supprimés")
    
    # ──────────────────────────────────────────────────────────────
    # CORRECTION 9 : Corriger les URIs mal formées
    # ──────────────────────────────────────────────────────────────
    def _fix_malformed_uris(self):
        """Corrige les URIs mal formées (e.g., mar#w3.org → http://www.w3.org)."""
        logger.info("  [10/10] Correction des URIs mal formées...")
        
        # Chercher les URIs qui contiennent du namespace mal formé
        malformed_uris = []
        for s, p, o in list(self.g.triples((None, None, None))):
            # Vérifier les URIs en tant qu'objets
            if isinstance(o, URIRef):
                uri_str = str(o)
                # Vérifier si c'est une URI mal formée comme mar#w3.org
                if "mar#w3.org" in uri_str or "mar#http" in uri_str:
                    malformed_uris.append((s, p, o, uri_str))
        
        for s, p, o, uri_str in malformed_uris:
            # Corriger mar#w3.org → http://www.w3.org
            if "mar#w3.org" in uri_str:
                correct_uri = URIRef(uri_str.replace("mar#", ""))
                self.g.remove((s, p, o))
                self.g.add((s, p, correct_uri))
                logger.info(f"    ✓ Corrigée : {uri_str} → {correct_uri}")
            
            # Corriger mar#http → http
            elif "mar#http" in uri_str:
                correct_uri = URIRef(uri_str.replace("mar#", ""))
                self.g.remove((s, p, o))
                self.g.add((s, p, correct_uri))
                logger.info(f"    ✓ Corrigée : {uri_str} → {correct_uri}")
        
        if not malformed_uris:
            logger.info(f"    ✓ Aucune URI mal formée détectée")
    
    # ──────────────────────────────────────────────────────────────
    # CORRECTION 10 : Vérifier l'intégrité des blocs XML
    # ──────────────────────────────────────────────────────────────
    def _check_xml_integrity(self):
        """Vérifie l'intégrité des blocs RDF/XML (pas de triplets orphelins)."""
        logger.info("  [10/10] Vérification de l'intégrité XML...")
        
        # Dans RDFLib, les triplets orphelins n'existent pas - tous les triplets
        # sont automatiquement liés à une description. Cette vérification est ici
        # pour la cohérence mais ne supprimera rien dans RDFLib.
        
        total_triples = len(self.g)
        logger.info(f"    ✓ Total de triplets : {total_triples} (tous intégrés)")

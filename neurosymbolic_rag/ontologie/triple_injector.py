"""
triple_injector.py — Phase 1 & 2 de l'audit ontologique.

Injecte les pipeline_triples extraits par Mistral comme de VRAIS
triplets RDF dans le graphe, au lieu de les stocker en texte plat.

Phase 1 : Chaque triplet {subject, predicate, object} → arc RDF réel
Phase 2 : Les entités extraites sont typées (Zone, Acteur, etc.)
          au lieu d'être des ConceptLexical flottants
Phase 3 : Matérialisation des inférences clés pour Neo4j
Phase 4 : Liaison des définitions retenues au graphe
"""

import logging
import re
import unicodedata
from typing import Dict, List, Any, Optional

from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD
from rdflib.namespace import SKOS

logger = logging.getLogger(__name__)

NS_MAR = "http://www.maritime-ontology.org/mar#"
NS_LKIF = "http://www.estrellaproject.org/lkif-core/lkif-core.owl#"

# Seuil de confiance pour réduire le bruit (triplets Mistral)
CONFIDENCE_THRESHOLD = 0.8

# ══════════════════════════════════════════════════════════════
# MAPPING : catégorie Mistral → classe OWL
# ══════════════════════════════════════════════════════════════
CATEGORY_TO_OWL_CLASS = {
    "Activity":   "Activite",
    "Zone":       "Zone",
    "Actor":      "Acteur",
    "Acteur":     "Acteur",
    "Sanction":   "Sanction",
    "Controle":   "Controle",
    "Exception":  "ExceptionJuridique",
    "Espece":     "EspeceMarine",
    "Periode":    "Periode",
    "Etat":       "EtatSouverain",
    "Stock":      "Stock",
}

# MAPPING : nom de prédicat brut → propriété OWL réelle
PREDICATE_MAP = {
    "mar:appliesInZone":     "appliesInZone",
    "mar:concerneActivite":  "concerneActivite",
    "mar:concerneActeur":    "concerneActeur",
    "mar:entraineSanction":  "entraineSanction",
    "mar:soumisA":           "soumisAControle",
    "mar:soumisAControle":   "soumisAControle",
    "mar:appliesDuring":     "appliesDuring",
    "mar:admetException":    "aException",
    "mar:aException":        "aException",
    "mar:fondeeSur":         "fondeeSur",
    "mar:protegeEspece":     "protegeEspece",
    "mar:concerneStock":     "concerneStock",
    "mar:hasDerogation":     "hasDerogation",
    "mar:hasConcept":        "hasConcept",
}

# Normalisation forcée des Zones pour éviter les doublons
ZONE_MAPPING = {
    # HAUTE MER (HM)
    "haute_mer": "HM",
    "high_seas": "HM",
    "the_high_seas": "HM",
    "en_dehors_des_limites_de_la_juridiction_nationale": "HM",
    "au_dela_de_la_juridiction_nationale": "HM",
    "zones_situees_au_dela_de_la_juridiction_nationale": "HM",
    "zones_ne_relevant_pas_de_la_juridiction_nationale": "HM",
    "beyond_national_jurisdiction": "HM",
    "area_beyond_national_jurisdiction": "HM",
    
    # ZEE (EEZ)
    "zee": "EEZ",
    "eez": "EEZ",
    "zone_economique_exclusive": "EEZ",
    "exclusive_economic_zone": "EEZ",
    "zones_economiques_exclusives": "EEZ",
    "dans_les_limites_de_la_juridiction_nationale": "EEZ",
    
    # MER TERRITORIALE (MT)
    "mer_territoriale": "MT",
    "territorial_sea": "MT",
    "eaux_territoriales": "MT",
    "territorial_waters": "MT",
    
    # ZONE CONTIGUE (ZC)
    "zone_contigue": "ZC",
    "contiguous_zone": "ZC",
}


def _slugify(value: str) -> str:
    """Nettoie une chaîne pour en faire un identifiant IRI valide."""
    # Normalisation NFKD pour décomposer les caractères accentués
    clean = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    # Garder uniquement Alphanumérique et Underscore
    clean = re.sub(r"[^A-Za-z0-9_]+", "_", clean)
    # Supprimer les underscores multiples et aux extrémités
    clean = re.sub(r"_+", "_", clean).strip("_")
    # S'assurer que ça ne commence pas par un chiffre (optionnel mais recommandé pour les classes)
    if clean and clean[0].isdigit():
        clean = "v" + clean
    return clean[:80] or "Unknown"


def _resolve_predicate(raw_pred: str) -> Optional[str]:
    """Résout un prédicat brut vers le nom local de la propriété OWL."""
    # Essai direct
    if raw_pred in PREDICATE_MAP:
        return PREDICATE_MAP[raw_pred]
    # Sans préfixe
    clean = raw_pred.replace("mar:", "")
    for key, val in PREDICATE_MAP.items():
        if clean == key.replace("mar:", ""):
            return val
    # Fallback : utiliser le nom tel quel s'il est dans le namespace
    return clean if clean else None


def _resolve_owl_class(category: str, mar: Namespace) -> URIRef:
    """Résout une catégorie Mistral en classe OWL."""
    # Slugifier la catégorie pour éviter les espaces dans l'URI
    local = CATEGORY_TO_OWL_CLASS.get(category, "Activite")
    return mar[_slugify(local)]


class TripleInjector:
    """Injecte les triplets extraits comme de vraies relations RDF."""

    def __init__(self, g: Graph, mar: Namespace, lkif: Namespace):
        self.g = g
        self.mar = mar
        self.lkif = lkif
        self._created_individuals = set()
        self._stats = {
            "triples_injected": 0,
            "individuals_created": 0,
            "entities_typed": 0,
            "definitions_linked": 0,
            "inferences_materialized": 0,
        }

    # ══════════════════════════════════════════════════════════════
    # PHASE 1 : Injecter les pipeline_triples comme vrais arcs RDF
    # ══════════════════════════════════════════════════════════════
    def inject_triples(self, triples: List[dict]):
        """
        Transforme chaque triplet extrait en vrai arc RDF.

        Chaque triplet a la forme :
        {
            "subject": "I001",
            "predicate": "mar:appliesInZone",
            "object": "mar:Zone_HAUTE_MER",
            "concept_id": "Zone",
            "confidence": 0.99,
            "interdiction_id": "I001"
        }
        """
        if not triples:
            logger.info("  ℹ️  Aucun triplet à injecter")
            return

        logger.info(f"  🔗 Phase 1 : Injection de {len(triples)} triplets extraits...")

        for t in triples:
            subject_raw = t.get("subject", "")
            predicate_raw = t.get("predicate", "")
            object_raw = t.get("object", "")
            category = t.get("concept_id", "")
            confidence = float(t.get("confidence", 0.5))

            # FILTRE DE BRUIT : Ne garder que l'essentiel à haute confiance
            if confidence < CONFIDENCE_THRESHOLD:
                continue

            if not subject_raw or not predicate_raw or not object_raw:
                continue

            # Résoudre le sujet (toujours une interdiction)
            subject_uri = self._resolve_subject(subject_raw)
            if not subject_uri:
                continue

            # Résoudre le prédicat : Forcer le bon prédicat selon la catégorie
            # (Corrige les hallucinations de Mistral qui utilise concerneActivite pour des espèces)
            forced_pred_uri = self._category_to_predicate(category)
            if forced_pred_uri:
                predicate_uri = forced_pred_uri
            else:
                pred_local = _resolve_predicate(predicate_raw)
                if not pred_local:
                    continue
                predicate_uri = self.mar[pred_local]

            # Résoudre ou créer l'objet (Phase 2 intégrée)
            object_uri = self._resolve_or_create_object(
                object_raw, category, confidence
            )
            if not object_uri:
                continue

            # --- FILTRE DE COHÉRENCE JURIDIQUE ---
            # Éviter de lier I003 (Construction) ou I004 (Sable) à la Haute Mer (HM)
            obj_local = str(object_uri).replace(NS_MAR, "")
            if obj_local == "HM" and subject_raw in ["I003", "I004"]:
                logger.warning(f"  🚫 Filtrage relation absurde : {subject_raw} en Haute Mer")
                continue

            # Injecter le triplet RDF réel
            if (subject_uri, predicate_uri, object_uri) not in self.g:
                self.g.add((subject_uri, predicate_uri, object_uri))
                self._stats["triples_injected"] += 1

        logger.info(
            f"  ✅ Phase 1 terminée : {self._stats['triples_injected']} triplets injectés, "
            f"{self._stats['individuals_created']} individus créés"
        )

    def _resolve_subject(self, raw: str) -> Optional[URIRef]:
        """Résout le sujet — c'est toujours une interdiction (I001-I006)."""
        clean = _slugify(raw.replace("mar:", "").strip())
        uri = self.mar[clean]
        # Vérifier que l'individu existe
        if (uri, RDF.type, OWL.NamedIndividual) in self.g:
            return uri
        # Vérifier par pattern I00x
        if re.match(r"I\d{3}", clean):
            return uri
        return None

    def _resolve_or_create_object(self, raw: str, category: str,
                                   confidence: float) -> Optional[URIRef]:
        """
        Phase 2 : Résout un objet existant OU crée un nouvel individu
        correctement typé (pas un ConceptLexical).
        """
        # Nettoyer et slugifier
        clean = _slugify(raw.replace("mar:", "").strip())
        
        # NORMALISATION DES ZONES (Dédoublonage forcé)
        if category == "Zone" and clean.lower() in ZONE_MAPPING:
            clean = ZONE_MAPPING[clean.lower()]
            
        uri = self.mar[clean]

        # RECHERCHE PAR LABEL (Dédoublonage agressif)
        # Si un individu de la même classe a un label quasi identique, on fusionne
        label_norm = raw.strip().lower()
        for ind, _, lab in self.g.triples((None, RDFS.label, None)):
            if str(lab).lower() == label_norm:
                # Vérifier que le sujet est bien une URIRef pour respecter le type de retour
                if isinstance(ind, URIRef):
                    return ind

        # Sinon, créer un nouvel individu TYPÉ
        if clean in self._created_individuals:
            return uri

        # Déterminer la classe OWL appropriée
        owl_class = _resolve_owl_class(category, self.mar)
        
        # Créer l'individu avec le bon type
        self.g.add((uri, RDF.type, owl_class))
        self.g.add((uri, RDF.type, OWL.NamedIndividual))
        
        # Label lisible
        label = raw.strip()
        # Nettoyer les préfixes de catégorie
        for prefix in ["Zone ", "Acteur ", "Activite ", "Sanction ",
                        "Controle ", "Exception ", "Espece ", "Stock ",
                        "Etat ", "Periode "]:
            if label.startswith(prefix):
                label = label[len(prefix):]
                break
        self.g.add((uri, RDFS.label, Literal(label, lang="fr")))

        # Score de confiance
        if confidence:
            self.g.add((uri, self.mar.confidence,
                        Literal(confidence, datatype=XSD.decimal)))

        self._created_individuals.add(clean)
        self._stats["individuals_created"] += 1
        self._stats["entities_typed"] += 1

        return uri

    # ══════════════════════════════════════════════════════════════
    # PHASE 2 : Typer les entités extraites (entites_trouvees)
    # ══════════════════════════════════════════════════════════════
    def type_extracted_entities(self, raw_by_file: Dict[str, Any]):
        """
        Pour chaque entité dans raw_extractions.entites_trouvees,
        crée un individu OWL correctement typé ET le relie à
        l'interdiction correspondante.
        """
        if not raw_by_file:
            return

        logger.info("  🏷️  Phase 2 : Typage des entités extraites...")
        count = 0

        for filename, data in raw_by_file.items():
            if not isinstance(data, dict):
                continue

            # Extraire l'ID d'interdiction
            iid = data.get("interdiction_id", "")
            if not iid:
                match = re.search(r"(I\d{3})", filename)
                iid = match.group(1) if match else ""

            if not iid:
                continue

            iid_uri = self.mar[iid]

            # Extractions brutes
            rx = data.get("raw_extractions", {})
            entities = rx.get("entites_trouvees", data.get("entites", []))

            for ent in entities:
                texte = ent.get("texte_original", "").strip()
                cat = ent.get("categorie", "").strip()

                if not texte or not cat:
                    continue

                # Créer un identifiant propre (Slugifier TOUTES les parties)
                local_id = f"{_slugify(cat)}_{_slugify(iid)}_{_slugify(texte)}"
                uri = self.mar[local_id]

                if (uri, RDF.type, OWL.NamedIndividual) in self.g:
                    continue

                # Typer correctement
                owl_class = _resolve_owl_class(cat, self.mar)
                self.g.add((uri, RDF.type, owl_class))
                self.g.add((uri, RDF.type, OWL.NamedIndividual))
                self.g.add((uri, RDFS.label, Literal(texte, lang="fr")))
                self.g.add((uri, SKOS.prefLabel, Literal(texte, lang="fr")))

                # Relier à l'interdiction avec le bon prédicat
                pred = self._category_to_predicate(cat)
                if pred:
                    self.g.add((iid_uri, pred, uri))
                    count += 1

        logger.info(f"  ✅ Phase 2 terminée : {count} entités typées et reliées")

    def _category_to_predicate(self, category: str) -> Optional[URIRef]:
        """Détermine le prédicat pour relier une entité à son interdiction."""
        mapping = {
            "Activity":  self.mar.concerneActivite,
            "Zone":      self.mar.appliesInZone,
            "Actor":     self.mar.concerneActeur,
            "Acteur":    self.mar.concerneActeur,
            "Sanction":  self.mar.entraineSanction,
            "Controle":  self.mar.soumisAControle,
            "Exception": self.mar.aException,
            "Espece":    self.mar.protegeEspece,
            "Etat":      self.mar.concerneActeur,
            "Stock":     self.mar.concerneStock,
            "Periode":   self.mar.appliesDuring,
        }
        return mapping.get(category)

    # ══════════════════════════════════════════════════════════════
    # PHASE 3 : Matérialiser les inférences pour Neo4j
    # ══════════════════════════════════════════════════════════════
    def materialize_inferences(self):
        """
        Pré-calcule les classes inférées que Neo4j ne peut pas déduire :
        - ZoneInterdite : toute Zone reliée à une Interdiction
        - ActiviteIllicite : toute Activité reliée à une Interdiction
        - ActeurEnInfraction : tout Acteur pratiquant une ActiviteIllicite
        - Résolution de la chaîne pratiqueActivite ∘ estActiviteDe → estSoumisA
        """
        logger.info("  ⚡ Phase 3 : Matérialisation des inférences...")
        mar = self.mar
        count = 0

        # 1. ZoneInterdite : Zone ⊓ ∃estZoneDe.Interdiction
        for s, p, o in self.g.triples((None, mar.appliesInZone, None)):
            if (s, RDF.type, mar.Interdiction) in self.g:
                if (o, RDF.type, mar.ZoneInterdite) not in self.g:
                    self.g.add((o, RDF.type, mar.ZoneInterdite))
                    count += 1

        # 2. ActiviteIllicite : Activité ⊓ ∃estActiviteDe.Interdiction
        for s, p, o in self.g.triples((None, mar.concerneActivite, None)):
            if (s, RDF.type, mar.Interdiction) in self.g:
                if (o, RDF.type, mar.ActiviteIllicite) not in self.g:
                    self.g.add((o, RDF.type, mar.ActiviteIllicite))
                    count += 1

        # 3. Résoudre la chaîne : pratiqueActivite ∘ estActiviteDe → estSoumisA
        #    Si un acteur pratique une activité qui est activité d'une interdiction,
        #    alors cet acteur est soumis à cette interdiction.
        for acteur, _, activite in self.g.triples((None, mar.pratiqueActivite, None)):
            for interdict, _, act2 in self.g.triples((None, mar.concerneActivite, None)):
                if act2 == activite and (interdict, RDF.type, mar.Interdiction) in self.g:
                    if (acteur, mar.estSoumisA, interdict) not in self.g:
                        self.g.add((acteur, mar.estSoumisA, interdict))
                        count += 1

        # 4. NormeInternationale : Norme ⊓ ∃fondeeSur.(Convention ⊔ Résolution)
        for norme, _, source in self.g.triples((None, mar.fondeeSur, None)):
            is_intl = ((source, RDF.type, mar.ConventionInternationale) in self.g or
                       (source, RDF.type, mar.ResolutionAGONU) in self.g)
            if is_intl:
                if (norme, RDF.type, mar.NormeInternationale) not in self.g:
                    self.g.add((norme, RDF.type, mar.NormeInternationale))
                    count += 1

        self._stats["inferences_materialized"] = count
        logger.info(f"  ✅ Phase 3 terminée : {count} inférences matérialisées")

    # ══════════════════════════════════════════════════════════════
    # PHASE 4 : Lier les définitions retenues au graphe
    # ══════════════════════════════════════════════════════════════
    def link_definitions(self, definitions_retenues: Dict[str, list]):
        """
        Pour chaque définition retenue déjà injectée comme skos:Concept,
        crée un lien mar:hasConcept entre l'interdiction et le concept.
        """
        if not definitions_retenues:
            return

        logger.info("  📎 Phase 4 : Liaison des définitions au graphe...")
        count = 0

        for iid, defs_list in definitions_retenues.items():
            if not defs_list:
                continue

            iid_uri = self.mar[iid]
            if (iid_uri, RDF.type, OWL.NamedIndividual) not in self.g:
                continue

            for entry in defs_list:
                term = entry.get("term", "")
                if not term:
                    continue

                # Retrouver l'URI du concept (format unifié : Concept_...)
                local_id = f"Concept_{_slugify(term)[:50]}"
                concept_uri = self.mar[local_id]

                if (concept_uri, RDF.type, OWL.NamedIndividual) in self.g:
                    # Lier l'interdiction au concept
                    if (iid_uri, self.mar.hasConcept, concept_uri) not in self.g:
                        self.g.add((iid_uri, self.mar.hasConcept, concept_uri))
                        count += 1

        self._stats["definitions_linked"] = count
        logger.info(f"  ✅ Phase 4 terminée : {count} définitions reliées aux interdictions")

    # ══════════════════════════════════════════════════════════════
    # POINT D'ENTRÉE UNIQUE
    # ══════════════════════════════════════════════════════════════
    def inject_all(self, data: dict):
        """
        Exécute l'injection simplifiée pour réduire le bruit.
        """
        logger.info("\n🔧 INJECTION QUALIFIÉE (Triplets + Définitions)")

        # Phase 1 : Triplets → arcs RDF (Filtrés par confiance dans inject_triples)
        self.inject_triples(data.get("triples", []))

        # Phase 2 désactivée pour réduire le bruit (entités déjà typées par le populator)
        # self.type_extracted_entities(data.get("raw_by_file", {}))

        # Phase 3 : Matérialisation des inférences (NÉCESSAIRE pour parité OWL ↔ Neo4j)
        self.materialize_inferences()

        # Phase 4 : Liaison des définitions au graphe
        self.link_definitions(data.get("definitions_retenues", {}))

        # Rapport
        logger.info("\n📊 RAPPORT D'INJECTION :")
        for key, val in self._stats.items():
            logger.info(f"  {key:30s} : {val}")
        logger.info("")

        return self._stats

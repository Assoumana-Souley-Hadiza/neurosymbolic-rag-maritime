"""
ontology_cleaner.py — Diagnostic et nettoyage complet de l'ontologie

Responsabilités :
1. Détecter les doublons (URIs différentes, labels similaires)
2. Créer un mapping canonique centralisé (source unique de vérité)
3. Corriger le pipeline pour éviter de créer des doublons
4. Valider la cohérence finaleRésultat : rapport diagnostic + fichier de correction
"""

import logging
import json
from pathlib import Path
from typing import Dict, Set, List, Tuple
from collections import defaultdict
import unicodedata
import re

from rdflib import Graph, Namespace, Literal, RDF, RDFS, OWL, URIRef
from rdflib.namespace import SKOS

logger = logging.getLogger(__name__)

NS_MAR = "http://www.maritime-ontology.org/mar#"


class OntologyDiagnostics:
    """Analyse les problèmes dans l'ontologie."""

    def __init__(self, g: Graph, mar: Namespace):
        self.g = g
        self.mar = mar
        self.issues = {
            "duplicated_individuals": [],
            "orphaned_individuals": [],
            "invalid_altlabels": [],
            "inconsistent_types": [],
            "broken_references": [],
        }
        self.canonical_mapping = {}

    def _normalize_label(self, label: str) -> str:
        """Normalise un label pour comparaison."""
        if not label:
            return ""
        # Minuscule + accents supprimés
        label = unicodedata.normalize('NFD', str(label)).encode('ascii', 'ignore').decode('utf-8')
        label = label.lower().strip()
        # Remplacer espaces/underscores par un seul espace
        label = re.sub(r'[\s_]+', ' ', label)
        return label

    def _similarity(self, s1: str, s2: str) -> float:
        """Calcule une similarité simple (Levenshtein-like)."""
        from difflib import SequenceMatcher
        norm1 = self._normalize_label(s1)
        norm2 = self._normalize_label(s2)
        if not norm1 or not norm2:
            return 0.0
        return SequenceMatcher(None, norm1, norm2).ratio()

    def find_duplicates(self) -> Dict[str, List[str]]:
        """
        Trouve les individuals avec des labels similaires mais des URIs différentes.
        Retourne un dict {canonical_label: [uri1, uri2, ...]}
        """
        label_to_uris = defaultdict(list)

        # Grouper par label normalisé
        for subj in self.g.subjects(RDF.type, OWL.NamedIndividual):
            labels = list(self.g.objects(subj, RDFS.label))
            if not labels:
                continue

            # Prendre le premier label FR
            label = None
            for lbl in labels:
                if lbl.language == 'fr' or lbl.language is None:
                    label = str(lbl)
                    break
            if not label:
                label = str(labels[0])

            norm_label = self._normalize_label(label)
            label_to_uris[norm_label].append(str(subj))

        # Garder seulement les groupes avec doublons
        duplicates = {norm: uris for norm, uris in label_to_uris.items() if len(uris) > 1}
        return duplicates

    def find_invalid_altlabels(self, max_per_individual: int = 5) -> List[Tuple[str, int]]:
        """
        Trouve les individuals avec trop d'altLabels (signe de bruit auto-généré).
        Retourne [(uri, count), ...]
        """
        invalid = []
        for subj in self.g.subjects(RDF.type, OWL.NamedIndividual):
            altlabels = list(self.g.objects(subj, SKOS.altLabel))
            if len(altlabels) > max_per_individual:
                invalid.append((str(subj), len(altlabels)))
        return sorted(invalid, key=lambda x: x[1], reverse=True)

    def find_orphaned_individuals(self) -> List[str]:
        """
        Trouve les individuals sans aucune relation (sauf type et label).
        """
        orphaned = []
        for subj in self.g.subjects(RDF.type, OWL.NamedIndividual):
            # Compter les relations autre que RDF.type, RDFS.label, RDFS.comment, etc.
            has_relation = False
            for p, o in self.g.predicate_objects(subj):
                if p not in (RDF.type, RDFS.label, RDFS.comment, SKOS.altLabel, SKOS.prefLabel, SKOS.definition):
                    has_relation = True
                    break
            if not has_relation:
                orphaned.append(str(subj))
        return orphaned

    def generate_canonical_mapping(self) -> Dict[str, str]:
        """
        Crée un mapping {non_canonical_uri: canonical_uri} pour tous les doublons.
        Règle : on garde l'URI la plus simple (la plus courte ou sans préfixe).
        """
        mapping = {}
        duplicates = self.find_duplicates()

        for norm_label, uris in duplicates.items():
            # Trier par longueur (la plus courte = la plus canonique)
            sorted_uris = sorted(uris, key=lambda u: len(u))
            canonical = sorted_uris[0]

            # Tous les autres pointent vers le canonical
            for uri in sorted_uris[1:]:
                mapping[uri] = canonical

            logger.info(f"  📌 Canonical mapping: {norm_label}")
            for uri in sorted_uris:
                marker = "✓" if uri == canonical else "→"
                logger.info(f"      {marker} {uri}")

        return mapping

    def generate_report(self) -> dict:
        """Génère un rapport complet de diagnostic."""
        report = {
            "timestamp": str(Path.cwd()),
            "duplicates": self.find_duplicates(),
            "orphaned_count": len(self.find_orphaned_individuals()),
            "invalid_altlabels_top10": self.find_invalid_altlabels()[:10],
            "canonical_mapping": self.generate_canonical_mapping(),
        }
        return report


class OntologyCanonicalizer:
    """Applique les corrections pour canonicaliser l'ontologie."""

    def __init__(self, g: Graph, mar: Namespace):
        self.g = g
        self.mar = mar
        self.stats = {
            "individuals_merged": 0,
            "altlabels_trimmed": 0,
            "orphans_removed": 0,
            "references_redirected": 0,
        }

    def merge_duplicates(self, mapping: Dict[str, str]):
        """
        Fusionne les individuals dupliqués.
        Pour chaque non_canonical_uri → canonical_uri :
        - Transférer toutes les relations
        - Supprimer le non-canonical
        """
        for non_canonical, canonical in mapping.items():
            nc_uri = URIRef(non_canonical)
            can_uri = URIRef(canonical)

            # Transférer où non_canonical est sujet
            for p, o in list(self.g.predicate_objects(nc_uri)):
                if p not in (RDF.type, RDFS.label, SKOS.altLabel, SKOS.prefLabel):
                    self.g.add((can_uri, p, o))
                self.g.remove((nc_uri, p, o))

            # Transférer où non_canonical est objet
            for s, p in list(self.g.subject_predicates(nc_uri)):
                self.g.add((s, p, can_uri))
                self.g.remove((s, p, nc_uri))
                self.stats["references_redirected"] += 1

            self.stats["individuals_merged"] += 1

    def trim_altlabels(self, max_per_individual: int = 5, min_similarity_to_prefLabel: float = 0.3):
        """
        Supprime les altLabels auto-générés (trop nombreux, peu similaires au prefLabel).
        Garde les altLabels vraiment pertinents.
        """
        for subj in self.g.subjects(RDF.type, OWL.NamedIndividual):
            prefLabels = list(self.g.objects(subj, SKOS.prefLabel))
            altLabels = list(self.g.objects(subj, SKOS.altLabel))

            if not prefLabels or len(altLabels) <= max_per_individual:
                continue

            # Garder seulement les altLabels qui ressemblent au prefLabel
            kept = []
            for alt in altLabels:
                alt_str = str(alt)
                for pref in prefLabels:
                    pref_str = str(pref)
                    # Calcul simplifié de similarité
                    if self._similarity(alt_str, pref_str) > min_similarity_to_prefLabel:
                        kept.append(alt)
                        break

            # Supprimer les autres
            for alt in altLabels:
                if alt not in kept:
                    self.g.remove((subj, SKOS.altLabel, alt))
                    self.stats["altlabels_trimmed"] += 1

    def _similarity(self, s1: str, s2: str) -> float:
        from difflib import SequenceMatcher
        return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()

    def remove_orphans(self):
        """Supprime les individuals orphelins."""
        orphans = []
        for subj in self.g.subjects(RDF.type, OWL.NamedIndividual):
            has_relation = False
            for p, o in self.g.predicate_objects(subj):
                if p not in (RDF.type, RDFS.label, RDFS.comment, SKOS.altLabel, SKOS.prefLabel, SKOS.definition):
                    has_relation = True
                    break
            if not has_relation:
                orphans.append(subj)

        for orphan in orphans:
            for p, o in list(self.g.predicate_objects(orphan)):
                self.g.remove((orphan, p, o))
            for s, p in list(self.g.subject_predicates(orphan)):
                self.g.remove((s, p, orphan))
            self.stats["orphans_removed"] += 1

    def run_all_corrections(self, mapping: Dict[str, str]):
        """Lance toutes les corrections."""
        logger.info("\n🧹 NETTOYAGE DE L'ONTOLOGIE")
        self.merge_duplicates(mapping)
        self.trim_altlabels()
        self.remove_orphans()
        logger.info(f"  ✅ {self.stats['individuals_merged']} individuals fusionnés")
        logger.info(f"  ✅ {self.stats['altlabels_trimmed']} altLabels supprimés")
        logger.info(f"  ✅ {self.stats['orphans_removed']} orphelins supprimés")
        return self.stats

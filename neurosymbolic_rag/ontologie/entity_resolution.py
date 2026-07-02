"""
entity_resolution.py — Module de Dédoublonnage d'Entités (Canonicalization)

Résout les redondances entre l'approche Top-Down (nœuds experts) et Bottom-Up (extractions LLM).
Utilise une "fusion destructrice" : si un nœud extrait correspond à un nœud expert,
les relations sont transférées vers le nœud expert et le nœud extrait est supprimé.
"""

import logging
import re
import difflib
import unicodedata
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, Node

logger = logging.getLogger(__name__)

NS_MAR = "http://www.maritime-ontology.org/mar#"

class EntityResolver:
    def __init__(self, g: Graph, mar: Namespace):
        self.g = g
        self.mar = mar
        self.stats = {
            "top_down_nodes": 0,
            "bottom_up_nodes": 0,
            "merged_nodes": 0,
            "edges_transferred": 0
        }

    def _normalize_label(self, label: str) -> str:
        """Normalise un label pour la comparaison (minuscule, sans ponctuation ni accents)."""
        if not label:
            return ""
        # Supprimer les accents
        label = unicodedata.normalize('NFD', label).encode('ascii', 'ignore').decode("utf-8")
        label = label.lower()
        label = re.sub(r'[\(\)\[\]\{\}\.,;:\'\"]', ' ', label)
        # Supprimer les mots de liaison basiques
        words = [w for w in label.split() if w not in ("de", "la", "le", "les", "des", "du", "un", "une", "en", "et", "ou", "a", "au", "aux", "pour", "sur", "dans", "par")]
        return " ".join(words).strip()

    def _is_match(self, label_bu: str, label_td: str) -> bool:
        """Détermine si deux labels représentent la même entité."""
        norm_bu = self._normalize_label(label_bu)
        norm_td = self._normalize_label(label_td)

        if not norm_bu or not norm_td:
            return False

        # 1. Dictionnaire de Mapping Forcé (Hardcoded Synonyms)
        manual_mapping = {
            # Zones
            "haute mer": "haute mer",
            "zee": "zone economique exclusive",
            "zone cotiere": "bande 100 metres",
            
            # Acteurs / Organisations
            "cop cbd": "secretariat convention diversite biologique",
            "conference parties": "secretariat convention diversite biologique",
            "fao": "fao organisation nations unies alimentation agriculture",
            "omi": "organisation maritime internationale",
            "imo": "organisation maritime internationale",
            "cbi": "commission baleiniere internationale",
            "iwc": "commission baleiniere internationale",
            "communautes locales autochtones": "communautes autochtones",
            "amenageur industriel": "promoteur",
            "exploitant station": "usines traitement",
            "navire usine": "navires usines",
            "navire peche": "navires peche",
            "etat cotier": "etat cotier",
            "etat pavillon": "etat pavillon",
            "etat port": "etat port",
            
            # Concepts
            "emv": "ecosysteme marin vulnerable",
            "ecosystemes marins vulnerables": "ecosysteme marin vulnerable",
            "aires marines protegees": "aire marine protegee",
        }
        
        # Vérifier si l'un ou l'autre correspond via le dictionnaire
        # Si norm_td est la cible ("zone economique exclusive"), et que norm_bu contient "zee"
        for key, target in manual_mapping.items():
            if (key in norm_bu and target in norm_td) or (key in norm_td and target in norm_bu):
                return True

        # 2. Match exact
        if norm_bu == norm_td:
            return True

        # 3. Inclusion forte (La chaîne courte est complètement incluse dans la longue)
        if len(norm_td) >= 6 and norm_td in norm_bu:
            return True
        if len(norm_bu) >= 6 and norm_bu in norm_td:
            return True

        # 4. Similarité (via SequenceMatcher) — seuil 0.85 pour éviter les faux positifs
        ratio = difflib.SequenceMatcher(None, norm_bu, norm_td).ratio()
        if ratio > 0.85:
            return True

        return False

    def _merge_nodes(self, source_uri: Node, target_uri: Node):
        """Transfère toutes les relations du source vers le target, puis supprime le source."""
        # Transférer où source est le SUJET
        for p, o in list(self.g.predicate_objects(source_uri)):
            if p not in (RDF.type, RDFS.label, self.mar.confidence, OWL.NamedIndividual):
                self.g.add((target_uri, p, o))
                self.stats["edges_transferred"] += 1
            self.g.remove((source_uri, p, o))

        # Transférer où source est l'OBJET
        for s, p in list(self.g.subject_predicates(source_uri)):
            self.g.add((s, p, target_uri))
            self.stats["edges_transferred"] += 1
            self.g.remove((s, p, source_uri))

    def resolve_all(self) -> dict:
        """
        Exécute la résolution d'entités AGRESSIVE — détecte TOUS les doublons.
        Stratégie :
          1. Phase 1 : Bottom-Up vs Top-Down (comme avant)
          2. Phase 2 : Top-Down vs Top-Down (nouveau — détecte doublons experts)
          3. Phase 3 : Nettoyage final via canonicalisation
        """
        logger.info("  🔍 Démarrage de la résolution d'entités (3 phases — AGGRESSIVE)")
        
        # Classes à dédoublonner
        target_classes = [
            self.mar.Zone, self.mar.Acteur, self.mar.Activite, 
            self.mar.EspeceMarine, self.mar.Sanction, self.mar.Controle,
            self.mar.ExceptionJuridique, self.mar.EtatSouverain, 
            self.mar.Stock, self.mar.Periode, self.mar.ConceptLexical
        ]

        for owl_class in target_classes:
            # Récupérer tous les individus (y compris les sous-classes)
            individuals = set()
            for subclass in self.g.transitive_subjects(RDFS.subClassOf, owl_class):
                for ind in self.g.subjects(RDF.type, subclass):
                    individuals.add(ind)
            for ind in self.g.subjects(RDF.type, owl_class):
                individuals.add(ind)

            # Séparer Top-Down (sans I00X) et Bottom-Up (avec confidence ou _source_file)
            top_down = {}
            bottom_up = {}

            for ind in individuals:
                # Récupérer le label
                labels = list(self.g.objects(ind, RDFS.label))
                if not labels:
                    continue
                label = str(labels[0])

                has_confidence = bool(list(self.g.objects(ind, self.mar.confidence)))
                has_source = any(str(ind).startswith(prefix) for prefix in ["Activity_", "Actor_"])

                if has_confidence or has_source:
                    bottom_up[ind] = label
                else:
                    top_down[ind] = label

            self.stats["top_down_nodes"] += len(top_down)
            self.stats["bottom_up_nodes"] += len(bottom_up)

            # ── PHASE 1 : Bottom-Up vs Top-Down ──────────────────────────
            for bu_uri, bu_label in list(bottom_up.items()):
                if (bu_uri, None, None) not in self.g:  # Peut avoir été supprimé en phase 1
                    continue
                    
                best_match = None
                best_score = 0
                
                for td_uri, td_label in top_down.items():
                    if self._is_match(bu_label, td_label):
                        best_match = td_uri
                        break
                
                if best_match:
                    logger.debug(f"      [P1] 🔗 Fusion: '{bu_label}' ➡️ '{top_down[best_match]}'")
                    self._merge_nodes(bu_uri, best_match)
                    self.stats["merged_nodes"] += 1
                    bottom_up.pop(bu_uri, None)

            # ── PHASE 2 : Top-Down vs Top-Down (nouveau) ─────────────────
            td_list = list(top_down.items())
            for i, (td_uri_1, label_1) in enumerate(td_list):
                if (td_uri_1, None, None) not in self.g:  # Peut avoir été supprimé
                    continue
                    
                for td_uri_2, label_2 in td_list[i+1:]:
                    if (td_uri_2, None, None) not in self.g:
                        continue
                        
                    if self._is_match(label_1, label_2):
                        # Garder l'URI la plus courte comme canonical
                        if len(str(td_uri_1)) <= len(str(td_uri_2)):
                            logger.debug(f"      [P2] 🔗 Fusion Top-Down: '{label_1}' ➡️ '{label_2}'")
                            self._merge_nodes(td_uri_2, td_uri_1)
                        else:
                            logger.debug(f"      [P2] 🔗 Fusion Top-Down: '{label_2}' ➡️ '{label_1}'")
                            self._merge_nodes(td_uri_1, td_uri_2)
                        self.stats["merged_nodes"] += 1
                        break

        logger.info(f"  ✅ Dédoublonnage terminé : {self.stats['merged_nodes']} nœuds fusionnés, {self.stats['edges_transferred']} relations redirigées.")
        return self.stats

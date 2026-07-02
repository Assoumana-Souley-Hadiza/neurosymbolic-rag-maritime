"""
pipeline.py v2 — Pipeline ontologique maritime standalone.

Peut tourner SANS settings.yaml externe :
  - Chemin vers les données brutes passé en argument ou détecté automatiquement
  - Exporte TTL, OWL/XML, JSON-LD, N-Triples
  - Exécute les 12 questions de compétence SPARQL
  - Génère un rapport JSON + texte

Usage :
    python -m ontologie.pipeline                     # auto-detect
    python -m ontologie.pipeline --raw-dir path/raw  # dossier des *_final.json
    python -m ontologie.pipeline --config settings.yaml
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD
from rdflib.namespace import SKOS

logger = logging.getLogger(__name__)

NS_MAR  = "http://www.maritime-ontology.org/mar#"
NS_LKIF = "http://www.estrellaproject.org/lkif-core/lkif-core.owl#"


class MaritimeOntologyPipeline:
    """Pipeline ontologique maritime — version 2.0 standalone."""

    DEFAULT_OUT_DIR = "output/ontologie"

    def __init__(self,
                 raw_dir: Optional[str] = None,
                 config_path: Optional[str] = None,
                 out_dir: Optional[str] = None):
        self.mar  = Namespace(NS_MAR)
        self.lkif = Namespace(NS_LKIF)
        self.skos = SKOS
        self.g    = Graph()
        self._bind_namespaces()

        self.project_root = Path(__file__).resolve().parent.parent
        self.config     = self._load_config(config_path) if config_path else {}
        self.raw_dir    = Path(raw_dir)  if raw_dir  else self._auto_detect_raw()
        self.out_dir    = Path(out_dir)  if out_dir  else self.project_root / self.DEFAULT_OUT_DIR
        self.stats: Dict[str, Any] = {}

    def _auto_detect_raw(self) -> Path:
        """Cherche automatiquement le dossier contenant les *_final.json ou *_merged.json."""
        # Vérifier d'abord dans la config
        config_raw = self.config.get("data", {}).get("processed_dir")
        if config_raw:
            p = self.project_root / config_raw
            if p.exists() and (list(p.glob("*_final.json")) or list(p.glob("*_merged.json"))):
                logger.info(f"  🔍 Dossier brut trouvé via config : {p}")
                return p

        candidates = [
            self.project_root / "data/raw/extraction_merged",
            self.project_root / "data/raw/all_entité_triplets",
            self.project_root / "data/raw",
            Path("data/raw/extraction_merged"),
        ]
        for c in candidates:
            if c.exists() and (list(c.glob("*_final.json")) or list(c.glob("*_merged.json"))):
                logger.info(f"  🔍 Données détectées automatiquement : {c}")
                return c
        # Cherche depuis la racine projet
        for p in Path(".").rglob("*_merged.json"):
            return p.parent
        for p in Path(".").rglob("*_final.json"):
            return p.parent
            
        logger.warning("  ⚠️ Aucun dossier de données brutes trouvé — population statique uniquement")
        return Path(".")

    def _load_config(self, path: str) -> dict:
        try:
            import yaml
            with open(path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"  ⚠️ Config non chargée ({e}) — paramètres par défaut utilisés")
            return {}

    def _bind_namespaces(self):
        self.g.bind("mar",  self.mar)
        self.g.bind("lkif", self.lkif)
        self.g.bind("skos", SKOS)
        self.g.bind("rdf",  RDF)
        self.g.bind("rdfs", RDFS)
        self.g.bind("owl",  OWL)
        self.g.bind("xsd",  XSD)
        self.g.bind("dct",  URIRef("http://purl.org/dc/terms/"))
        self.g.bind("time", URIRef("http://www.w3.org/2006/time#"))

    # ── STEP 1 : Schéma OWL 2 DL ─────────────────────────────────
    def step_build_schema(self):
        logger.info("\n[STEP 1] Construction du schéma OWL 2 DL")
        from .schema import SchemaBuilder
        builder = SchemaBuilder(self.g, self.mar, self.lkif)
        builder.build_all()
        self._schema_ref = builder._ref

        # ── SKOS Metadata ───────────────────────────────────────────
        self.g.add((SKOS.altLabel, RDF.type, OWL.AnnotationProperty))
        self.g.add((SKOS.prefLabel, RDF.type, OWL.AnnotationProperty))
        self.g.add((SKOS.definition, RDF.type, OWL.AnnotationProperty))
        self.g.add((SKOS.broader, RDF.type, OWL.ObjectProperty))
        self.g.add((SKOS.narrower, RDF.type, OWL.ObjectProperty))
        self.g.add((SKOS.related, RDF.type, OWL.ObjectProperty))

    # ── STEP 2 : Chargement des données ──────────────────────────
    def step_load_data(self) -> dict:
        logger.info("\n[STEP 2] Chargement des données brutes")
        from .loader import load_all_raw_data, load_definitions_retenues, load_synonyms_hypernyms
        data = load_all_raw_data(self.raw_dir)
        
        # Charger les définitions retenues (détecter 'Definitions_retenues' ou 'definitions_retenues_propres')
        defs_dir = self.raw_dir.parent / "Definitions_retenues"
        if not defs_dir.exists():
            defs_dir = self.raw_dir.parent / "definitions_retenues_propres"
            
        if defs_dir.exists():
            data["definitions_retenues"] = load_definitions_retenues(defs_dir)
        else:
            data["definitions_retenues"] = {}
            
        # Charger les synonymes et hyperonymes
        syn_dir = self.raw_dir.parent / "Synonyme et hyperonymes"
        data["lexical"] = load_synonyms_hypernyms(syn_dir)
            
        return data

    # ── STEP 3 : Population des individus ────────────────────────
    def step_populate(self, data: dict):
        logger.info("\n[STEP 3] Population des individus OWL")
        from .populator import OntologyPopulator
        pop = OntologyPopulator(self.g, self.mar, self.lkif, self.skos)

        pop.populate_all(
            data=data,
            definitions_retenues=data.get("definitions_retenues", {})
        )

        n_ind = sum(1 for _, p, o in self.g
                    if p == RDF.type and o == OWL.NamedIndividual)
        logger.info(f"  ✅ {n_ind} individus OWL créés")
        self.stats["individuals"] = n_ind

    # ── STEP 3b : Injection des triplets extraits ────────────────
    def step_inject(self, data: dict):
        logger.info("\n[STEP 3b] Injection des données extraites (4 phases)")
        from .triple_injector import TripleInjector
        injector = TripleInjector(self.g, self.mar, self.lkif)
        inject_stats = injector.inject_all(data)
        self.stats["triples_injected"] = inject_stats.get("triples_injected", 0)
        self.stats["entities_typed"] = inject_stats.get("entities_typed", 0)
        self.stats["inferences_materialized"] = inject_stats.get("inferences_materialized", 0)
        self.stats["definitions_linked"] = inject_stats.get("definitions_linked", 0)

    # ── STEP 3c : Résolution d'entités (Dédoublonnage) ───────────
    def step_resolve_entities(self):
        logger.info("\n[STEP 3c] Résolution d'entités (Top-Down vs Bottom-Up)")
        from .entity_resolution import EntityResolver
        resolver = EntityResolver(self.g, self.mar)
        res_stats = resolver.resolve_all()
        self.stats["nodes_merged"] = res_stats.get("merged_nodes", 0)
        self.stats["edges_transferred"] = res_stats.get("edges_transferred", 0)

    # ── STEP 3d : Enrichissement lexical (Synonymes/Hyperonymes) ──
    # Mapping IID → activité principale dans le populator
    _IID_TO_ACTIVITY = {
        "I001": "Activite_CHALUTAGE_FOND",
        "I002": "Activite_CHASSE_BALEINE",
        "I003": "Activite_CONSTRUCTION_LITTORALE",
        "I004": "Activite_EXTRACTION_SABLE",
        "I005": "Activite_CAPTURE_OISEAUX_MARINS",
        "I006": "Activite_REJET_HYDROCARBURES",
    }

    def step_enrich_lexical(self, data: dict):
        """
        Enrichissement lexical du graphe avec synonymes et hyperonymes.

        Stratégie pour le RAG :
        ─ Synonymes (skos:altLabel) : attachés à la FOIS sur l'interdiction (mar:I001)
          et sur l'activité correspondante (mar:Activite_CHALUTAGE_FOND).
          → Quand l'utilisateur dit "chalutage démersal", le RAG peut matcher
          via skos:altLabel sur l'activité ET remonter à l'interdiction.

        ─ Hyperonymes (skos:broader) : on crée un vrai SKOS Concept avec une URI
          (mar:Concept_HYP_I001_peche_demersale) et on lie l'interdiction
          à ce concept via skos:broader.
          → Quand l'utilisateur dit "pêche destructrice", le RAG peut retrouver
          l'interdiction I001 via la relation skos:broader.
        """
        logger.info("\n[STEP 3d] Enrichissement lexical (Synonymes et Hyperonymes)")
        lexical_data = data.get("lexical", {})
        if not lexical_data:
            logger.info("  ℹ️ Aucune donnée lexicale à injecter.")
            return

        from .populator import slugify

        added_syns = 0
        added_hyps = 0

        for iid, lex in lexical_data.items():
            interdiction_uri = self.mar[iid]
            activity_local = self._IID_TO_ACTIVITY.get(iid)
            activity_uri = self.mar[activity_local] if activity_local else None
            interdiction_label = lex.get("interdiction", iid)

            # ── Synonymes → skos:altLabel sur interdiction + activité ──
            for syn in lex.get("synonymes", []):
                syn = syn.strip()
                if not syn:
                    continue
                # Détection de la langue améliorée
                # Si contient des caractères français typiques ou si le français est probable
                french_indicators = "éàèêëîïôûùç"
                has_french_chars = any(c in french_indicators for c in syn.lower())
                
                # Heuristique : Si on a des mots français courants ou des caractères spéciaux
                fr_words = {"de", "la", "le", "les", "des", "du", "un", "une", "en", "et", "ou", "pour", "dans", "sur", "au", "aux", "avec", "par", "d", "l"}
                syn_lower = syn.lower().replace("'", " ").split()
                has_fr_words = any(w in syn_lower for w in fr_words)
                
                lang = "fr" if (has_french_chars or has_fr_words) else "en"
                lit = Literal(syn, lang=lang)

                # Attacher à l'interdiction
                self.g.add((interdiction_uri, SKOS.altLabel, lit))
                # Attacher à l'activité principale
                if activity_uri:
                    self.g.add((activity_uri, SKOS.altLabel, lit))
                added_syns += 1

            # ── Hyperonymes → vrais SKOS Concepts avec skos:broader ──
            for hyp in lex.get("hyperonymes", []):
                hyp = hyp.strip()
                if not hyp:
                    continue
                slug = slugify(hyp)[:60]
                concept_local = f"Concept_HYP_{iid}_{slug}"
                concept_uri = self.mar[concept_local]

                # Créer le concept SKOS s'il n'existe pas
                if (concept_uri, RDF.type, SKOS.Concept) not in self.g:
                    self.g.add((concept_uri, RDF.type, SKOS.Concept))
                    self.g.add((concept_uri, RDF.type, OWL.NamedIndividual))
                    # Langue pour l'hyperonyme
                    french_indicators = "éàèêëîïôûùç"
                    has_french_chars = any(c in french_indicators for c in hyp.lower())
                    fr_words = {"de", "la", "le", "les", "des", "du", "un", "une", "en", "et", "ou", "pour", "dans", "sur"}
                    has_fr_words = any(w in hyp.lower().split() for w in fr_words)
                    
                    lang = "fr" if (has_french_chars or has_fr_words) else "en"
                    self.g.add((concept_uri, SKOS.prefLabel, Literal(hyp, lang=lang)))
                    self.g.add((concept_uri, SKOS.inScheme, self.mar["GlossairePeche"]))
                    self.g.add((concept_uri, RDFS.comment,
                                Literal(f"Hyperonyme de l'interdiction {iid} ({interdiction_label})", lang="fr")))

                # Lier l'interdiction et l'activité à ce concept via skos:broader
                self.g.add((interdiction_uri, SKOS.broader, concept_uri))
                if activity_uri:
                    self.g.add((activity_uri, SKOS.broader, concept_uri))
                added_hyps += 1

            logger.info(
                f"    ✅ {iid} ({interdiction_label}): "
                f"{len(lex.get('synonymes', []))} synonymes, "
                f"{len(lex.get('hyperonymes', []))} hyperonymes"
            )

        logger.info(f"  ✅ Total: {added_syns} synonymes (altLabel) et {added_hyps} hyperonymes (broader → Concept)")
        self.stats["lexical_synonyms"] = added_syns
        self.stats["lexical_hypernyms"] = added_hyps

    # ── STEP 4 : Corrections post-traitement ─────────────────────
    def step_corrections(self):
        logger.info("\n[STEP 4] Corrections et enrichissements")
        try:
            from .corrections import OntologyCorrections
            corrector = OntologyCorrections(self.g, self.mar, self.lkif)
            corrector.apply_all_corrections()
        except Exception as e:
            logger.warning(f"  ⚠️ Corrections non appliquées : {e}")

    # ── STEP 5 : Export ───────────────────────────────────────────
    def step_export(self) -> dict:
        logger.info("\n[STEP 5] Export des fichiers ontologiques")
        self.out_dir.mkdir(parents=True, exist_ok=True)
        paths = {}

        formats = [
            ("turtle",  "maritime_ontology.ttl",    "ttl"),
            ("xml",     "maritime_ontology.owl",     "owl"),
            ("json-ld", "maritime_ontology.jsonld",  "jsonld"),
            ("nt",      "maritime_ontology.nt",      "nt"),
        ]
        for fmt, name, ext in formats:
            out_path = self.out_dir / name
            try:
                if fmt == "xml":
                    self.g.serialize(destination=str(out_path), format=fmt, base=str(self.mar).rstrip("#"))
                else:
                    self.g.serialize(destination=str(out_path), format=fmt)
                paths[ext] = str(out_path)
                logger.info(f"  ✅ {name} ({out_path.stat().st_size} octets)")
            except Exception as e:
                logger.error(f"  ❌ Échec de l'export {fmt} : {e}")
                if fmt == "turtle":
                    fallback = self.out_dir / name.replace(".ttl", ".nt")
                    self.g.serialize(destination=str(fallback), format="nt")
                    logger.info(f"  ⚠️  Turtle a échoué, export NT de secours : {fallback}")

        return paths

    # ── STEP 6 : Questions SPARQL ─────────────────────────────────
    def step_sparql(self) -> dict:
        logger.info("\n[STEP 6] Questions de compétence SPARQL")
        try:
            from .sparql_runner import run_all_competency_questions, format_results_report
            results = run_all_competency_questions(self.g)

            rp = str(self.out_dir / "sparql_results.json")
            with open(rp, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            tp = str(self.out_dir / "sparql_report.txt")
            with open(tp, "w", encoding="utf-8") as f:
                f.write(format_results_report(results))
            logger.info(f"  [OK] Rapport SPARQL → {tp}")
            return results
        except Exception as e:
            logger.warning(f"  ⚠️ SPARQL partiellement échoué : {e}")
            return {}

    # ── STEP 7 : Raisonnement OWL-RL ─────────────────────────────
    def step_reason(self) -> bool:
        logger.info("\n[STEP 7] Raisonnement OWL-RL (owlrl)")
        try:
            import owlrl
            owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(self.g)
            n = len(self.g)
            logger.info(f"  ✅ Inférence terminée — {n} triplets après expansion")

            # Nettoyage des owl:sameAs réflexifs (bruit du raisonneur OWL-RL)
            reflexive_count = 0
            for s, p, o in list(self.g.triples((None, OWL.sameAs, None))):
                if s == o:
                    self.g.remove((s, p, o))
                    reflexive_count += 1
            if reflexive_count:
                logger.info(f"  🧹 {reflexive_count} triplets owl:sameAs réflexifs supprimés")

            # Vérification de cohérence
            conflicts = list(self.g.subjects(RDF.type, OWL.Nothing))
            if conflicts:
                logger.error(f"  ❌ {len(conflicts)} individus → owl:Nothing (incohérence)")
                for c in conflicts[:5]:
                    logger.error(f"     - {c}")
                return False
            else:
                logger.info("  ✅ Cohérence vérifiée — aucun conflit détecté")

            # Export avec inférences
            inf_path = str(self.out_dir / "maritime_ontology_inferred.ttl")
            self.g.serialize(destination=inf_path, format="turtle")
            logger.info(f"  ✅ Ontologie inférée → {inf_path}")
            return True

        except ImportError:
            logger.info("  ℹ️  owlrl non installé (pip install owlrl) — raisonnement ignoré")
            return False
        except Exception as e:
            logger.warning(f"  ⚠️ Raisonnement échoué : {e}")
            return False

    # ── STEP 8 : Export Neo4j (Cypher & Live) ─────────────────────
    def step_neo4j(self) -> Optional[str]:
        logger.info("\n[STEP 8] Export Neo4j (Fichier Cypher + Base de données)")
        try:
            from .neo4j_export import build_graph_data, generate_cypher_script, export_to_neo4j
            
            # 1. Génération du fichier Cypher (sauvegarde)
            nodes, edges = build_graph_data(self.g)
            cypher_script = generate_cypher_script(nodes, edges)
            
            cypher_path = self.out_dir / "neo4j_import.cypher"
            with open(cypher_path, "w", encoding="utf-8") as f:
                f.write(cypher_script)
            logger.info(f"  [OK] Script Cypher Neo4j sauvegardé → {cypher_path}")
            
            # 2. Export direct vers la base de données Neo4j
            neo4j_config = self.config.get("neo4j", {})
            if neo4j_config:
                logger.info("  🔄 Tentative d'export direct vers Neo4j Desktop...")
                success = export_to_neo4j(self.g, neo4j_config)
                if success:
                    logger.info("  ✅ Export vers Neo4j réussi !")
                else:
                    logger.warning("  ⚠️ Export Neo4j échoué (vérifie que la base est démarrée et que pip install neo4j est fait)")
            else:
                logger.info("  ℹ️ Pas de configuration 'neo4j' trouvée dans settings.yaml.")
                
            return str(cypher_path)
        except Exception as e:
            logger.warning(f"  ⚠️ Génération Cypher Neo4j échouée : {e}")
            return None

    # ── STEP 9 : Rapport final ────────────────────────────────────
    def step_report(self, paths: dict, sparql_results: dict) -> dict:
        self.stats.update({
            "total_triples":      len(self.g),
            "classes":            sum(1 for _, p, o in self.g if p == RDF.type and o == OWL.Class),
            "object_properties":  sum(1 for _, p, o in self.g if p == RDF.type and o == OWL.ObjectProperty),
            "data_properties":    sum(1 for _, p, o in self.g if p == RDF.type and o == OWL.DatatypeProperty),
            "individuals":        sum(1 for _, p, o in self.g if p == RDF.type and o == OWL.NamedIndividual),
            "interdictions":      sum(1 for _, p, o in self.g
                                      if p == RDF.type and o == self.mar.Interdiction),
            "sparql_questions":   len(sparql_results),
            "timestamp":          datetime.now().isoformat(),
            "version":            "2.0.0",
        })

        rp = str(self.out_dir / "ontology_report.json")
        with open(rp, "w", encoding="utf-8") as f:
            json.dump({"stats": self.stats, "output_files": paths}, f, ensure_ascii=False, indent=2)

        logger.info("\n" + "=" * 65)
        logger.info("  [✅] PIPELINE TERMINÉ — RÉSUMÉ")
        logger.info(f"  Triplets totaux    : {self.stats['total_triples']}")
        logger.info(f"  Classes OWL        : {self.stats['classes']}")
        logger.info(f"  Propriétés objet   : {self.stats['object_properties']}")
        logger.info(f"  Propriétés données : {self.stats['data_properties']}")
        logger.info(f"  Individus OWL      : {self.stats['individuals']}")
        logger.info(f"  Interdictions      : {self.stats['interdictions']}")
        logger.info(f"  --- Injection RAG ---")
        logger.info(f"  Triplets injectés  : {self.stats.get('triples_injected', 0)}")
        logger.info(f"  Entités typées     : {self.stats.get('entities_typed', 0)}")
        logger.info(f"  Inférences         : {self.stats.get('inferences_materialized', 0)}")
        logger.info(f"  Définitions liées  : {self.stats.get('definitions_linked', 0)}")
        logger.info(f"  --- Dédoublonnage ---")
        logger.info(f"  Nœuds fusionnés    : {self.stats.get('nodes_merged', 0)}")
        logger.info(f"  Arêtes redirigées  : {self.stats.get('edges_transferred', 0)}")
        logger.info("=" * 65)
        return self.stats

    # ── STEP 4b : Normalisation OWL (qualité pour Neo4j) ─────────
    def step_normalize(self):
        """
        Applique les 5 corrections de qualité OWL en mémoire :
          1. Labels bruts mar:XXX → texte lisible
          2. Faux acteurs → ConditionApplication
          3. Déduplication espèces
          4. xml:lang incorrects
          5. Hyperonymes excessifs
        """
        logger.info("\n[STEP 4b] Normalisation OWL (qualite pour Neo4j)")
        try:
            import importlib.util
            fix_owl_path = self.project_root / "scripts" / "fix_owl.py"
            spec = importlib.util.spec_from_file_location("fix_owl", str(fix_owl_path))
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load fix_owl module from {fix_owl_path}")
            fix_owl = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(fix_owl)

            n1 = fix_owl.fix_labels(self.g)
            n2 = fix_owl.fix_false_actors(self.g)
            n3 = fix_owl.fix_deduplication(self.g)
            n4 = fix_owl.fix_xml_lang(self.g)
            n5 = fix_owl.fix_hyperonyms(self.g)
            self.stats["normalize_labels"] = n1
            self.stats["normalize_false_actors"] = n2
            self.stats["normalize_dedup"] = n3
            self.stats["normalize_lang"] = n4
            self.stats["normalize_hyperonyms"] = n5
            logger.info(
                f"  [OK] Normalisation : {n1} labels, {n2} faux acteurs, "
                f"{n3} dedup, {n4} lang, {n5} hyperonymes"
            )
        except Exception as e:
            logger.warning(f"  [WARN] Normalisation echouee : {e}")

    # ── RUN ───────────────────────────────────────────────────────
    def run(self, reason: bool = True, run_sparql: bool = True) -> dict:
        logger.info("=" * 65)
        logger.info("  MARITIME ONTOLOGY PIPELINE v2.0 — OWL 2 DL")
        logger.info("  6 interdictions | Alignement LKIF-Core | Raisonnement OWL-RL")
        logger.info("=" * 65)

        self.step_build_schema()
        data = self.step_load_data()
        self.step_populate(data)
        self.step_inject(data)
        self.step_enrich_lexical(data)
        self.step_resolve_entities()
        self.step_corrections()
        if reason:
            self.step_reason()         # Raisonner AVANT de normaliser et d'exporter
        self.step_normalize()          # Nettoyage (incluant les inférences bruyantes)
        paths = self.step_export()
        sparql = self.step_sparql() if run_sparql else {}
        neo4j_path = self.step_neo4j()
        if neo4j_path:
            paths["neo4j"] = neo4j_path
            
        stats = self.step_report(paths, sparql)

        return {"stats": stats, "paths": paths}
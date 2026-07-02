"""
Ontologie Maritime — LKIF-Core aligned.

Package contenant le pipeline complet de construction de l'ontologie maritime :
  - Schéma OWL (classes, propriétés, restrictions)
  - Population des individus (A-Box)
  - Corrections post-traitement
  - Export (TTL, OWL, JSON-LD, N-Triples)
  - Requêtes SPARQL de compétence
  - Export Neo4j
"""
from .pipeline import MaritimeOntologyPipeline

__all__ = ["MaritimeOntologyPipeline"]
__version__ = "2.0.0"

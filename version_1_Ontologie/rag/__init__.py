"""
RAG Maritime — Système de Retrieval Augmented Generation pour le droit maritime.

Architecture Ontology-Augmented Hybrid RAG :
  - Dense Retriever (ChromaDB + bge-m3)
  - Sparse Retriever (BM25)
  - Graph Retriever (SPARQL sur ontologie OWL)
  - Fusion RRF avec bonus ontologique
"""

__version__ = "0.2.0"
__author__ = "Maritime RAG System"

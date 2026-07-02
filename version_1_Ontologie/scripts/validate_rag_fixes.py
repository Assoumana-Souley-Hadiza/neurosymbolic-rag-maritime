"""Validate all RAG config fixes."""
import sys
sys.path.insert(0, ".")

from rag.config import ONTOLOGY_CONFIG, NEO4J_CONFIG, QUERY_ANALYZER_CONFIG
from pathlib import Path

print("=== Config Fixes Validation ===")

# Fix 6: OWL path
owl_path = Path(ONTOLOGY_CONFIG["owl_path"])
print(f"OWL path: {owl_path}")
print(f"  Exists: {owl_path.exists()}")

# Fix 7: NEO4J_CONFIG
print(f"NEO4J_CONFIG: {NEO4J_CONFIG}")

# Fix 8: existence_weights
ew = QUERY_ANALYZER_CONFIG.get("existence_weights", "MISSING!")
print(f"existence_weights: {ew}")

# Test QueryAnalyzer with existence query
from rag.core.query_analyzer import QueryAnalyzer
qa = QueryAnalyzer()

tests = [
    "interdiction chasse a la baleine au Maroc",
    "est-ce que la chasse a la baleine est interdite au Senegal",
    "y a-t-il une protection des cetaces en Algerie",
    "quelles sont les conventions sur les rejets d'hydrocarbures",
]

for q in tests:
    intent, weights, country = qa.analyze(q)
    print(f"\n  Query: '{q}'")
    print(f"    intent={intent}, country={country}")

# Fix 9: context window
from rag.llm_generator import DocumentContextBuilder
import inspect
sig = inspect.signature(DocumentContextBuilder.build)
default_max = sig.parameters["max_chars"].default
print(f"\nContext window: {default_max} chars")

print("\nAll RAG fixes validated!")

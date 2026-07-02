import logging
logging.basicConfig(level=logging.INFO)
from rag.integration.neo4j_bridge import Neo4jBridge

bridge = Neo4jBridge()
if not bridge.is_ready():
    print("Bridge is not ready. Check Neo4j connection.")
    exit(1)

print("--- Testing get_synonyms_batch ---")
terms = ["chalutage", "baleine"]
print(f"Terms: {terms}")
res = bridge.get_synonyms_batch(terms)
print(f"Result: {res}")

print("\n--- Testing Cypher Directly ---")
cypher = """
UNWIND $terms AS term
MATCH (n)
WHERE toLower(coalesce(n.label, n.name, '')) CONTAINS toLower(term)
OPTIONAL MATCH (n)-[:SYNONYME_DE|HAS_SYNONYM|SYNONYME]-(syn)
RETURN term,
       coalesce(n.label, n.name) AS node_label,
       collect(DISTINCT coalesce(syn.label, syn.name)) AS synonyms
"""
results = bridge.run(cypher, {"terms": terms})
print(results)

bridge.close()

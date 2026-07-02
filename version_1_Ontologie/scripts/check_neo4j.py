"""Check Neo4j state vs OWL ontology."""
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "nawras2026"))
try:
    driver.verify_connectivity()
    print("Neo4j connecte!")

    with driver.session(database="neo4j") as s:
        r = s.run("MATCH (n) RETURN count(n) AS c").single()
        print(f"Total noeuds: {r['c']}")

        r = s.run("MATCH ()-[r]->() RETURN count(r) AS c").single()
        print(f"Total relations: {r['c']}")

        print("\n=== NOEUDS PAR LABEL ===")
        for rec in s.run("CALL db.labels() YIELD label RETURN label ORDER BY label"):
            lbl = rec["label"]
            cnt = s.run(f"MATCH (n:`{lbl}`) RETURN count(n) AS c").single()["c"]
            print(f"  :{lbl} -> {cnt}")

        print("\n=== RELATIONS PAR TYPE ===")
        for rec in s.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType ORDER BY relationshipType"):
            rt = rec["relationshipType"]
            cnt = s.run(f"MATCH ()-[r:`{rt}`]->() RETURN count(r) AS c").single()["c"]
            print(f"  [{rt}] -> {cnt}")

        print("\n=== SAMPLE: Interdictions ===")
        for rec in s.run("MATCH (n:Interdiction) RETURN n.id AS id, n.label AS lbl LIMIT 6"):
            print(f"  {rec['id']}: {rec['lbl']}")

        print("\n=== SAMPLE: Especes ===")
        for rec in s.run("MATCH (n:EspeceMarine) RETURN n.id AS id, n.label AS lbl LIMIT 8"):
            print(f"  {rec['id']}: {rec['lbl']}")

        print("\n=== SAMPLE: Synonymes ===")
        for rec in s.run("MATCH (s:Synonyme)-[:SYNONYME_DE]->(n) RETURN s.label AS syn, n.label AS target, labels(n) AS types LIMIT 8"):
            print(f"  '{rec['syn']}' -> '{rec['target']}' ({rec['types']})")

        # Check for bad labels (mar:)
        r = s.run("MATCH (n) WHERE n.label STARTS WITH 'mar:' RETURN count(n) AS c").single()
        print(f"\nBad labels (mar:): {r['c']}")

        # Check ConditionApplication
        r = s.run("MATCH (n:ConditionApplication) RETURN count(n) AS c").single()
        print(f"ConditionApplication: {r['c']}")

except Exception as e:
    print(f"Erreur: {e}")
finally:
    driver.close()

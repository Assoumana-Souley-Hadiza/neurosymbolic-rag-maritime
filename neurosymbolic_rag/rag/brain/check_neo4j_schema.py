
import os
from neo4j import GraphDatabase
import json

# Configuration depuis votre fichier rag.config ou valeurs par défaut
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "nawras2026"

def check_neo4j_schema():
    print("--- Diagnostic du schema Neo4j ---")
    try:
        driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
        with driver.session() as session:
            # 1. Lister les types de relations
            print("\n1. Types de relations presentes :")
            rel_types = session.run("CALL db.relationshipTypes()")
            for record in rel_types:
                print(f"   - {record[0]}")

            # 2. Lister les labels de nœuds
            print("\n2. Labels de nœuds presents :")
            node_labels = session.run("CALL db.labels()")
            for record in node_labels:
                print(f"   - {record[0]}")

            # 3. Inspecter un nœud Interdiction au hasard
            print("\n3. Inspection d'un noeud 'Interdiction' :")
            node_sample = session.run("MATCH (n:Interdiction) RETURN n LIMIT 1")
            record = node_sample.single()
            if record:
                node = record[0]
                print(f"   - Proprietes : {list(node.keys())}")
                print(f"   - Exemple de label : {node.get('label') or node.get('name')}")
                
                # Voir ses relations sortantes
                rels = session.run("MATCH (n:Interdiction)-[r]->(m) WHERE id(n) = $id RETURN type(r) as type, labels(m) as target_labels LIMIT 5", {"id": node.id})
                print("   - Relations sortantes :")
                for r in rels:
                    print(f"     [:{r['type']}] -> {r['target_labels']}")
            else:
                print("   - Aucun noeud 'Interdiction' trouve !")

            # 4. Vérifier spécifiquement les synonymes
            print("\n4. Test specifique de recherche de synonymes :")
            syn_check = session.run("MATCH (n)-[r]-(m) WHERE type(r) CONTAINS 'SYN' OR type(r) CONTAINS 'LABEL' RETURN type(r) as type LIMIT 5")
            found_syn = False
            for r in syn_check:
                found_syn = True
                print(f"   - Relation de type synonyme trouvee : {r['type']}")
            if not found_syn:
                print("   - Aucun relation contenant 'SYN' ou 'LABEL' trouvee !")

        driver.close()
    except Exception as e:
        print(f"Erreur de connexion : {e}")

if __name__ == "__main__":
    check_neo4j_schema()

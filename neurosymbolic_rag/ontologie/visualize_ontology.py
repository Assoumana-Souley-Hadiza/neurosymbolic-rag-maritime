#!/usr/bin/env python3
"""
Visualisation interactive de l'ontologie maritime en HTML
Utilise PyVis pour créer un graphe interactif explorable
"""

import json
from pathlib import Path
from rdflib import Graph, Namespace, URIRef
from pyvis.network import Network

def load_ontology(owl_path: str) -> Graph:
    """Charge l'ontologie OWL."""
    print(f"📖 Chargement de l'ontologie : {owl_path}")
    g = Graph()
    g.parse(owl_path, format='xml')
    print(f"✅ Ontologie chargée : {len(g)} triplets")
    return g

def create_visualization(g: Graph, output_html: str = "maritime_ontology_graph.html"):
    """Crée une visualisation interactive du graphe RDF."""
    
    print("\n🎨 Création du graphe interactif...")
    
    # Créer le réseau PyVis
    net = Network(height="900px", width="100%", directed=True, notebook=False)
    
    # Configurer la physique
    net.toggle_physics(True)
    
    # Ajouter les nœuds et arêtes
    ns_mar = "http://www.maritime-ontology.org/mar#"
    NS_MAR = Namespace(ns_mar)
    
    processed_nodes = set()
    processed_edges = set()
    
    # Dictionnaire pour les couleurs par type
    colors = {
        'Interdiction': '#FF6B6B',        # Rouge
        'EspeceMarine': '#4ECDC4',        # Turquoise
        'Zone': '#45B7D1',                # Bleu
        'Activite': '#FFA07A',            # Orange
        'Acteur': '#98D8C8',              # Vert menthe
        'Periode': '#F7DC6F',             # Jaune
        'Exception': '#BB8FCE',           # Violet
        'Controle': '#85C1E2',            # Bleu ciel
        'ConceptLexical': '#F8B88B',      # Beige
        'SourceJuridique': '#D7BCCB',     # Rose
        'default': '#CCCCCC'              # Gris
    }
    
    # Ajouter les nœuds
    for subject in set(g.subjects()):
        if not isinstance(subject, URIRef):
            continue
        
        node_id = str(subject).replace(ns_mar, '')
        
        if node_id not in processed_nodes:
            # Obtenir le label
            labels = list(g.objects(subject, URIRef('http://www.w3.org/2000/01/rdf-schema#label')))
            label = str(labels[0]) if labels else node_id
            
            # Déterminer le type et la couleur
            node_type = 'default'
            color = colors['default']
            
            if 'Interdiction' in node_id:
                node_type = 'Interdiction'
                color = colors['Interdiction']
                size = 40
            elif 'Espece' in node_id:
                node_type = 'EspeceMarine'
                color = colors['EspeceMarine']
                size = 25
            elif 'Zone' in node_id:
                node_type = 'Zone'
                color = colors['Zone']
                size = 20
            elif 'Activite' in node_id:
                node_type = 'Activite'
                color = colors['Activite']
                size = 18
            elif 'Acteur' in node_id:
                node_type = 'Acteur'
                color = colors['Acteur']
                size = 18
            elif 'Periode' in node_id:
                node_type = 'Periode'
                color = colors['Periode']
                size = 15
            elif 'Exception' in node_id:
                node_type = 'Exception'
                color = colors['Exception']
                size = 15
            elif 'Controle' in node_id:
                node_type = 'Controle'
                color = colors['Controle']
                size = 15
            elif 'Glossaire' in node_id or 'Concept' in node_id:
                node_type = 'ConceptLexical'
                color = colors['ConceptLexical']
                size = 12
            elif 'Resolution' in node_id or 'convention' in node_id.lower():
                node_type = 'SourceJuridique'
                color = colors['SourceJuridique']
                size = 16
            else:
                size = 15
            
            # Ajouter le nœud
            net.add_node(
                node_id,
                label=label[:50],  # Limiter la longueur du label
                title=label,       # Afficher le label complet au survol
                color=color,
                size=size,
                shape='box' if node_type == 'Interdiction' else ('ellipse' if node_type == 'EspeceMarine' else 'dot')
            )
            
            processed_nodes.add(node_id)
    
    # Ajouter les arêtes (propriétés importantes seulement)
    important_predicates = {
        'protegeEspece': '🦈 protège',
        'appliesInZone': '📍 s\'applique',
        'concerneActivite': '⚙️ concerne',
        'concerneActeur': '👥 acteur',
        'aException': '⚠️ exception',
        'appliesDuring': '⏱️ période',
        'soumisA': '📋 soumis',
        'fondeeSur': '📄 fondée sur',
    }
    
    for pred_local, pred_label in important_predicates.items():
        pred = URIRef(ns_mar + pred_local)
        
        for subject, obj in g.subject_objects(pred):
            if isinstance(subject, URIRef) and isinstance(obj, URIRef):
                source = str(subject).replace(ns_mar, '')
                target = str(obj).replace(ns_mar, '')
                
                if source in processed_nodes and target in processed_nodes:
                    edge_key = (source, target, pred_local)
                    
                    if edge_key not in processed_edges:
                        net.add_edge(
                            source,
                            target,
                            title=pred_label,
                            label=pred_local,
                            color='#555555',
                            width=2
                        )
                        processed_edges.add(edge_key)
    
    # Configurer la physique du réseau pour une meilleure disposition
    net.show_buttons(filter_=['physics'])
    net.write_html(output_html)
    
    print(f"\n✅ Visualisation créée : {output_html}")
    print(f"   📊 Nœuds : {len(processed_nodes)}")
    print(f"   🔗 Arêtes : {len(processed_edges)}")
    print(f"\n🌐 Ouvre ce fichier dans tu navigateur pour explorer le graphe !")
    return output_html

def main():
    """Fonction principale."""
    owl_path = "data/output/maritime_ontology.owl"
    
    if not Path(owl_path).exists():
        print(f"❌ Fichier non trouvé : {owl_path}")
        print("Assure-toi d'avoir exécuté 'python main.py' en premier")
        return
    
    # Charger l'ontologie
    g = load_ontology(owl_path)
    
    # Créer la visualisation
    output_file = create_visualization(g)
    
    print(f"\n📂 Fichier généré : {Path(output_file).absolute()}")

if __name__ == "__main__":
    main()

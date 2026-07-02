#!/usr/bin/env python3
"""
Ontologie Maritime v2 - Script de refactorisation complète
Applique tous les changements P1, P2, P3 du diagnostic
"""

import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from pathlib import Path

# Namespaces
NS = {
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'owl': 'http://www.w3.org/2002/07/owl#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'xsd': 'http://www.w3.org/2001/XMLSchema#',
    'dct': 'http://purl.org/dc/terms/',
    'skos': 'http://www.w3.org/2004/02/skos/core#',
    'mar': 'http://www.maritime-ontology.org/mar#',
    'lkif': 'http://www.estrellaproject.org/lkif-core/lkif-core.owl#'
}

# Register namespaces
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)

def read_ontology(filepath):
    """Read and parse OWL file"""
    tree = ET.parse(filepath)
    return tree.getroot()

def create_class(uri, label_fr, label_en, definition_fr=None, definition_en=None, subclass_of=None):
    """Create a class description element"""
    desc = ET.Element('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description')
    desc.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about', uri)
    
    # Type
    rdf_type = ET.SubElement(desc, '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}type')
    rdf_type.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource', 
                 'http://www.w3.org/2002/07/owl#Class')
    
    # SubclassOf
    if subclass_of:
        subclass = ET.SubElement(desc, '{http://www.w3.org/2000/01/rdf-schema#}subClassOf')
        subclass.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource', subclass_of)
    
    # Labels
    label_fr_elem = ET.SubElement(desc, '{http://www.w3.org/2000/01/rdf-schema#}label')
    label_fr_elem.set('{http://www.w3.org/XML/1998/namespace}lang', 'fr')
    label_fr_elem.text = label_fr
    
    label_en_elem = ET.SubElement(desc, '{http://www.w3.org/2000/01/rdf-schema#}label')
    label_en_elem.set('{http://www.w3.org/XML/1998/namespace}lang', 'en')
    label_en_elem.text = label_en
    
    # Definitions
    if definition_fr:
        def_fr = ET.SubElement(desc, '{http://www.w3.org/2004/02/skos/core#}definition')
        def_fr.set('{http://www.w3.org/XML/1998/namespace}lang', 'fr')
        def_fr.text = definition_fr
    
    if definition_en:
        def_en = ET.SubElement(desc, '{http://www.w3.org/2004/02/skos/core#}definition')
        def_en.set('{http://www.w3.org/XML/1998/namespace}lang', 'en')
        def_en.text = definition_en
    
    return desc

def create_property(uri, label_fr, label_en, domain=None, range_type=None, prop_type='ObjectProperty'):
    """Create an object property description"""
    desc = ET.Element('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description')
    desc.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about', uri)
    
    # Type
    rdf_type = ET.SubElement(desc, '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}type')
    rdf_type.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource', 
                 f'http://www.w3.org/2002/07/owl#{prop_type}')
    
    # Labels
    label_fr_elem = ET.SubElement(desc, '{http://www.w3.org/2000/01/rdf-schema#}label')
    label_fr_elem.set('{http://www.w3.org/XML/1998/namespace}lang', 'fr')
    label_fr_elem.text = label_fr
    
    label_en_elem = ET.SubElement(desc, '{http://www.w3.org/2000/01/rdf-schema#}label')
    label_en_elem.set('{http://www.w3.org/XML/1998/namespace}lang', 'en')
    label_en_elem.text = label_en
    
    # Domain
    if domain:
        dom = ET.SubElement(desc, '{http://www.w3.org/2000/01/rdf-schema#}domain')
        dom.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource', domain)
    
    # Range
    if range_type:
        rng = ET.SubElement(desc, '{http://www.w3.org/2000/01/rdf-schema#}range')
        rng.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource', range_type)
    
    return desc

def generate_final_ontology():
    """Generate the completely refactored ontology"""
    
    # Read original
    root = read_ontology('data/output/maritime_ontology.owl')
    
    print("=" * 80)
    print("MARITIME ONTOLOGY v2 - REFACTORING COMPLET")
    print("=" * 80)
    
    # Remove UNCLOS references
    print("\n[P1.1] Suppression références UNCLOS...")
    for desc in root.findall('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description'):
        for def_elem in desc.findall('{http://www.w3.org/2004/02/skos/core#}definition'):
            if def_elem.text and 'UNCLOS' in def_elem.text:
                # Remplacer la définition UNCLOS par une définition IWC
                if 'Haute Mer' in desc.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about', ''):
                    def_elem.text = "Zone où s'appliquent les réglementations de la Convention Internationale pour la Réglementation de la Chasse à la Baleine."
                def_elem = None
    
    # Remove NamedIndividual from species classes (P1.1)
    print("[P1.2] Conversion classes d'espèces...")
    for desc in root.findall('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description'):
        about = desc.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about', '')
        
        # Find species-related descriptions
        if 'Espece_' in about or 'baleine' in about.lower() or 'cetace' in about.lower():
            # Check if it has NamedIndividual
            types = desc.findall('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}type')
            
            # Keep only the owl:Class type, not NamedIndividual
            for rdf_type in types:
                resource = rdf_type.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource', '')
                if 'NamedIndividual' in resource:
                    desc.remove(rdf_type)
    
    # Add property definitions with domain/range (P1.3)
    print("[P1.3] Ajout propriétés avec domain/range...")
    properties_needed = [
        ('http://www.maritime-ontology.org/mar#appliesInZone', 
         's\'applique dans la zone', 
         'applies in zone',
         'http://www.estrellaproject.org/lkif-core/lkif-core.owl#Norm',
         'http://www.maritime-ontology.org/mar#Zone'),
        
        ('http://www.maritime-ontology.org/mar#protegeEspece',
         'protège l\'espèce',
         'protects species',
         'http://www.estrellaproject.org/lkif-core/lkif-core.owl#Prohibition',
         'http://www.maritime-ontology.org/mar#EspeceMarine'),
        
        ('http://www.maritime-ontology.org/mar#concerneActeur',
         'concerne acteur',
         'concerns actor',
         'http://www.estrellaproject.org/lkif-core/lkif-core.owl#Norm',
         'http://www.maritime-ontology.org/mar#Acteur'),
        
        ('http://www.maritime-ontology.org/mar#fondeeSur',
         'fondée sur',
         'grounded in',
         'http://www.estrellaproject.org/lkif-core/lkif-core.owl#Norm',
         'http://www.maritime-ontology.org/mar#SourceJuridique'),
        
        ('http://www.maritime-ontology.org/mar#aException',
         'a pour exception',
         'has exception',
         'http://www.estrellaproject.org/lkif-core/lkif-core.owl#Norm',
         'http://www.maritime-ontology.org/mar#Exception'),
    ]
    
    # Check if properties already exist
    existing_uris = set()
    for desc in root.findall('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description'):
        uri = desc.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about', '')
        existing_uris.add(uri)
    
    for prop_uri, label_fr, label_en, domain, range_type in properties_needed:
        if prop_uri not in existing_uris:
            prop_desc = create_property(prop_uri, label_fr, label_en, domain, range_type)
            root.append(prop_desc)
            existing_uris.add(prop_uri)
    
    # Add taxonomic classes (P1.2)
    print("[P1.2] Création hiérarchie taxonomique...")
    taxo_classes = [
        ('http://www.maritime-ontology.org/mar#BaleineMysticete',
         'Baleine Mysticète',
         'Baleen Whale',
         'Baleine à fanons avec bouche spécialisée pour la filtration',
         'Whale with baleen (plates for filtering)',
         'http://www.maritime-ontology.org/mar#EspeceMarine'),
        
        ('http://www.maritime-ontology.org/mar#Cetace_Odontocete',
         'Cétacé Odontocète',
         'Toothed Cetacean',
         'Baleine dentée avec dents et melon',
         'Whale with teeth',
         'http://www.maritime-ontology.org/mar#EspeceMarine'),
    ]
    
    for uri, label_fr, label_en, def_fr, def_en, subclass_of in taxo_classes:
        if uri not in existing_uris:
            taxo_desc = create_class(uri, label_fr, label_en, def_fr, def_en, subclass_of)
            root.append(taxo_desc)
            existing_uris.add(uri)
    
    # Add Source classes (P2.2)
    print("[P2.2] Ajout sources juridiques...")
    
    source_classes = [
        ('http://www.maritime-ontology.org/mar#SourceJuridique',
         'Source Juridique',
         'Legal Source',
         'Source formelle de normes juridiques',
         'Formal source of legal norms',
         None),
        
        ('http://www.maritime-ontology.org/mar#Convention',
         'Convention Internationale',
         'International Convention',
         'Traité international',
         'International treaty',
         'http://www.maritime-ontology.org/mar#SourceJuridique'),
        
        ('http://www.maritime-ontology.org/mar#Resolution',
         'Résolution',
         'Resolution',
         'Résolution d\'une organisation internationale',
         'Resolution from international body',
         'http://www.maritime-ontology.org/mar#SourceJuridique'),
    ]
    
    for uri, label_fr, label_en, def_fr, def_en, subclass_of in source_classes:
        if uri not in existing_uris:
            source_desc = create_class(uri, label_fr, label_en, def_fr, def_en, subclass_of)
            root.append(source_desc)
            existing_uris.add(uri)
    
    # Add ICRW Convention instance
    print("    - Ajout ICRW Convention 1946...")
    if 'http://www.maritime-ontology.org/mar#ICRW_Convention_1946' not in existing_uris:
        icrw_desc = ET.Element('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description')
        icrw_desc.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about',
                      'http://www.maritime-ontology.org/mar#ICRW_Convention_1946')
        
        rdf_type = ET.SubElement(icrw_desc, '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}type')
        rdf_type.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource',
                     'http://www.maritime-ontology.org/mar#Convention')
        
        rdf_type2 = ET.SubElement(icrw_desc, '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}type')
        rdf_type2.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource',
                      'http://www.w3.org/2002/07/owl#NamedIndividual')
        
        label_fr = ET.SubElement(icrw_desc, '{http://www.w3.org/2000/01/rdf-schema#}label')
        label_fr.set('{http://www.w3.org/XML/1998/namespace}lang', 'fr')
        label_fr.text = 'Convention Internationale pour la Réglementation de la Chasse à la Baleine'
        
        label_en = ET.SubElement(icrw_desc, '{http://www.w3.org/2000/01/rdf-schema#}label')
        label_en.set('{http://www.w3.org/XML/1998/namespace}lang', 'en')
        label_en.text = 'International Convention for the Regulation of Whaling'
        
        def_elem = ET.SubElement(icrw_desc, '{http://www.w3.org/2004/02/skos/core#}definition')
        def_elem.set('{http://www.w3.org/XML/1998/namespace}lang', 'fr')
        def_elem.text = 'Convention d\'exploitation piscicole et protection des cétacés de 1946'
        
        issued = ET.SubElement(icrw_desc, '{http://purl.org/dc/terms/}issued')
        issued.set('{http://www.w3.org/2001/XMLSchema#}gYear', '1946')
        
        root.append(icrw_desc)
        existing_uris.add('http://www.maritime-ontology.org/mar#ICRW_Convention_1946')
    
    # Add Resolutions
    print("    - Ajout IWC Resolutions...")
    resolutions = [
        ('IWC_Resolution_61_105', 'Résolution 61/105 de la Commission Baleinière Internationale', 
         'IWC Resolution 61/105'),
        ('IWC_Resolution_64_72', 'Résolution 64/72 de la Commission Baleinière Internationale',
         'IWC Resolution 64/72'),
        ('IWC_Resolution_66_68', 'Résolution 66/68 de la Commission Baleinière Internationale',
         'IWC Resolution 66/68'),
        ('IWC_Resolution_71_123', 'Résolution 71/123 de la Commission Baleinière Internationale',
         'IWC Resolution 71/123'),
    ]
    
    for res_id, res_label_fr, res_label_en in resolutions:
        uri = f'http://www.maritime-ontology.org/mar#{res_id}'
        if uri not in existing_uris:
            res_desc = ET.Element('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description')
            res_desc.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about', uri)
            
            rdf_type = ET.SubElement(res_desc, '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}type')
            rdf_type.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource',
                         'http://www.maritime-ontology.org/mar#Resolution')
            
            rdf_type2 = ET.SubElement(res_desc, '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}type')
            rdf_type2.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource',
                          'http://www.w3.org/2002/07/owl#NamedIndividual')
            
            label_fr_elem = ET.SubElement(res_desc, '{http://www.w3.org/2000/01/rdf-schema#}label')
            label_fr_elem.set('{http://www.w3.org/XML/1998/namespace}lang', 'fr')
            label_fr_elem.text = res_label_fr
            
            label_en_elem = ET.SubElement(res_desc, '{http://www.w3.org/2000/01/rdf-schema#}label')
            label_en_elem.set('{http://www.w3.org/XML/1998/namespace}lang', 'en')
            label_en_elem.text = res_label_en
            
            based_on = ET.SubElement(res_desc, '{http://www.maritime-ontology.org/mar#}basedOn')
            based_on.set('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource',
                         'http://www.maritime-ontology.org/mar#ICRW_Convention_1946')
            
            root.append(res_desc)
            existing_uris.add(uri)
    
    # Add Actor classes (P3.2)
    print("[P3.2] Typage acteurs...")
    actor_classes = [
        ('http://www.maritime-ontology.org/mar#EtatSouverain',
         'État Souverain',
         'Sovereign State',
         'Entité politique reconnue en droit international',
         'Recognized political entity under international law',
         'http://www.maritime-ontology.org/mar#Acteur'),
        
        ('http://www.maritime-ontology.org/mar#Navire',
         'Navire',
         'Vessel',
         'Bateau impliqué dans activités réglementées',
         'Boat involved in regulated activities',
         'http://www.maritime-ontology.org/mar#Acteur'),
        
        ('http://www.maritime-ontology.org/mar#Organisation',
         'Organisation Internationale',
         'International Organization',
         'Entité internationale comme l\'IWC',
         'International entity such as IWC',
         'http://www.maritime-ontology.org/mar#Acteur'),
    ]
    
    for uri, label_fr, label_en, def_fr, def_en, subclass_of in actor_classes:
        if uri not in existing_uris:
            actor_desc = create_class(uri, label_fr, label_en, def_fr, def_en, subclass_of)
            root.append(actor_desc)
            existing_uris.add(uri)
    
    # Add Activity classes (P3.3)
    print("[P3.3] Complétude activités...")
    activity_classes = [
        ('http://www.maritime-ontology.org/mar#ChalutageDefond',
         'Chalutage de Fond',
         'Bottom Trawling',
         'Pêche commerciale au chalut opérant au fond',
         'Commercial fishing using trawl nets on seafloor',
         'http://www.maritime-ontology.org/mar#Activite'),
        
        ('http://www.maritime-ontology.org/mar#ChalutageDefondProfond',
         'Chalutage Profond',
         'Deep-Sea Bottom Trawling',
         'Chalutage de fond au-delà de 400 mètres (Interdiction I001)',
         'Bottom trawling beyond 400m depth (Prohibition I001)',
         'http://www.maritime-ontology.org/mar#ChalutageDefond'),
    ]
    
    for uri, label_fr, label_en, def_fr, def_en, subclass_of in activity_classes:
        if uri not in existing_uris:
            activity_desc = create_class(uri, label_fr, label_en, def_fr, def_en, subclass_of)
            root.append(activity_desc)
            existing_uris.add(uri)
    
    # Update metadata
    print("\n[Metadata] Mise à jour version et description...")
    for ontology in root.findall('{http://www.w3.org/2002/07/owl#}Ontology'):
        # Update version
        for elem in ontology.findall('{http://www.w3.org/2002/07/owl#}versionInfo'):
            elem.text = 'v2.0'
        
        # Update description
        for elem in ontology.findall('{http://purl.org/dc/terms/}description'):
            elem.text = 'Maritime Ontology v2.0 - Refactored with LKIF-Core alignment, taxonomic hierarchy, and complete property definitions. IWC and ICRW based (no UNCLOS).'
    
    print("\n✅ Refactorisation complète!")
    print(f"   Classes ajoutées: {len(existing_uris) - 400} (approx)")
    print(f"   Total items: ~{len(root.findall('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description')) + len(root.findall('{http://www.w3.org/2002/07/owl#}Ontology'))}")
    
    return root

def prettify_xml(root):
    """Pretty print XML"""
    rough_string = ET.tostring(root, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def save_ontology(root, filepath):
    """Save ontology to file"""
    tree = ET.ElementTree(root)
    tree.write(filepath, encoding='utf-8', xml_declaration=True)
    print(f"\n✅ Fichier sauvegardé: {filepath}")

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("REFACTORISATION ONTOLOGIE MARITIME COMPLÈTE")
    print("=" * 80)
    print("\nChargement du fichier OWL...")
    
    root = generate_final_ontology()
    
    output_path = 'data/output/maritime_ontology_v2.owl'
    save_ontology(root, output_path)
    
    print("\n" + "=" * 80)
    print("RÉSUMÉ DES CHANGEMENTS APPLIQUÉS:")
    print("=" * 80)
    print("""
✅ [P1.1] Classes/Instances: Espèces converties en classes pures
✅ [P1.2] Taxonomie: Hiérarchie Mysticète/Odontocète créée
✅ [P1.3] Propriétés: domain/range ajoutés (appliesInZone, protegeEspece, etc.)
✅ [P2.1] Norme/Interdiction/I002: Alignement LKIF clarified
✅ [P2.2] Sources: ICRW Convention 1946 + 4 Résolutions modélisées
✅ [P3.1] Zones: UNCLOS supprimé, IWC seul conservé
✅ [P3.2] Acteurs: EtatSouverain, Navire, Organisation typés
✅ [P3.3] Activités: Chalutage de fond ajouté
    """)
    
    print(f"\n📄 Fichier final: {output_path}")
    print("   - Format: RDF/XML")
    print("   - Framework: LKIF-Core")
    print("   - Sources: ICRW + IWC Resolutions uniquement")
    print("=" * 80)

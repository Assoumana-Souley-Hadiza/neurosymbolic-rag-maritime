import rdflib
from rdflib.namespace import OWL, RDF, RDFS

g = rdflib.Graph()
g.parse("output/ontologie/maritime_ontology.owl", format="xml")

undefined_classes = set()
undefined_props = set()

for s, p, o in g:
    if p == RDF.type and isinstance(o, rdflib.URIRef):
        if (o, RDF.type, OWL.Class) not in g and "w3.org" not in o and "lkif" not in o:
            undefined_classes.add(o)
    if isinstance(p, rdflib.URIRef) and "w3.org" not in p and "lkif" not in p:
        if (p, RDF.type, OWL.ObjectProperty) not in g and (p, RDF.type, OWL.DatatypeProperty) not in g and (p, RDF.type, OWL.AnnotationProperty) not in g:
            undefined_props.add(p)

print("Undefined classes:", undefined_classes)
print("Undefined props:", undefined_props)

"""
Test the VIVO data model.
"""

import nose

import rdflib
from . import vivo

import logging
logging.basicConfig(level=logging.DEBUG)

raw = vivo.turtle_prefixes + u"""
bu:jcarberry
    a  vivo:FacultyMember , blocal:BrownThing ;
    rdfs:label "Carberry, Josiah" ;
    foaf:firstName "Josiah" ;
    foaf:lastName "Carberry" ;
    blocal:shortId "jcarberry" .
"""

def test_init_graph():
    g = vivo.init_graph()
    namespaces = [e for e in g.namespaces()]
    assert ('blocal', rdflib.term.URIRef(u'http://vivo.brown.edu/ontology/vivo-brown/'))\
        in\
        namespaces
    assert ('vivo', rdflib.term.URIRef(u'http://vivoweb.org/ontology/core#'))\
        in\
        namespaces

def test_select_query():
    v = vivo.VGraph()
    v.parse(data=raw, format='turtle')
    q = """
    select ?firstName
    where { ?f a vivo:FacultyMember ;
               foaf:firstName ?firstName . }
    """
    for row in v.select(q):
        assert row.firstName.toPython() == u'Josiah'

def test_select_query_with_bindings():
    v = vivo.VGraph()
    v.parse(data=raw, format='turtle')
    q = """
    select ?firstName
    where { ?f a vivo:FacultyMember ;
               foaf:firstName ?firstName . }
    """
    for row in v.select(q, bind={'f': 'bu:jcarberry'}):
        assert row.firstName.toPython() == u'Josiah'

def test_construct_query():
    """
    Create a new Graph.
    """
    v = vivo.VGraph()
    q = """
    construct {
        ?f a foaf:Person .
    }
    where {}
    """
    new_data = v.construct(q, bind={'f': 'bu:jcarberry'})
    #Make sure we get back what we added.
    for r in new_data.subjects(predicate=rdflib.RDF.type, object=vivo.FOAF.Person):
        assert vivo.BU['jcarberry'] == r

def test_construct_modify():
    """
    Modify an existing Graph.
    """
    v = vivo.VGraph()
    v.parse(data=raw, format='turtle')
    q = """
    construct {
        ?f a foaf:Person
    }
    where {
        ?f a vivo:FacultyMember
    }
    """
    new_data = v.construct(q)
    for r in new_data.subjects(predicate=rdflib.RDF.type, object=vivo.FOAF.Person):
        assert vivo.BU['jcarberry'] == r



if __name__ == '__main__':
    nose.main()
"""
Requires access to a VIVO instance and the environment
variables in setvivoenv.sh to be set.

run as
$nosetests test_web_client.py

"""

import nose

from tempfile import NamedTemporaryFile

from rdflib import Graph, Literal

from vivo_utils import sparql, web_client

sparql = sparql.VIVOSparql()
sparql.login()

def get_vivo_data():
    #Check if the resource is available via a SPARQL query
    q = """
    DESCRIBE <http://vivo.school.edu/individual/place-tmp123>
    """
    sparql.setQuery(q)
    results = sparql.results_graph()
    return results

def query_vivo(vivo_data):
    exists = vivo_data.query('\
    select ?label\
    where {\
        <http://vivo.school.edu/individual/place-tmp123> rdfs:label ?label .\
    }', initNs={'rdfs': 'http://www.w3.org/2000/01/rdf-schema#'})
    return exists


def test_add_remove_rdf():
    g = Graph()
    test_graph = """
    @prefix core:    <http://vivoweb.org/ontology/core#> .
    @prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
    <http://vivo.school.edu/individual/talk-tmp123>
          rdfs:label "Temporary talk" ;
          core:hasGeographicLocation
                  <http://vivo.school.edu/individual/place-tmp123> .

    <http://vivo.school.edu/individual/place-tmp123>
          rdfs:label "Temporary place" ;
          core:geographicLocationOf <http://vivo.school.edu/individual/talk-tmp123> .
    """
    g.parse(data=test_graph, format='n3')

    vs = web_client.Session()
    vs.login()
    #To be sure, data doesn't exist, remove it.
    with NamedTemporaryFile() as f:
        g.serialize(destination=f.name, format='n3')
        vs.remove_rdf(f.name)

    with NamedTemporaryFile() as f:
        g.serialize(destination=f.name, format='n3')
        vs.add_rdf(f.name)

    data = get_vivo_data()
    exists = query_vivo(data)

    #Make sure data is there.
    for label, in exists:
        assert label == Literal(u'Temporary place')
        break

    #Remove it
    with NamedTemporaryFile() as f:
        g.serialize(destination=f.name, format='n3')
        vs.remove_rdf(f.name)

    #Make sure data isn't there.
    data = get_vivo_data()
    exists = query_vivo(data)
    assert exists.bindings == []

    vs.logout()

    sparql.logout()

if __name__ == '__main__':
    nose.main()

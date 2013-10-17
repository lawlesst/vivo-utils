"""
Helpers for working with VIVO data.
"""
import string
import uuid


#RDFlib
import rdflib
from rdflib import Namespace, ConjunctiveGraph, Graph, URIRef, RDFS
from rdflib.namespace import NamespaceManager, ClosedNamespace

#logging
import logging

#named graphs for data loading
kb2 = URIRef('http://vitro.mannlib.cornell.edu/default/vitro-kb-2')

#setup namespaces
#code inspired by / borrowed from https://github.com/libris/librislod
#local data namespace
BU = Namespace('http://vivo.brown.edu/individual/')
#local ontology
BLOCAL = Namespace('http://vivo.brown.edu/ontology/vivo-brown/')
BIBO = Namespace('http://purl.org/ontology/bibo/')
DCTERMS = Namespace('http://purl.org/dc/terms/')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
VIVO = Namespace('http://vivoweb.org/ontology/core#')
VITROPUBLIC = Namespace('http://vitro.mannlib.cornell.edu/ns/vitro/public#')
VITRO = Namespace('http://vitro.mannlib.cornell.edu/ns/vitro/0.7#')
OWL = rdflib.OWL

namespaces = {}
for k, o in vars().items():
    if isinstance(o, (Namespace, ClosedNamespace)):
        namespaces[k] = o

ns_mgr = NamespaceManager(Graph())
for k, v in namespaces.items():
    ns_mgr.bind(k.lower(), v)

rq_prefixes = u"\n".join("prefix %s: <%s>" % (k.lower(), v)
                         for k, v in namespaces.items())

prefixes = u"\n    ".join("%s: %s" % (k.lower(), v)
                          for k, v in namespaces.items()
                          if k not in u'RDF RDFS OWL XSD')

turtle_prefixes = u"\n".join("@prefix %s: <%s> ." % (k.lower(), v)
                         for k, v in namespaces.items())
#namespace setup complete

def init_graph(graph_type=None):
    """
    Helper to initialize a VIVO graph with
    namespace manager.
    """
    if graph_type == 'conjunctive':
        g = ConjunctiveGraph()
    else:
        g = Graph()
    g.namespace_manager = ns_mgr
    return g

def make_uuid_uri(ns, prefix='n'):
    """
    Create a unique url.
    """
    u = str(uuid.uuid1())
    if prefix is not None:
        uri = URIRef("%s%s%s" % (ns, prefix, u))
    else:
        uri = URIRef(ns + u)
    return uri

class SPARQLTemplate(string.Template):
    """
    Template for processing SPARQL queries
    from Python strings."""
    delimiter = '?'
    idpattern = '[a-z]+'

def prep_query(raw, replace_dict, add_prefixes=False):
    t = SPARQLTemplate(raw)
    transformed = t.safe_substitute(replace_dict)
    if add_prefixes == True:
        return rq_prefixes + transformed
    return transformed

class VGraph(Graph):

    def __init__(self):
        Graph.__init__(self, namespace_manager=ns_mgr)

    def construct(self, query, bind={}):
        """
        Returns a new Graph with data returned
        by the construct query.

        Pass in a dictionary bind with values to replace
        in the query
        """
        out = init_graph()
        prepped_query = prep_query(query, bind)
        logging.debug(prepped_query)
        results = self.query(prepped_query)
        if results.graph is None:
            return
        else:
            out += results.graph
            return out

    def select(self, query, bind={}):
        """
        Return RDFLib SPARQL query results for the query.

        Pass in a dictionary bind with values to replace
        in the query.
        """
        prepped_query = prep_query(query, bind)
        logging.debug(prepped_query)
        return self.query(prepped_query)
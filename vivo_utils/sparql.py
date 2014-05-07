"""
A subclass of SPARQLWrapper that will work with the built-in
SPARQL admin interface that comes with VIVO.

At the moment, will only return RS_JSON for SELECT and
N3 for CONSTRUCT queries.

"""
import csv
from StringIO import StringIO
import urllib
import urllib2
import warnings

from rdflib import Graph

from SPARQLWrapper import SPARQLWrapper, JSON, N3
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed, EndPointNotFound, EndPointInternalError
from SPARQLWrapper.Wrapper import _SPARQL_JSON

#VIVO returns its RS_JSON as application/javascript
_SPARQL_JSON.append('application/javascript')

from web_client import Session

#logging
import logging
_logger = logging.getLogger(__name__)


class VIVOSparql(SPARQLWrapper):
    """
    Extension of SPARQLWrapper to work with the built-in VIVO
    SPARQL query interface.  Eliminates the need to use Fuseki
    for SPARQL non-update queries.
    """

    def __init__(self, **kwargs):
        self.url = kwargs.get('url')
        if self.url:
            self.vweb = Session()
        else:
            self.vweb = Session()
        self.session = None
        #Add the VIVO SPARQL end point path to the VIVO url.
        self.endpoint = self.vweb.url + 'admin/sparqlquery'
        SPARQLWrapper.__init__(self, self.endpoint, kwargs)
        #The resultFormat and rdfResultFormat are required
        #parameters for the VIVO SPARQL interface.
        #This are set to RS_JSON for SELECT and
        #N3 for CONSTRUCT.  These can be overridden when
        #called but have not been tested.
        self.addCustomParameter('resultFormat', 'RS_JSON')
        self.addCustomParameter('rdfResultFormat', 'N3')
        self.format = None
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')

    def login(self):
        """
        Login to the VIVO web interface.
        """
        kw = {}
        if self.username is not None:
            kw['username'] = self.username
        if self.password is not None:
            kw['password'] = self.password
        self.vweb.login(**kw)
        self.session = self.vweb.session
        self.cookies = urllib.urlencode(self.session.cookies)

    def logout(self):
        """
        End the VIVO web session.
        """
        self.vweb.logout()

    def setQuery(self, query):
        """
        Handle query response format by looking at the response type.
        """
        if ('construct' in query.lower()) or\
                ('describe' in query.lower()):
            self.setReturnFormat(N3)
        elif 'select' in query.lower():
            if self.format != 'csv':
                self.setReturnFormat(JSON)
        #else:
        #    raise Exception("Query type not supported.\
        #    Options are CONSTRUCT, SELECT, DESCRIBE.")
        SPARQLWrapper.setQuery(self, query)

    def _query(self):
        """
        Override _query method to use cookies acquired on login.
        """
        request = self._createRequest()
        try:
            opener = urllib2.build_opener()
            opener.addheaders.append(('Cookie', self.cookies))
            response = opener.open(request)
            return (response, self.returnFormat)
        except urllib2.HTTPError, e:
            if e.code == 400:
                raise QueryBadFormed()
            elif e.code == 404:
                raise EndPointNotFound()
            elif e.code == 500:
                raise EndPointInternalError(e.read())
            else:
                raise e
            return (None, self.returnFormat)

    def results_graph(self):
        """
        Shortcut for use with CONSTRUCT queries.  Returns
        results as an RDFLib graph.
        """
        resp, rformat = self._query()
        if rformat == 'N3':
            rformat = 'n3'
        g = Graph()
        g.parse(resp, format=rformat)
        return g

    def results_csv(self, query, filename='results.csv'):
        """
        Shortcut for use with SELECT queries.  Outpus
        as CSV file.
        """
        #Hide warnings.  CSV isn't recognized by SPARQLWrapper.
        warnings.simplefilter("ignore")
        format = 'vitro:csv'
        self.addCustomParameter('resultFormat', format)
        self.format = 'csv'
        self.setQuery(query)
        results = self.queryAndConvert()
        rows = csv.reader(StringIO(results.read()))
        with open(filename, 'wb') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        return True




if __name__ == "__main__":
    #Simple query to see if all is working as expected.
    q = """
    PREFIX vivo: <http://vivoweb.org/ontology/core#>
    SELECT *
    WHERE {?s a vivo:FacultyMember}
    LIMIT 3
    """
    sparql = VIVOSparql()
    sparql.login()
    sparql.setQuery(q)
    print sparql.queryAndConvert()
    sparql.logout()

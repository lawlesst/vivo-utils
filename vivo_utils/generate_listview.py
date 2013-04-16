"""
Utility for developing listViewConfig queries.

More details are available at: http://lawlesst.github.io/notebook/vivo-listview.html

"""
from pprint import pprint
import optparse
import re
import xml.etree.ElementTree as ET

from rdflib import Graph
from rdflib.namespace import split_uri

#logging
import logging
_logger = logging.getLogger(__name__)

#Setup VIVO's SPARQL endpoint
from sparql import VIVOSparql

#Regex
SELECT_QUERIES = re.compile("SELECT DISTINCT\s+(\?.*) WHERE \{", re.DOTALL)


def pre_process_listview(listview_file):
    with open(listview_file) as raw_file:
        raw = raw_file.read()
        list_view_xml = raw.replace(
            '<collated>', '')\
            .replace('</collated>', '')\
            .replace('<critical-data-required>', '')\
            .replace('</critical-data-required>', '')
    return list_view_xml


def process_listview_select(tree):
    select = tree.findall('query-select')[0].text
    #Pull out the fields from the select queries and use
    #to put results in a list of dictionaries that's easier to read.
    field_list = [
        r.strip().replace('\n', '')
        for r in re.search(SELECT_QUERIES, select).groups()[0].replace('\n', ' ').split('?') if r.strip() != ''
    ]
    return (select, field_list)


def main():
    p = optparse.OptionParser()
    p.add_option('-s', '--subject', help="Subject for query.")
    p.add_option('-p', '--property', help="Property for query.")
    p.add_option('-m', '--max', help="Maximum number of results to return.")
    config, arguments = p.parse_args()
    sparql = VIVOSparql()
    sparql.login()

    listview_file = arguments[0]

    #Determine if the property has a namespace prefix or not.
    qproperty = config.property
    prefix, prop = split_uri(unicode(config.property))
    if prefix.startswith('http'):
        #Adjust for full uri for property
        qproperty = "<{0}>".format(qproperty)

    #'core:authorInAuthorship'
    bindings = {
        'subject': '<{0}>'.format(config.subject),
        'property': '{0}'.format(qproperty),
    }

    g = Graph()

    list_view_xml = pre_process_listview(listview_file)

    root = ET.fromstring(list_view_xml)
    #Parse and execute SPARQL constructs.
    for construct_query in root.findall('query-construct'):
        query = construct_query.text\
            .replace('?subject', bindings['subject'])\
            .replace('?property', bindings['property'])
        _logger.debug('SPARQL:\n%s' % query)
        sparql.setQuery(query)
        results = sparql.queryAndConvert()
        g.parse(data=results, format='n3')

    select_query, field_list = process_listview_select(root)

    _logger.debug('FINAL SPARQL SELECT:\n%s' % select_query)
    results_list = []
    for row in g.query(select_query):
        pretty_dict = dict(zip(field_list, row))
        results_list.append(pretty_dict)
    
    pprint(results_list)

    sparql.logout()

if __name__ == "__main__":
    main()

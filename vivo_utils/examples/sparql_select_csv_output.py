
from vivo_utils import sparql

sparql = sparql.VIVOSparql()
sparql.login()

query = """
SELECT ?s ?p
WHERE
{
      ?s ?p <http://vivo.brown.edu/individual/org-new-york-academy-medicine>
}
"""

sparql.results_csv(query)

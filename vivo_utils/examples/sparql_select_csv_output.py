
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

#Optionally pass in a filename or path to save the results to CSV.
#By default results will be saved to the current directory as results.csv
sparql.results_csv(query, filename="/tmp/myresults.csv")

sparql.logout()

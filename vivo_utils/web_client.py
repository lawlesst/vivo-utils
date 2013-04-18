#!../venv/bin/python

"""
Login to the Vivo web app and post RDF files for 'Add' and 'Remove'.

This serves the purpose of bulk updating and deleting.  Since
it uses the web interface directly, the reasoning and Solr indexing
will be triggered.

Writing directly to the models with Jena doesn't allow for that.

"""


import optparse
import os
import sys
import urllib

import requests

#logging
import logging
_logger = logging.getLogger(__name__)


class Session(object):

    def __init__(self, **kwargs):
        self.session = requests.session()
        self.url = self._get_vivo_url()

    def _get_vivo_url(self):
        """Helper to make sure trailing slash
        is found in VIVO url.
        """
        vurl = os.getenv('VIVO_URL').rstrip('/') + '/'
        return vurl

    def login(self):
        """
        Login to the VIVO web interface.
        """
        payload = {
            'loginName': os.getenv('VIVO_USER'),
            'loginPassword': os.getenv('VIVO_PASS'),
            'loginForm': 'Log in'
        }
        self.session.post(
            self.url + 'authenticate',
            data=payload,
            verify=False
        )
        self.cookies = urllib.urlencode(self.session.cookies)

    def logout(self):
        """
        End the VIVO web session.
        """
        resp = self.session.get(self.url + 'logout', verify=False)
        #Check response history for logout.
        logout_resp = resp.history[0]
        if logout_resp.status_code == 302:
            return True
        else:
            raise Exception('Logout failed.')


def get_name_extension(path):
    """
    Get the file name and extension for a given filename or path.
    """
    #Let's normalize the path
    norm_path = os.path.normpath(path)
    root, ext = os.path.splitext(norm_path)
    #Get the trailing
    name = root.split(os.path.sep)[-1]
    #Strip leading period from extension
    ext = ext.lstrip('.')
    return (name, ext)


def add_rdf(file_path, format='N3'):
    filename, extension = get_name_extension(file_path)
    vs = Session()
    vs.login()
    base_url = vs.url
    payload = dict(
        language=format,
        submit='Load Data',
        action='loadRDFData',
    )
    p = vs.session.post(
        base_url + 'uploadRDF',
        verify=False,
        data=payload,
        files={'rdfStream': (filename, open(file_path, 'rb'))}
    )
    #All posts seem to return a 200.  Should check for messages that
    #indicate something went wrong.
    #Success: RDF upload successful.
    #Error: Could not load from file:
        #edu.cornell.mannlib.vitro.webapp.rdfservice.
        #RDFServiceException: com.hp.hpl.jena.shared.JenaException:
        #org.xml.sax.SAXParseException: The element type "link"
        #must be terminated by the matching end-tag "".
    print>>sys.stderr, "Adding %s to %s." % (file_path, base_url)
    if p.status_code != 200:
        raise Exception('Error adding RDF.  Check Vivo log.\n%s' % p.content)
    vs.logout()
    return True


def remove_rdf(file_path, format='N3'):
    filename, extension = get_name_extension(file_path)
    vs = Session()
    vs.login()
    base_url = vs.url
    payload = dict(
        mode='remove',
        language=format,
        submit='submit',
    )
    p = vs.session.post(
        base_url + 'uploadRDF',
        verify=False,
        data=payload,
        files={'rdfStream': (filename, open(file_path, 'rb'))},
        headers={'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'}
    )
    print>>sys.stderr, "Removing %s from %s." % (file_path, base_url)
    #Here we can actually look for this text:
    #Removed RDF from file post_sample.n3. Removed 1 statements.
    if p.status_code != 200:
        raise Exception('Error removing RDF.  Check Vivo log.\n%s' % p.content)
    vs.logout()
    return True


def recompute_inferences(config):
    """
    -authenticate
    -post to address
    - look for text on returned page
    """
    vs = Session()
    vs.login()
    base_url = vs.url
    #Recompute of inferences started. See vivo log for further details.
    print>>sys.stderr, 'Recomputing inferences for %s.' % base_url
    r = vs.session.post(
        base_url + 'RecomputeInferences',
        data={'submit': 'Recompute Inferences'}
    )
    if r.content.find('Recompute of inferences started.\
                    See vivo log for further details.') == -1:
        raise Exception("Rebuilding inferences failed")
    vs.logout()
    return True


def rebuild_index(config):
    """
    Logs into Vivo and submits a Rebuild Index command.

    This tool does not wait for the index to finish rebuilding.
    """
    s = Session()
    s.login()
    base_url = s.url
    s = requests.session()
    r = s.post(
        base_url + 'SearchIndex',
        data={
            'rebuild': 'Rebuild'
        }
    )
    #Find the confirmation - Preparing to rebuild the search index.
    if r.content.find('the search index') == -1:
        raise Exception('Rebuilding search index failed.\
                Check Vivo log and admin pages.')
    s.logout()
    return True


def merge_individuals(uri1, uri2, session=None):
    """
    Use the merge tool to merge individual resources.
    """
    if session is not None:
        s = session
    else:
        s = Session()
        s.login()
    base_url = s.url
    params = {'action': 'mergeResources',
              'uri1': uri1,
              'uri2': uri2,
              'usePrimaryLabelOnly': 'Use Primary Label Only',
              'submit': 'Merge resources'}
    merge = s.session.get(base_url + 'ingest', params=params)
    if merge.url == base_url + 'authenticate':
        raise Exception("Failed to login to VIVO.")
    if merge.status_code != 200:
        raise Exception("Merge failed; requests output: %s" % merge.content)
    s.logout()
    return True


def created_named_graph(name, session=None):
    """action:createModel
    modelName:http://localhost/staged
    submit:Create Model
    modelType:sdb"""
    s = Session()
    s.login()
    params = {
        'action': 'createModel',
        'modelName': name,
        'submit': 'Create Model',
        'modelType': 'sdb',
    }
    r = s.session.post(s.url + 'ingest', data=params)
    if r.status_code != 200:
        raise Exception('Action failed:\n{0}'.format(r.content))
    print r.content
    print r.url
    return


def remove_named_graph(name, session=None):
    """action:createModel
    modelName:http://localhost/staged
    submit:Create Model
    modelType:sdb"""
    s = Session()
    s.login()
    params = {
        'action': 'removeModel',
        'modelName': name,
        'submit': 'remove',
        'modelType': 'sdb',
    }
    s.session.post(s.url + 'ingest', data=params)
    return


def clear_named_graph(name, session=None):
    """action:clearModel
    modelName:http://localhost/staged
    modelType:sdb
    submit:clear statements"""
    s = Session()
    s.login()
    params = {
        'action': 'clearModel',
        'modelName': name,
        'submit': 'clear statements',
        'modelType': 'sdb',
    }
    s.session.post(s.url + 'ingest', data=params)
    return


def add_rdf_to_named_graph(file_path, model_name, format='N3'):
    filename, extension = get_name_extension(file_path)
    vs = Session()
    vs.login()
    base_url = vs.url
    payload = dict(
        language=format,
        submit='Load Data',
        modelName=model_name,
        docLoc='',
    )
    print payload
    p = vs.session.post(
        base_url + 'uploadRDF',
        verify=False,
        data=payload,
        files={'filePath': (filename, open(file_path, 'rb'))}
    )
    print p.url
    print p.status_code
    print p.headers
    if p.status_code != 200:
        raise Exception('Error adding RDF.  Check Vivo log.\n%s' % p.content)
    vs.logout()
    return True



def main():
    p = optparse.OptionParser()
    p.add_option('--file', help="File to load or remove.  Used for add and remove RDF only.")
    p.add_option('--format', default='N3', help="Format for the loaded or removed RDF.  Defaults to N3.")
    p.add_option('--uri1', help="Primary uri for merging.")
    p.add_option('--uri2', help="Secondary uri for merging.")
    config, arguments = p.parse_args()

    if len(arguments) == 0:
        raise Exception("No action specified.  Options are recompute, rebuild, add, remove, merge.")

    #Handle commands.
    for arg in arguments:
        if 'recompute' in arg:
            recompute_inferences(config)
        elif 'rebuild' in arg:
            rebuild_index(config)
        elif 'add' in arg:
            add_rdf(config.file, format=config.format)
        elif 'remove' in arg:
            remove_rdf(config.file, format=config.format)
        elif 'merge' in arg:
            merge_individuals(config.uri1, config.uri2)

if __name__ == "__main__":
    main()


---

#### No longer maintained

```These tools are longer maintained or up-to-date with the current version of [VIVO](http://vivoweb.org/). Please see the [VIVO wiki](https://wiki.duraspace.org/display/VIVO/Community+Projects) for community developed tools.```

---

Tools for ingesting and managing VIVO data with Python.

### Installation

* Requires Python 2.6 or 2.7.
* Requires [pip](https://pypi.python.org/pypi/pip)
* Requires git

Run
~~~
$ pip install git+https://github.com/lawlesst/vivo-utils.git
~~~
Edit setvivoenv.sh to match your VIVO web application and run
~~~
$ source setvivoenv.sh
~~~

### How will this be useful for my VIVO project? 

* If you want to run SPARQL queries from scripts against the VIVO web application but do not have a separate SPARQL endpoint, like Fuseki, setup.
* If you want to automate adding and removing data through the VIVO web application, which will trigger the VIVO inferencing and reasoning.
* If you want to automate merging of URIs. 
* If you want to write customized listViewConfigs but want to experiment with queries before adding the config to the web application.


Note: there is an [RDF web service api](https://wiki.duraspace.org/display/VIVO/RDFServiceRequest+API) planned for VIVO/Vitro 1.6.
Once that is available, this code will be updated to work with that.  

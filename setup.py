from distutils.core import setup


setup(
    name='VIVO utils',
    version='0.1',
    packages=['vivo_utils',],
    description='Tools for ingesting and managing VIVO data.',
    long_description=open('README.md').read(),
    author='Ted Lawless',
    author_email='tlawless@brown.edu',
    install_requires=['requests', 'rdflib'],
    dependency_links = ['https://github.com/RDFLib/rdflib-sparql/tarball/master#egg=rdflib-sparql==0.2-dev'],
    entry_points={
        'console_scripts': [
            'generateListView = vivo_utils.generate_list_view:main',
        ]
    }
)
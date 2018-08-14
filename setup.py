from setuptools import setup

setup(name='qoma_smuggler',
        scripts=['scripts/smuggler_test.py'],    
        version='0.0.1',
        py_modules= ['qoma_smuggler'],
        description='Qoma Utilities for Python HLI',
        long_description='Qoma Utilities for Python interface to FIS Marketmap FAME HLI',
        install_requires=['numpy>=1.13.3','pandas>=0.23.4','pyhli>=0.0.11'],
        author='Qoma LLC',
        author_email='info@qoma.io',
        url='http://github.com/qomaio',
        license='AGPLv3',
        platforms=['any']
)

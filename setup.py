from setuptools import setup

setup(name='qoma_smuggler',
        python_requires='>=2.7.5,>=3.6.5',
        scripts=['scripts/smuggler_test.py'],    
        version='0.0.2',
        py_modules= ['qoma_smuggler'],
        description='Transport Data and Commands Across the FAME / Python Border',
        long_description='Transport data and commands across the FAME / Python border. '+
        'A set of utilities for: reading FAME databases into R; writing '+
        'Python data into FAME databases; executing FAME commands in the Python environment; and, executing ' +
        'Python commands in the FAME environment.',
        install_requires=['numpy>=1.13.3','pandas>=0.23.4','pyhli>=0.0.11'],
        author='Qoma LLC',
        author_email='info@qoma.io',
        url='http://github.com/qomaio',
        license='AGPLv3',
        platforms=['any'],
        include_package_data=True)

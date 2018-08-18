# Qoma Smuggler

Transport data and commands across the FAME / Python border.
    A set of utilities for: 
    
* reading FAME databases into Python; 
* writing Python data into FAME databases; 
* executing FAME commands in Python environment; and, 
* executing Python commands in the FAME environment.

## Prerequisites

* Install Python (>=3.6), Scipy and Jupyter Notebook. Consider
    * [Anaconda](https://www.anaconda.com/download/) or
    * [Docker](https://hub.docker.com/r/jupyter/scipy-notebook/)
* Install FAME and successfully enter and exit the FAME 4GL environment.
    
## Installation and testing

* `pip install qoma-smuggler`
* `python /opt/pkg/anaconda3/bin/smuggler_test.py`

Your Python scripts directory may be somewhere other than `/opt/pkg/anaconda3/bin/`.  A quick trick to find the test script is `pip uninstall qoma-smuggler`, then respond `n` to the confirmation prompt.  Your script directory will be displayed to your terminal.

On first use, you will be directed to a website to obtain a `QOMA_PIN` which will entitle you to use the [pyhli](https://github.com/qomaio/pyhli) for the duration of your FAME license.

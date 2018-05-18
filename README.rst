document_extractor
===========================================

command line utility to load documents into files.
-------------------------------------------

.. image:: https://secure.travis-ci.org/imalkevich/document_extractor.png?branch=master
        :target: https://travis-ci.org/imalkevich/document_extractor

.. image:: https://codecov.io/github/imalkevich/document_extractor/coverage.svg?branch=master
    :target: https://codecov.io/github/imalkevich/document_extractor
    :alt: codecov.io

This tool loads content from <paratext> elements of document XML into files. 
Already loaded documents are ignored.

Installation
------------

::

    pip install document_extractor

or

::

    python setup.py install

Usage
-----
::

    python -m extractor.loader

    usage: loader.py [-h] [-f FILE] [-v]

    load documents and extract text

    optional arguments:
    -h, --help            show this help message and exit
    -f FILE, --file FILE  file with document guids
    -v, --version         displays the current version of errorguimonitor

Utilities
---------
::
    kill the process in PowerShell  Stop-Process -Id (Get-NetTCPConnection -LocalPort 8088).OwningProcess -Force

Author
------

-  Ihar Malkevich (imalkevich@gmail.com)
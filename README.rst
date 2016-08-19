molo.servicedirectory
=============================

A molo module for calling service directory.

The following keys should be set in the django projects settings file (the values are only examples):

SERVICE_DIRECTORY_API_BASE_URL = 'http://0.0.0.0:8000/api/'

SERVICE_DIRECTORY_API_USERNAME = 'root'
SERVICE_DIRECTORY_API_PASSWORD = 'admin'

GOOGLE_PLACES_API_SERVER_KEY = 'thisisnotarealkeyreplaceitwithyourown'

ideally things like the passwords and api keys should be kept out of the repository and possibly included in the
settings through importing from a secrets file that is ignored by the version control.

eg in settings.py:

try:
    from secrets import *
except ImportError:
    raise


.. image:: https://img.shields.io/travis/praekelt/molo.servicedirectory.svg
        :target: https://travis-ci.org/praekelt/molo.servicedirectory

.. image:: https://img.shields.io/pypi/v/molo.servicedirectory.svg
        :target: https://pypi.python.org/pypi/molo.servicedirectory

.. image:: https://coveralls.io/repos/praekelt/molo.servicedirectory/badge.png?branch=develop
    :target: https://coveralls.io/r/praekelt/molo.servicedirectory?branch=develop
    :alt: Code Coverage

.. image:: https://readthedocs.org/projects/molo.servicedirectory/badge/?version=latest
    :target: https://molo.servicedirectory.readthedocs.org
    :alt: molo.servicedirectory Docs



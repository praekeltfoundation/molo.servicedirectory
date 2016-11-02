molo.servicedirectory
=====================

A Molo module that adds a service directory.

In short it's a searchable directory that contains services, which are represented by keywords (eg: 'HIV'),
that themselves are organised into categories (eg: 'Health'). Said services are provided by organisations.

Users can search on service keyword or category, as well as organisation name. As part of the flow the
user is prompted for a location, which is turned into coordinates through the Google Places API and used
to order the results based on proximity of the user to the found organisations.

Installation
============

It's assumed that you're already familiar with `Molo`_, this being a Molo plugin.

Currently the installation is **quite complicated**. Please bear with us as the standalone version of
molo.servicedirectory is a work in progress.

Also have a look at ``test_settings.py`` - this file is copied into a scaffolded (`Scaffolding a site using Molo`_)
test app by the build and shows the various settings and how they should look.
You can use the same process to set up a standalone local Django application with Molo and the servicedirectory
plugin. See ``.travis.yml`` and run the commands from the ``install`` and ``script`` sections.

.. _Scaffolding a site using Molo: http://molo.readthedocs.io/getting-started.html#scaffold-a-site-using-molo

Prerequisites
-------------

You need to have an Elasticsearch 1.x server up and running. The 1.x limitation is due to Haystack not
supporting newer versions yet. See the `Installing Search Engines`_ documentation.

.. _Installing Search Engines: http://django-haystack.readthedocs.io/en/latest/installing_search_engines.html#elasticsearch

Installation Steps
------------------

You can install molo.servicedirectory using pip. In addition you'll have to do the following:

1. Add each of the following to your ``INSTALLED_APPS``:

    1. ``molo.servicedirectory``
    2. ``djgeojson``
    3. ``leaflet``
    4. ``import_export``
    5. ``haystack``

2. Add ``molo.servicedirectory.middleware.HaystackBatchFlushMiddleware`` to the **top** of your ``MIDDLEWARE_CLASSES``.

3. Add a ``HAYSTACK_CONNECTIONS`` setting:

    1. See the section on modifying your settings.py for Elasticsearch in the `Getting Started with Haystack`_ tutorial.
    2. Set the ``ENGINE`` key of your Haystack connection to ``molo.servicedirectory.haystack_elasticsearch_raw_query.custom_elasticsearch.ConfigurableElasticSearchEngine``.

4. Add a ``HAYSTACK_SIGNAL_PROCESSOR`` setting with the value ``molo.servicedirectory.signal_processors.BatchingSignalProcessor``.

5. Add a ``GOOGLE_PLACES_API_SERVER_KEY`` setting (you can get a key from the `Google Developers Console`_).

6. Add a ``GOOGLE_ANALYTICS_TRACKING_ID`` setting

7. Add settings for the Vumi Go API:

    1. ``VUMI_GO_ACCOUNT_KEY``
    2. ``VUMI_GO_CONVERSATION_KEY``
    3. ``VUMI_GO_API_TOKEN``
    4. ``VUMI_GO_API_URL``

8. Add a ``LEAFLET_CONFIG`` setting that looks like this:

    LEAFLET_CONFIG = {
        'SPATIAL_EXTENT': (-180, -90, 180, 90)
    }

9. Include the ``molo.servicedirectory`` URLs in your ``urlpatterns``, eg:

    url(r'^servicedirectory/',
        include('molo.servicedirectory.urls',
                namespace='molo.servicedirectory',
                app_name='molo.servicedirectory')),

Keys and other secrets are best kept out of version control and should be fetched from environment variables.
eg: ``GOOGLE_PLACES_API_SERVER_KEY = environ.get('GOOGLE_PLACES_API_SERVER_KEY', 'please-change-me')``

Known Issues
============

``manage.py rebuild_index`` will nuke the service directory index and **won't rebuild it!**
Both Molo and Wagtail are overriding Haystack's ``update_index`` management command, which appears to be
the root cause of the issue. In fact, ``rebuild_index`` won't work at all unless you set ``WAGTAILSEARCH_BACKENDS``
in settings (see ``test_settings.py`` and `Molo Core Features`_).

The Wagtail Admin integration is incomplete. Missing features are:

* Import/export functionality for the service directory models
* Organisation model - map widget for the ``location`` field, as well as the alternate ``location_coords`` field missing

Both features are still available in standard Django admin.


.. _Molo: https://github.com/praekelt/molo/
.. _Getting Started with Haystack: http://django-haystack.readthedocs.io/en/latest/tutorial.html#elasticsearch
.. _Google Developers Console: https://console.developers.google.com
.. _Molo Core Features: http://molo.readthedocs.io/features.html#core-features


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

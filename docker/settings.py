from os import environ

import dj_database_url

from .base import INSTALLED_APPS, MIDDLEWARE_CLASSES


# Disable debug mode
DEBUG = False
TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['*']

SECRET_KEY = environ.get('SECRET_KEY', 'please-change-me')

RAVEN_DSN = environ.get('RAVEN_DSN')
RAVEN_CONFIG = {'dsn': RAVEN_DSN} if RAVEN_DSN else {}

STATIC_ROOT = '/deploy/static'

INSTALLED_APPS = INSTALLED_APPS + [
    'djgeojson',
    'leaflet',
    'import_export',
    'haystack'
]

MIDDLEWARE_CLASSES = \
    ['molo.servicedirectory.middleware.HaystackBatchFlushMiddleware'] + \
    MIDDLEWARE_CLASSES

DATABASES = {
    'default': dj_database_url.config()
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'molo.servicedirectory.haystack_elasticsearch_raw_query'
                  '.custom_elasticsearch.ConfigurableElasticSearchEngine',
        'URL': 'http://%s:9200' % environ.get('ES_HOST', '127.0.0.1'),
        'INDEX_NAME': 'haystack_service_directory',
    },
}

HAYSTACK_SIGNAL_PROCESSOR = 'molo.servicedirectory.signal_processors' \
                            '.BatchingSignalProcessor'

GOOGLE_PLACES_API_SERVER_KEY = environ.get('GOOGLE_PLACES_API_SERVER_KEY',
                                           'please-change-me')
GOOGLE_ANALYTICS_TRACKING_ID = environ.get('GOOGLE_ANALYTICS_TRACKING_ID',
                                           'please-change-me')

VUMI_GO_ACCOUNT_KEY = environ.get('VUMI_GO_ACCOUNT_KEY', 'please-change-me')
VUMI_GO_CONVERSATION_KEY = environ.get('VUMI_GO_CONVERSATION_KEY',
                                       'please-change-me')
VUMI_GO_API_TOKEN = environ.get('VUMI_GO_API_TOKEN', 'please-change-me')
VUMI_GO_API_URL = environ.get('VUMI_GO_API_URL', 'please-change-me')

LEAFLET_CONFIG = {
    'SPATIAL_EXTENT': (-180, -90, 180, 90)
}

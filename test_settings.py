from .base import INSTALLED_APPS, MIDDLEWARE_CLASSES

INSTALLED_APPS = INSTALLED_APPS + [
    'djgeojson',
    'leaflet',
    'import_export',
    'haystack'
]

MIDDLEWARE_CLASSES = \
    ['molo.servicedirectory.middleware.HaystackBatchFlushMiddleware'] + \
    MIDDLEWARE_CLASSES

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'molo.servicedirectory.haystack_elasticsearch_raw_query'
                  '.custom_elasticsearch.ConfigurableElasticSearchEngine',
        'URL': 'http://127.0.0.1:9200',
        'INDEX_NAME': 'test',
    },
}

HAYSTACK_SIGNAL_PROCESSOR = 'molo.servicedirectory.signal_processors' \
                            '.BatchingSignalProcessor'

GOOGLE_PLACES_API_SERVER_KEY = 'AIzaSyCAqZ-dr0pUNEe1TrV7jFLjD6-IXb8xCJI'

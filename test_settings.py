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

WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': (
            'molo.core.wagtailsearch.backends.elasticsearch'
        ),
        'INDEX': 'testapp',
    },
}

GOOGLE_PLACES_API_SERVER_KEY = 'AIzaSyCAqZ-dr0pUNEe1TrV7jFLjD6-IXb8xCJI'

VUMI_GO_ACCOUNT_KEY = '32bbb5f26d724c4f9b9a79b230aaab6c'
VUMI_GO_CONVERSATION_KEY = '14a978cf775946eaab275736d55439fe'
VUMI_GO_API_TOKEN = '5532BED691D5FCF4A5DCBF177F64E'
VUMI_GO_API_URL = 'http://go.vumi.org/api/v1/go/http_api_nostream'

GOOGLE_ANALYTICS_TRACKING_ID = 'UA-38728736-13'


from testapp.settings.base import *  # noqa: F403


PROJECT_ROOT = dirname(dirname(dirname(abspath(__file__))))

DATABASES = {'default': dj_database_url.config(
    default='sqlite:///%s' % (join(PROJECT_ROOT, 'db.sqlite3'),))}

ROOT_URLCONF = 'molo.project.urls'

SECRET_KEY = 'test'

TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'molo.servicedirectory.context_processors'
    '.enable_service_directory_context',
]

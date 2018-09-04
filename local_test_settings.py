import dj_database_url

from os.path import abspath, dirname, join


PROJECT_ROOT = dirname(dirname(dirname(abspath(__file__))))

DATABASES = {'default': dj_database_url.config(
    default='sqlite:///%s' % (join(PROJECT_ROOT, 'db.sqlite3'),))}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',

    'molo.core',

    'taggit',

    'wagtail.wagtailadmin',
    'wagtail.wagtailcore',
    'wagtail.wagtailimages',
    'wagtail.wagtailsites',
    'wagtail.wagtailusers',
    'wagtailmedia',
]

ROOT_URLCONF = 'molo.servicedirectory.urls'

SECRET_KEY = 'test'

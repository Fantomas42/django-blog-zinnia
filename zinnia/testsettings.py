"""Settings for testing zinnia"""

SITE_ID = 1

ROOT_URLCONF = 'zinnia.urls.tests'

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.core.context_processors.request',
    'zinnia.context_processors.media',
    'zinnia.context_processors.version',]


DATABASE_ENGINE = 'sqlite3'
INSTALLED_APPS = ['django.contrib.contenttypes',
                  'django.contrib.comments',
                  'django.contrib.sites',
                  'django.contrib.auth',
                  #'south',
                  'tagging', 'zinnia']


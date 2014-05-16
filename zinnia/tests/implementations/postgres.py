"""Settings for testing zinnia on Postgres"""
from zinnia.tests.implementations.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'zinnia',
        'USER': 'postgres',
        'HOST': 'localhost'
    }
}

# TODO: to remove
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.comments',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django_xmlrpc',
    'mptt',
    'tagging',
    'zinnia'
]

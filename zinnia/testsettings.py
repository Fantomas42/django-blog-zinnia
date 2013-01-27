"""Settings for testing zinnia"""
import os
from zinnia.xmlrpc import ZINNIA_XMLRPC_METHODS

DATABASES = {'default': {'NAME': 'zinnia_tests.db',
                         'ENGINE': 'django.db.backends.sqlite3'}}

SITE_ID = 1

USE_TZ = True

STATIC_URL = '/static/'

SECRET_KEY = 'secret-key'

ROOT_URLCONF = 'zinnia.tests.urls'

LOCALE_PATHS = [os.path.join(os.path.dirname(__file__),
                             'locale')]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.SHA1PasswordHasher']

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.core.context_processors.request',
    'zinnia.context_processors.version']

TEMPLATE_LOADERS = [
    ['django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader']
     ]
]

TEMPLATE_DIRS = [os.path.join(os.path.dirname(__file__),
                              'tests', 'templates')]

INSTALLED_APPS = ['django.contrib.contenttypes',
                  'django.contrib.comments',
                  'django.contrib.sessions',
                  'django.contrib.sites',
                  'django.contrib.admin',
                  'django.contrib.auth',
                  'django_xmlrpc',
                  'mptt', 'tagging', 'zinnia']

ZINNIA_PAGINATION = 3

XMLRPC_METHODS = ZINNIA_XMLRPC_METHODS

"""Settings for testing zinnia"""
import os
from zinnia.xmlrpc import ZINNIA_XMLRPC_METHODS

SITE_ID = 1

USE_TZ = True

STATIC_URL = '/static/'

SECRET_KEY = 'secret-key'

ROOT_URLCONF = 'zinnia.tests.implementions.urls.default'

LOCALE_PATHS = [os.path.join(os.path.dirname(__file__), 'locale')]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.SHA1PasswordHasher'
]

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.core.context_processors.request',
    'zinnia.context_processors.version'
]

TEMPLATE_LOADERS = [
    ['django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader']
     ]
]

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django_comments',
    'django_xmlrpc',
    'mptt',
    'tagging',
    'south',
    'zinnia'
]

ZINNIA_PAGINATION = 3

XMLRPC_METHODS = ZINNIA_XMLRPC_METHODS

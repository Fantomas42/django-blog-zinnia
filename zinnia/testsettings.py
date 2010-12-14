"""Settings for testing zinnia"""
import os
from zinnia.xmlrpc import ZINNIA_XMLRPC_METHODS

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3'}}

SITE_ID = 1

ROOT_URLCONF = 'zinnia.tests.urls'

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.core.context_processors.request',
    'zinnia.context_processors.media',
    'zinnia.context_processors.version']

TEMPLATE_DIRS = [os.path.join(os.path.dirname(__file__),
                              'tests', 'templates')]

INSTALLED_APPS = ['django.contrib.contenttypes',
                  'django.contrib.comments',
                  'django.contrib.sessions',
                  'django.contrib.sites',
                  'django.contrib.admin',
                  'django.contrib.auth',
                  #'south',
                  'django_xmlrpc',
                  'mptt',
                  'tagging', 'zinnia']

XMLRPC_METHODS = ZINNIA_XMLRPC_METHODS

ZINNIA_PING_EXTERNAL_URLS = False
ZINNIA_SAVE_PING_DIRECTORIES = False

"""Settings for testing zinnia"""
import os
from zinnia.xmlrpc import ZINNIA_XMLRPC_METHODS

DATABASES = {'default': {'NAME': ':memory:',
                         'ENGINE': 'django.db.backends.sqlite3'}}

SITE_ID = 1

STATIC_URL = '/static/'

AKISMET_SECRET_API_KEY = 'AKISMET_API_KEY'
TYPEPAD_SECRET_API_KEY = 'TYPEPAD_API_KEY'
BITLY_LOGIN = 'BITLY_LOGIN'
BITLY_API_KEY = 'BITLY_API_KEY'

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.comments',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django_xmlrpc',
    'mptt', 'tagging', 'zinnia']

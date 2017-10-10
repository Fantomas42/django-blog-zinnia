"""Settings for Zinnia documentation"""
from zinnia.xmlrpc import XMLRPC_METHODS # noqa

DATABASES = {'default': {'NAME': ':memory:',
                         'ENGINE': 'django.db.backends.sqlite3'}}

SITE_ID = 1

STATIC_URL = '/static/'

SECRET_KEY = 'secret-key'
AKISMET_SECRET_API_KEY = 'AKISMET_API_KEY'
TYPEPAD_SECRET_API_KEY = 'TYPEPAD_API_KEY'
BITLY_LOGIN = 'BITLY_LOGIN'
BITLY_API_KEY = 'BITLY_API_KEY'
MOLLOM_PUBLIC_KEY = 'MOLLOM_PUBLIC_KEY'
MOLLOM_PRIVATE_KEY = 'MOLLOM_PRIVATE_KEY'

INSTALLED_APPS = [
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django_comments',
    'django_xmlrpc',
    'mptt', 'tagging', 'zinnia']

SILENCED_SYSTEM_CHECKS = ['1_7.W001']

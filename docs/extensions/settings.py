"""Settings for Zinnia documentation"""
from zinnia.xmlrpc import ZINNIA_XMLRPC_METHODS

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

comments_app = 'django.contrib.comments'
try:
    import django_comments
    comments_app = 'django_comments'
except ImportError:
    pass

INSTALLED_APPS = [
    'django.contrib.sites',
    'django.contrib.contenttypes',
    comments_app,
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django_xmlrpc',
    'mptt', 'tagging', 'zinnia']

"""Settings for testing zinnia on MySQL"""
from zinnia.tests.implementations.settings import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'zinnia',
        'USER': 'root',
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

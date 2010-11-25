"""Settings for Zinnia Demo"""
import os

gettext = lambda s: s

DATABASES = {'default':
             {'ENGINE': 'django.db.backends.sqlite3',
              'NAME': os.path.join(os.path.dirname(__file__), 'demo.db')}
             }

MEDIA_URL = 'http://localhost:8000/'

SECRET_KEY = 'jo-1rzm(%sf)3#n+fb7h955yu$3(pt63abhi12_t7e^^5q8dyw'

USE_I18N = True
USE_L10N = True

SITE_ID = 1

LANGUAGE_CODE = 'en'

LANGUAGES = (('en', gettext('English')),
             ('fr', gettext('French')),
             ('es', gettext('Spanish')),
             ('de', gettext('German')),
             ('ru', gettext('Russian')),
             ('zh_CN', gettext('Simplified Chinese')),)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    )

ROOT_URLCONF = 'demo.urls'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    'django.template.loaders.eggs.load_template_source',
    )

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'zinnia.context_processors.media',
    'zinnia.context_processors.version',
    )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sitemaps',
    'django.contrib.comments',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'mptt',
    'zinnia',
    'tagging',
    'django_xmlrpc',
    )

from zinnia.xmlrpc import ZINNIA_XMLRPC_METHODS
XMLRPC_METHODS = ZINNIA_XMLRPC_METHODS

ZINNIA_PING_EXTERNAL_URLS = False

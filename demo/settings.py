"""Settings for Zinnia Demo"""
import os

gettext = lambda s: s

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {'default':
             {'ENGINE': 'django.db.backends.sqlite3',
              'NAME': os.path.join(os.path.dirname(__file__), 'demo.db')}
             }

TIME_ZONE = 'Europe/Paris'

STATIC_URL = '/static/'

MEDIA_URL = '/media/'

SECRET_KEY = 'jo-1rzm(%sf)3#n+fb7h955yu$3(pt63abhi12_t7e^^5q8dyw'

USE_TZ = True
USE_I18N = True
USE_L10N = True

SITE_ID = 1

LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('en', gettext('English')),
    ('fr', gettext('French')),
    ('de', gettext('German')),
    ('es', gettext('Spanish')),
    ('it', gettext('Italian')),
    ('nl', gettext('Dutch')),
    ('sl', gettext('Slovenian')),
    ('bg', gettext('Bulgarian')),
    ('hu', gettext('Hungarian')),
    ('cs', gettext('Czech')),
    ('sk', gettext('Slovak')),
    ('lt', gettext('Lithuanian')),
    ('ru', gettext('Russian')),
    ('pl', gettext('Polish')),
    ('eu', gettext('Basque')),
    ('he', gettext('Hebrew')),
    ('ca', gettext('Catalan')),
    ('tr', gettext('Turkish')),
    ('sv', gettext('Swedish')),
    ('is', gettext('Icelandic')),
    ('hr_HR', gettext('Croatian')),
    ('pt_BR', gettext('Brazilian Portuguese')),
    ('fa_IR', gettext('Persian')),
    ('fi_FI', gettext('Finnish')),
    ('uk_UA', gettext('Ukrainian')),
    ('zh-hans', gettext('Simplified Chinese')),
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'demo.urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'zinnia.context_processors.version',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sitemaps',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.staticfiles',
    'django_comments',
    'django_xmlrpc',
    'mptt',
    'tagging',
    'zinnia',
    # 'filer',
)

from zinnia.xmlrpc import ZINNIA_XMLRPC_METHODS
XMLRPC_METHODS = ZINNIA_XMLRPC_METHODS

if 'filer' in INSTALLED_APPS:
    ZINNIA_IMAGE_FILED = 'demo.models_bases.ZINNIA_IMAGE_FILED'
    INSTALLED_APPS += (
        'polymorphic',
        'easy_thumbnails',
    )
    THUMBNAIL_HIGH_RESOLUTION = True
    THUMBNAIL_PROCESSORS = (
        'easy_thumbnails.processors.colorspace',
        'easy_thumbnails.processors.autocrop',
        #'easy_thumbnails.processors.scale_and_crop',
        'filer.thumbnail_processors.scale_and_crop_with_subject_location',
        'easy_thumbnails.processors.filters',
    )

## Otherwise, if you want, you can safely disable an image filed
# ZINNIA_IMAGE_FILED = False

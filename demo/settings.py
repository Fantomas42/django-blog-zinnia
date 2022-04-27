"""Settings for Zinnia Demo"""
import logging
import os

logger = logging.getLogger(__name__)

gettext = lambda s: s  # noqa

DEBUG = False
ALLOWED_HOSTS = [
    '127.0.0.1'
]

DATABASES = {
    'default':
        {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(os.path.dirname(__file__), 'demo.db')
        }
}

TIME_ZONE = 'US/Eastern'

STATIC_ROOT = './demo_static/'

STATIC_URL = os.environ.get('STATIC_URL')
if not STATIC_URL:
    logger.warning(
        msg=f'WARNING: STATIC_URL is /static/'
    )
    STATIC_URL = '/static/'

MEDIA_URL = '/media/'

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    logger.warning(
        msg=f'WARNING: SECRET_KEY environment variable not set. '
            f'Using insecure configuration.'
    )
    SECRET_KEY = 'NeverUseThisSecretKey1234'

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
    # ('hr_HR', gettext('Croatian')),
    # ('pt_BR', gettext('Brazilian Portuguese')),
    # ('fa_IR', gettext('Persian')),
    # ('fi_FI', gettext('Finnish')),
    # ('uk_UA', gettext('Ukrainian')),
    ('zh-hans', gettext('Simplified Chinese')),
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'demo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'zinnia.context_processors.version',
            ]
        }
    }
]

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
    'zinnia'
)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

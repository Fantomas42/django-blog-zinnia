"""Settings for testing zinnia"""
SITE_ID = 1

USE_TZ = True

STATIC_URL = '/static/'

SECRET_KEY = 'secret-key'

ROOT_URLCONF = 'zinnia.tests.implementations.urls.default'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.SHA1PasswordHasher'
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware'
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'zinnia.context_processors.version',
            ],
            'loaders': [
                ['django.template.loaders.cached.Loader', [
                    'django.template.loaders.app_directories.Loader']
                 ]
            ]
        }
    }
]

SILENCED_SYSTEM_CHECKS = ['1_6.W001']

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
    'zinnia'
]

ZINNIA_PAGINATION = 3

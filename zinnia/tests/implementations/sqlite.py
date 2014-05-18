"""Settings for testing zinnia on SQLite"""
from zinnia.tests.implementations.settings import *  # noqa

DATABASES = {
    'default': {
        'NAME': 'zinnia.db',
        'ENGINE': 'django.db.backends.sqlite3'
    }
}

"""Settings for testing zinnia"""

SITE_ID = 1

DATABASE_ENGINE = 'sqlite3'
INSTALLED_APPS = ['django.contrib.contenttypes',
                  'django.contrib.comments',
                  'django.contrib.sites',
                  'django.contrib.auth',
                  'tagging', 'zinnia']

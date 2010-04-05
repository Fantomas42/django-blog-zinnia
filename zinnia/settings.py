"""Settings of Zinnia"""
from django.conf import settings

PING_DIRECTORIES = getattr(settings, 'ZINNIA_PING_DIRECTORIES', ())
SAVE_PING_DIRECTORIES = getattr(settings, 'ZINNIA_AUTO_PING',
                                bool(PING_DIRECTORIES))

COPYRIGHT = getattr(settings, 'ZINNIA_COPYRIGHT', 'Zinnia')
PAGINATION = getattr(settings, 'ZINNIA_PAGINATION', 10)
MAIL_COMMENT = getattr(settings, 'ZINNIA_MAIL_COMMENT', True)
AKISMET_COMMENT = getattr(settings, 'ZINNIA_AKISMET_COMMENT', True)
UPLOAD_TO = getattr(settings, 'ZINNIA_UPLOAD_TO', 'uploads')

MEDIA_URL = getattr(settings, 'ZINNIA_MEDIA_URL', '/zinnia/')

F_MIN = getattr(settings, 'ZINNIA_F_MIN', 0.1)
F_MAX = getattr(settings, 'ZINNIA_F_MAX', 1.0)

USE_BITLY = getattr(settings, 'ZINNIA_USE_BITLY', 'django_bitly' in settings.INSTALLED_APPS)

try:
    import twitter
    USE_TWITTER = getattr(settings, 'ZINNIA_USE_TWITTER', True)
except ImportError:
    USE_TWITTER = False

TWITTER_USER = getattr(settings, 'TWITTER_USER', '')
TWITTER_PASSWORD = getattr(settings, 'TWITTER_PASSWORD', '')


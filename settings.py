"""Settings of Zinnia"""
from django.conf import settings

PING_DIRECTORIES = getattr(settings, 'ZINNIA_PING_DIRECTORIES', ())
SAVE_PING_DIRECTORIES = getattr(settings, 'ZINNIA_AUTO_PING', bool(PING_DIRECTORIES))

PAGINATION = getattr(settings, 'ZINNIA_PAGINATION', 10)
MAIL_COMMENT = getattr(settings, 'ZINNIA_MAIL_COMMENT', True)
AKISMET_COMMENT = getattr(settings, 'ZINNIA_AKISMET_COMMENT', False)


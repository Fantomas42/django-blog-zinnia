"""Settings of Zinnia.plugins"""
from django.conf import settings

PLUGINS_TEMPLATES = getattr(settings, 'ZINNIA_PLUGINS_TEMPLATES', [])


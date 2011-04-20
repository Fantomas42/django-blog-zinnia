"""Bit.ly url shortener backend for Zinnia"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

try:
    from django_bitly.models import Bittle
except ImportError:
    raise ImproperlyConfigured('django_bitly is not available')

if not getattr(settings, 'BITLY_LOGIN', ''):
    raise ImproperlyConfigured('You have to set a BITLY_LOGIN setting')

if not getattr(settings, 'BITLY_API_KEY', ''):
    raise ImproperlyConfigured('You have to set a BITLY_API_KEY setting')


def backend(entry):
    """Bit.ly url shortener backend for Zinnia"""
    bittle = Bittle.objects.bitlify(entry)
    return bittle.shortUrl

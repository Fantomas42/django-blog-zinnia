"""Custom spam checker backend for testing Zinnia"""
from django.core.exceptions import ImproperlyConfigured

raise ImproperlyConfigured('This backend only exists for testing')


def backend(entry):
    """Custom spam checker backend for testing Zinnia"""
    return False

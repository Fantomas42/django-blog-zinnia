"""Custom spam checker backend for testing Zinnia"""
from django.core.exceptions import ImproperlyConfigured

#I still don't know what this is supposed to do.
#It's triggering test failures, in conflict with the error
#message. I'm very confused here.
raise ImproperlyConfigured('This backend only exists for testing')


def backend(entry):
    """Custom spam checker backend for testing Zinnia"""
    return False

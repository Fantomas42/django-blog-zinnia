"""Spam checker for Zinnia"""
import warnings

from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured

from zinnia.settings import SPAM_CHECKER_BACKENDS


def get_spam_checker(backend_path):
    """Return the selected spam checker backend"""
    try:
        backend_module = import_module(backend_path)
        backend = getattr(backend_module, 'backend')
    except (ImportError, AttributeError):
        warnings.warn('%s backend cannot be imported' % backend_path,
                      RuntimeWarning)
        backend = None
    except ImproperlyConfigured, e:
        warnings.warn(str(e), RuntimeWarning)
        backend = None

    return backend


def check_is_spam(content, content_object, request,
                  backends=SPAM_CHECKER_BACKENDS):
    """Return True if the content is a spam, else False"""
    for backend_path in backends:
        spam_checker = get_spam_checker(backend_path)
        if spam_checker is not None:
            is_spam = spam_checker(content, content_object, request)
            if is_spam:
                return True

    return False

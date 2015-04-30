"""Base models for Zinnia"""
from importlib import import_module

from django.core.exceptions import ImproperlyConfigured


def load_model_class(model_path):
    """
    Load by import a class by a string path like:
    'module.models.MyModel'.
    This mechanism allows extension and customization of
    the Entry model class.
    """
    dot = model_path.rindex('.')
    module_name = model_path[:dot]
    class_name = model_path[dot + 1:]
    try:
        _class = getattr(import_module(module_name), class_name)
        return _class
    except (ImportError, AttributeError):
        raise ImproperlyConfigured('%s cannot be imported' % model_path)

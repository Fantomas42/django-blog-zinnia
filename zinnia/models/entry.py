"""Entry model for Zinnia"""
import warnings

from django.utils.importlib import import_module

from zinnia.models_bases.entry import EntryAbstractClass
from zinnia.settings import ENTRY_BASE_MODEL


def get_base_model():
    """
    Determine the base Model to inherit in the
    Entry Model, this allow to overload it.
    """
    if not ENTRY_BASE_MODEL:
        return EntryAbstractClass

    dot = ENTRY_BASE_MODEL.rindex('.')
    module_name = ENTRY_BASE_MODEL[:dot]
    class_name = ENTRY_BASE_MODEL[dot + 1:]
    try:
        _class = getattr(import_module(module_name), class_name)
        return _class
    except (ImportError, AttributeError):
        warnings.warn('%s cannot be imported' % ENTRY_BASE_MODEL,
                      RuntimeWarning)
    return EntryAbstractClass


class Entry(get_base_model()):
    """
    The final Entry model based on inheritence.
    """

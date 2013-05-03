"""Entry model for Zinnia"""
from zinnia.settings import ENTRY_BASE_MODEL
from zinnia.models_bases import load_model_class


class Entry(load_model_class(ENTRY_BASE_MODEL)):
    """
    The final Entry model based on inheritence.
    """

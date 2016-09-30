"""Entry model for Zinnia"""
from zinnia.models_bases import load_model_class
from zinnia.settings import ENTRY_BASE_MODEL


class Entry(load_model_class(ENTRY_BASE_MODEL)):
    """
    The final Entry model based on inheritence.
    """

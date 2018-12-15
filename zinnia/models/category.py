"""Category model for Zinnia"""
from zinnia.models_bases import load_model_class
from zinnia.settings import CATEGORY_BASE_MODEL


class Category(load_model_class(CATEGORY_BASE_MODEL)):
    """
    The final Category model based on inheritence.
    """

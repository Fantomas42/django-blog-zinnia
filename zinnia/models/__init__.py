"""Models for Zinnia"""
# Here we import the Zinnia's Model classes
# to register the Models at the loading, not
# when the Zinnia's urls are parsed. Issue #161.
from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.models.category import Category


__all__ = [Entry.__name__,
           Author.__name__,
           Category.__name__]

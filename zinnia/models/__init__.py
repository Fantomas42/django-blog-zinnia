from zinnia.models.author import Author
from zinnia.models.category import Category


# Here we import the Zinnia's Model classes
# to register the Models at the loading, not
# when the Zinnia's URLs are parsed. Issue #161.
# Issue #161, seems not valid since Django 1.7.
__all__ = [Author.__name__,
           Category.__name__]

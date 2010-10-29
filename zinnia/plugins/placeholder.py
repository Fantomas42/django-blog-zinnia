"""Placeholder model for Zinnia"""
from cms.models.fields import PlaceholderField

from zinnia.models import EntryAbstractClass


class EntryPlaceholder(EntryAbstractClass):
    """Entry with a Placeholder to edit content"""

    content_placeholder = PlaceholderField('content')

    class Meta:
        """EntryPlaceholder's Meta"""
        abstract = True

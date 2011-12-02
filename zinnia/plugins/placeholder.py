"""Placeholder model for Zinnia"""
from cms.models.fields import PlaceholderField

from zinnia.models import EntryAbstractClass


class EntryPlaceholder(EntryAbstractClass):
    """Entry with a Placeholder to edit content"""

    content_placeholder = PlaceholderField('content')

    @property
    def html_content(self):
        """No additional formatting is necessary"""
        return self.content

    class Meta:
        """EntryPlaceholder's Meta"""
        abstract = True

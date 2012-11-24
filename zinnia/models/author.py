"""Author model for Zinnia"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import UserManager

from zinnia.managers import entries_published
from zinnia.managers import EntryRelatedPublishedManager


class Author(User):
    """Proxy model around :class:`django.contrib.auth.models.User`"""

    objects = UserManager()
    published = EntryRelatedPublishedManager()

    def entries_published(self):
        """Return only the entries published"""
        return entries_published(self.entries)

    def __unicode__(self):
        """If the user has a full name, use that or else the username"""
        return self.get_full_name() or self.username

    @models.permalink
    def get_absolute_url(self):
        """Return author's URL"""
        return ('zinnia_author_detail', (self.username,))

    class Meta:
        """Author's Meta"""
        app_label = 'zinnia'
        proxy = True

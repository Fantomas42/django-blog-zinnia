"""Author model for Zinnia"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import UserManager

from zinnia.managers import entries_published
from zinnia.managers import EntryRelatedPublishedManager


class Author(User):
    """
    Proxy model around :class:`django.contrib.auth.models.User`.
    """

    objects = UserManager()
    published = EntryRelatedPublishedManager()

    def entries_published(self):
        """
        Returns author's published entries.
        """
        return entries_published(self.entries)

    @models.permalink
    def get_absolute_url(self):
        """
        Builds and returns the author's URL based on his username.
        """
        return ('zinnia_author_detail', (self.username,))

    def __unicode__(self):
        """
        If the user has a full name, use it instead of the username.
        """
        return self.get_full_name() or self.username

    class Meta:
        """
        Author's meta informations.
        """
        app_label = 'zinnia'
        proxy = True

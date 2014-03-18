"""Author model for Zinnia"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.encoding import python_2_unicode_compatible

from zinnia.managers import entries_published
from zinnia.managers import EntryRelatedPublishedManager


class AuthorPublishedManager(models.Model):
    """
    Proxy model manager to avoid overriding of
    the default User's manager and issue #307.
    """
    published = EntryRelatedPublishedManager()

    class Meta:
        abstract = True


@python_2_unicode_compatible
class Author(get_user_model(),
             AuthorPublishedManager):
    """
    Proxy model around :class:`django.contrib.auth.models.get_user_model`.
    """

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
        return ('zinnia:author_detail', [self.get_username()])

    def __str__(self):
        """
        If the user has a full name, use it instead of the username.
        """
        return self.get_full_name() or self.get_username()

    class Meta:
        """
        Author's meta informations.
        """
        app_label = 'zinnia'
        proxy = True

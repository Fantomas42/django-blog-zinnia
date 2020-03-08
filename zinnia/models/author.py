"""Author model for Zinnia"""
from django.apps import apps
from django.conf import settings
from django.db import models
from django.urls import reverse

from zinnia.managers import EntryRelatedPublishedManager
from zinnia.managers import entries_published


def safe_get_user_model():
    """
    Safe loading of the User model, customized or not.
    """
    user_app, user_model = settings.AUTH_USER_MODEL.split('.')
    return apps.get_registered_model(user_app, user_model)


class AuthorPublishedManager(models.Model):
    """
    Proxy model manager to avoid overriding of
    the default User's manager and issue #307.
    """
    published = EntryRelatedPublishedManager()

    class Meta:
        abstract = True


class Author(safe_get_user_model(),
             AuthorPublishedManager):
    """
    Proxy model around :class:`django.contrib.auth.models.get_user_model`.
    """

    def entries_published(self):
        """
        Returns author's published entries.
        """
        return entries_published(self.entries)

    def get_absolute_url(self):
        """
        Builds and returns the author's URL based on his username.
        """
        try:
            return super(Author, self).get_absolute_url()
        except AttributeError:
            return reverse('zinnia:author_detail', args=[self.get_username()])

    def __str__(self):
        """
        If the user has a full name, use it instead of the username.
        """
        return (self.get_short_name()
                or self.get_full_name()
                or self.get_username())

    class Meta:
        """
        Author's meta informations.
        """
        proxy = True

"""Author model for Zinnia"""
from django.db import models
from django.contrib.auth.models import User

from zinnia.managers import entries_published
from zinnia.managers import AuthorPublishedManager


class Author(User):
    """Proxy Model around django.contrib.auth.models.User"""

    objects = models.Manager()
    published = AuthorPublishedManager()

    def entries_published(self):
        """Return only the entries published"""
        return entries_published(self.entries)

    def __unicode__(self):
        if self.first_name and self.last_name:
            return u'%s %s' % (self.first_name, self.last_name)
        return self.username

    @models.permalink
    def get_absolute_url(self):
        """Return author's URL"""
        return ('zinnia_author_detail', (self.username,))

    class Meta:
        """Author's Meta"""
        app_label = 'zinnia'
        proxy = True


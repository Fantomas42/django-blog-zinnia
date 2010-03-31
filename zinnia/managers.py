"""Managers of Zinnia"""
from datetime import datetime

from django.db import models
from django.contrib.sites.models import Site


DRAFT = 0
HIDDEN = 1
PUBLISHED = 2

def authors_published():
    """Return the published authors"""
    from zinnia.models import Entry
    from django.contrib.auth.models import User

    author_ids = [user.pk for user in User.objects.all()
                  if user.entry_set.count()]
    return User.objects.filter(pk__in=author_ids)


def entries_published(queryset):
    """Return only the entries published"""
    now = datetime.now()
    return queryset.filter(status=PUBLISHED,
                           start_publication__lte=now,
                           end_publication__gt=now,
                           sites=Site.objects.get_current())


class EntryPublishedManager(models.Manager):
    """Manager to retrieve published entries"""

    def get_query_set(self):
        return entries_published(
            super(EntryPublishedManager, self).get_query_set())

    def search(self, pattern):
        lookup = None
        for pattern in pattern.split():
            q = models.Q(content__icontains=pattern) | \
                models.Q(excerpt__icontains=pattern) | \
                models.Q(title__icontains=pattern)
            if lookup is None:
                lookup = q
            else:
                lookup |= q

        return self.get_query_set().filter(lookup)

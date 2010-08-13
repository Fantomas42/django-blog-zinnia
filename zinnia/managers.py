"""Managers of Zinnia"""
from datetime import datetime

from django.db import models
from django.contrib.sites.models import Site

from zinnia.settings import ADVANCED_SEARCH

DRAFT = 0
HIDDEN = 1
PUBLISHED = 2

def tags_published():
    """Return the pusblished tags"""
    from tagging.models import Tag
    from zinnia.models import Entry
    tags_published = Tag.objects.usage_for_queryset(Entry.published.all())
    return Tag.objects.filter(name__in=[t.name for t in tags_published])

def authors_published():
    """Return the published authors"""
    from django.contrib.auth.models import User

    author_ids = [user.pk for user in User.objects.all()
                  if user.entry_set.filter(status=PUBLISHED).count()]
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
        if ADVANCED_SEARCH:
            try:
                return self.advanced_search(pattern)
            except ImportError:
                return self.basic_search(pattern)
        return self.basic_search(pattern)

    def advanced_search(self, pattern):
        from zinnia.search import advanced_search
        return advanced_search(pattern)

    def basic_search(self, pattern):
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

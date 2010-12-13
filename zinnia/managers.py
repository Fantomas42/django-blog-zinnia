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
    tags_entry_published = Tag.objects.usage_for_queryset(Entry.published.all())
    return Tag.objects.filter(name__in=[t.name for t in tags_entry_published])


def authors_published():
    """Return the published authors"""
    from django.contrib.auth.models import User
    return User.objects.filter(entry__status=PUBLISHED).distinct()


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
        """Return published entries"""
        return entries_published(
            super(EntryPublishedManager, self).get_query_set())

    def on_site(self):
        """Return entries published on current site"""
        return super(EntryPublishedManager, self).get_query_set(
            ).filter(sites=Site.objects.get_current())

    def search(self, pattern):
        """Top level search method on entries"""
        if ADVANCED_SEARCH:
            try:
                return self.advanced_search(pattern)
            except ImportError:
                return self.basic_search(pattern)
        return self.basic_search(pattern)

    def advanced_search(self, pattern):
        """Advanced search on entries"""
        from zinnia.search import advanced_search
        return advanced_search(pattern)

    def basic_search(self, pattern):
        """Basic search on entries"""
        lookup = None
        for pattern in pattern.split():
            query_part = models.Q(content__icontains=pattern) | \
                         models.Q(excerpt__icontains=pattern) | \
                         models.Q(title__icontains=pattern)
            if lookup is None:
                lookup = query_part
            else:
                lookup |= query_part

        return self.get_query_set().filter(lookup)

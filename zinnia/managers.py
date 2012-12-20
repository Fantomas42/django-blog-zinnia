"""Managers of Zinnia"""
from django.db import models
from django.utils import timezone
from django.contrib.sites.models import Site

DRAFT = 0
HIDDEN = 1
PUBLISHED = 2


def tags_published():
    """Return the published tags"""
    from tagging.models import Tag
    from zinnia.models.entry import Entry
    tags_entry_published = Tag.objects.usage_for_queryset(
        Entry.published.all())
    # Need to do that until the issue #44 of django-tagging is fixed
    return Tag.objects.filter(name__in=[t.name for t in tags_entry_published])


def entries_published(queryset):
    """Return only the entries published"""
    now = timezone.now()
    return queryset.filter(
        models.Q(start_publication__lte=now) |
        models.Q(start_publication=None),
        models.Q(end_publication__gt=now) |
        models.Q(end_publication=None),
        status=PUBLISHED, sites=Site.objects.get_current())


class EntryPublishedManager(models.Manager):
    """Manager to retrieve published entries"""

    def get_query_set(self):
        """Return published entries"""
        return entries_published(
            super(EntryPublishedManager, self).get_query_set())

    def on_site(self):
        """Return entries published on current site"""
        return super(EntryPublishedManager, self).get_query_set().filter(
            sites=Site.objects.get_current())

    def search(self, pattern):
        """Top level search method on entries"""
        try:
            return self.advanced_search(pattern)
        except:
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


class EntryRelatedPublishedManager(models.Manager):
    """Manager to retrieve objects associated with published entries"""

    def get_query_set(self):
        """Return a queryset containing published entries"""
        now = timezone.now()
        return super(
            EntryRelatedPublishedManager, self).get_query_set().filter(
                models.Q(entries__start_publication__lte=now) |
                models.Q(entries__start_publication=None),
                models.Q(entries__end_publication__gt=now) |
                models.Q(entries__end_publication=None),
                entries__status=PUBLISHED,
                entries__sites=Site.objects.get_current()
            ).distinct()

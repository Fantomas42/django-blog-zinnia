"""Managers of Zinnia"""
from django.contrib.sites.models import Site
from django.db import models
from django.utils import timezone

from zinnia.settings import SEARCH_FIELDS

DRAFT = 0
HIDDEN = 1
PUBLISHED = 2


def tags_published(request=None):
    """
    Return the published tags.
    """
    from tagging.models import Tag
    from zinnia.models.entry import Entry
    tags_entry_published = Tag.objects.usage_for_queryset(
        Entry.objects.published(request))
    # Need to do that until the issue #44 of django-tagging is fixed
    return Tag.objects.filter(name__in=[t.name for t in tags_entry_published])


def entries_published(queryset, request=None):
    """
    Return only the entries published.
    """
    now = timezone.now()
    return queryset.filter(
        models.Q(start_publication__lte=now) |
        models.Q(start_publication=None),
        models.Q(end_publication__gt=now) |
        models.Q(end_publication=None),
        status=PUBLISHED, sites=Site.objects.get_current(request))


class EntryQuerySet(models.QuerySet):
    def published(self, request=None):
        """
        Return published entries.
        """
        return entries_published(self, request)

    def on_site(self, request=None):
        """
        Return entries of current site.
        """
        return self.filter(sites=Site.objects.get_current(request))


class EntryManager(models.Manager.from_queryset(EntryQuerySet)):
    """
    Manager to retrieve published entries.
    """

    def search(self, pattern):
        """
        Top level search method on entries.
        """
        try:
            return self.advanced_search(pattern)
        except Exception:
            return self.basic_search(pattern)

    def advanced_search(self, pattern, request=None):
        """
        Advanced search on entries.
        """
        from zinnia.search import advanced_search
        return advanced_search(pattern, request)

    def basic_search(self, pattern, request=None):
        """
        Basic search on entries.
        """
        lookup = None
        for pattern in pattern.split():
            query_part = models.Q()
            for field in SEARCH_FIELDS:
                query_part |= models.Q(**{'%s__icontains' % field: pattern})
            if lookup is None:
                lookup = query_part
            else:
                lookup |= query_part

        return self.published(request).filter(lookup)


class EntryRelatedPublishedManager(models.Manager):
    """
    Manager to retrieve objects associated with published entries.
    """

    def get_queryset(self):
        """
        Return a queryset containing published entries.
        """
        now = timezone.now()
        return super(
            EntryRelatedPublishedManager, self).get_queryset().filter(
            models.Q(entries__start_publication__lte=now) |
            models.Q(entries__start_publication=None),
            models.Q(entries__end_publication__gt=now) |
            models.Q(entries__end_publication=None),
            entries__status=PUBLISHED,
            entries__sites=Site.objects.get_current()
        ).distinct()

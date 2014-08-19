"""Managers of Zinnia"""
import django
from django.db import models
from django.utils import timezone
from django.contrib.sites.models import Site

DRAFT = 0
HIDDEN = 1
PUBLISHED = 2


def tags_published():
    """
    Return the published tags.
    """
    from tagging.models import Tag
    from zinnia.models.entry import Entry
    tags_entry_published = Tag.objects.usage_for_queryset(
        Entry.published.all())
    # Need to do that until the issue #44 of django-tagging is fixed
    return Tag.objects.filter(name__in=[t.name for t in tags_entry_published])


def entries_published(queryset):
    """
    Return only the entries published.
    """
    now = timezone.now()
    return queryset.filter(
        models.Q(start_publication__lte=now) |
        models.Q(start_publication=None),
        models.Q(end_publication__gt=now) |
        models.Q(end_publication=None),
        status=PUBLISHED, sites=Site.objects.get_current())


class EntryPublishedManager(models.Manager):
    """
    Manager to retrieve published entries.
    """

    def _get_queryset_compat(self, *args, **kwargs):
        """
        rant: why oh why would you rename something so widely used?
        benjaoming:
        In Django 1.6, a DeprecationWarning appears whenever get_query_set
        is called. This is an unfortunate decision by django core devs
        because a lot of custom manager inheritance relies on the naming
        of get_query_set/get_queryset. In this case, the DeprecationWarnings
        firstly broke django-mptt, and then the django-mptt fix broke all the
        Django<1.6 custom managers with custom querysets defined using `get_query_set`.

        See issue: #316
        """
        if django.VERSION >= (1, 6):
            # in 1.6+, get_queryset gets defined by the base manager and complains if it's called.
            # otherwise, we have to define it ourselves.
            get_queryset = super(EntryPublishedManager, self).get_queryset
        else:
            get_queryset = super(EntryPublishedManager, self).get_query_set
        return get_queryset(*args, **kwargs)

    if django.VERSION < (1, 6):
        # Backwards compatibility hack.
        # Before fixing #316, we always provided a get_queryset() method even on django < 1.6.
        # So if anyone's relying on it, need to preserve this until django 1.6 is the minimum supported version.
        # Then we can get rid of this since it will be provided by models.Model anyway.
        def get_queryset(self, *args, **kwargs):
            return self.get_query_set(*args, **kwargs)

    def get_query_set(self):
        """
        Return published entries.
        """
        return entries_published(self._get_queryset_compat())

    def on_site(self):
        """
        Return entries published on current site.
        """
        return self._get_queryset_compat().filter(
            sites=Site.objects.get_current())

    def search(self, pattern):
        """
        Top level search method on entries.
        """
        try:
            return self.advanced_search(pattern)
        except:
            return self.basic_search(pattern)

    def advanced_search(self, pattern):
        """
        Advanced search on entries.
        """
        from zinnia.search import advanced_search
        return advanced_search(pattern)

    def basic_search(self, pattern):
        """
        Basic search on entries.
        """
        lookup = None
        for pattern in pattern.split():
            query_part = models.Q(content__icontains=pattern) | \
                models.Q(excerpt__icontains=pattern) | \
                models.Q(title__icontains=pattern)
            if lookup is None:
                lookup = query_part
            else:
                lookup |= query_part

        return self._get_queryset_compat().filter(lookup)


class EntryRelatedPublishedManager(models.Manager):
    """
    Manager to retrieve objects associated with published entries.
    """

    def _get_queryset_compat(self, *args, **kwargs):
        """
        rant: why oh why would you rename something so widely used?
        benjaoming:
        In Django 1.6, a DeprecationWarning appears whenever get_query_set
        is called. This is an unfortunate decision by django core devs
        because a lot of custom manager inheritance relies on the naming
        of get_query_set/get_queryset. In this case, the DeprecationWarnings
        firstly broke django-mptt, and then the django-mptt fix broke all the
        Django<1.6 custom managers with custom querysets defined using `get_query_set`.

        See issue: django-mptt/django-mptt#316
        """
        if django.VERSION >= (1, 6):
            # in 1.6+, get_queryset gets defined by the base manager and complains if it's called.
            # otherwise, we have to define it ourselves.
            get_queryset = super(EntryPublishedManager, self).get_queryset
        else:
            get_queryset = super(EntryPublishedManager, self).get_query_set
        return get_queryset(*args, **kwargs)

    if django.VERSION < (1, 6):
        # Backwards compatibility hack.
        # Before fixing #316, we always provided a get_queryset() method even on django < 1.6.
        # So if anyone's relying on it, need to preserve this until django 1.6 is the minimum supported version.
        # Then we can get rid of this since it will be provided by models.Model anyway.
        def get_queryset(self, *args, **kwargs):
            return self.get_query_set(*args, **kwargs)
            
    def get_query_set(self):
        """
        Return a queryset containing published entries.
        """
        now = timezone.now()
        return self._get_queryset_compat().filter(
            models.Q(entries__start_publication__lte=now) |
            models.Q(entries__start_publication=None),
            models.Q(entries__end_publication__gt=now) |
            models.Q(entries__end_publication=None),
            entries__status=PUBLISHED,
            entries__sites=Site.objects.get_current()
            ).distinct()

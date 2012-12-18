"""Sitemaps for Zinnia"""
from django.db.models import Max
from django.db.models import Count
from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from tagging.models import Tag
from tagging.models import TaggedItem

from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.models.category import Category
from zinnia.settings import PROTOCOL


class ZinniaSitemap(Sitemap):
    """Base Sitemap class for Zinnia"""
    protocol = PROTOCOL


class EntrySitemap(ZinniaSitemap):
    """Sitemap for entries"""
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        """Return published entries"""
        return Entry.published.all()

    def lastmod(self, obj):
        """Return last modification of an entry"""
        return obj.last_update


class EntryRelatedSitemap(ZinniaSitemap):
    """Sitemap for models related to Entries"""
    model = None
    changefreq = 'monthly'

    def items(self):
        """
        Get a queryset, cache infos for standardized access to them later
        then compute the maximum of entries to define the priority
        of each items.
        """
        queryset = self.get_queryset()
        self.cache_infos(queryset)
        self.set_max_entries()
        return queryset

    def get_queryset(self):
        """
        Build a queryset of items with published entries and annotated
        with the number of entries and the latest modification date.
        """
        return self.model.published.annotate(
            count_entries=Count('entries')).annotate(
                last_update=Max('entries__last_update'))

    def cache_infos(self, queryset):
        """
        Cache infos like the number of entries published and
        the last modification date for standardized access later.
        """
        self.cache = {}
        for item in queryset:
            self.cache[item.pk] = (item.count_entries, item.last_update)

    def set_max_entries(self):
        """
        Define the maximum of entries for computing the priority
        of each items later.
        """
        if self.cache:
            self.max_entries = float(max([i[0] for i in self.cache.values()]))

    def lastmod(self, item):
        """
        The last modification date is defined
        by the latest entries last update in the cache.
        """
        return self.cache[item.pk][1]

    def priority(self, item):
        """
        The priority of the item depends of the number of entries published
        in the cache divided by the maximum of entries.
        """
        return '%.1f' % max(self.cache[item.pk][0] / self.max_entries, 0.1)


class CategorySitemap(EntryRelatedSitemap):
    """Sitemap for categories"""
    model = Category


class AuthorSitemap(EntryRelatedSitemap):
    """Sitemap for authors"""
    model = Author


class TagSitemap(EntryRelatedSitemap):
    """Sitemap for tags"""

    def get_queryset(self):
        """
        Return the published Tags with option counts.
        """
        self.entries_qs = Entry.published.all()
        return Tag.objects.usage_for_queryset(
            self.entries_qs, counts=True)

    def cache_infos(self, queryset):
        """
        Cache the number of entries published and the last
        modification date under each tag.
        """
        self.cache = {}
        for item in queryset:
            # If the sitemap is going to be too slow,
            # don't hesitate to do this :
            # self.cache[item.pk] = (item.count, None)
            self.cache[item.pk] = (
                item.count, TaggedItem.objects.get_by_model(
                    self.entries_qs, item)[0].last_update)

    def location(self, item):
        """Return URL of the Tag"""
        return reverse('zinnia_tag_detail', args=[item.name])

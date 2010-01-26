"""Sitemaps for Zinnia"""
from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from tagging.models import Tag
from tagging.models import TaggedItem

from zinnia.models import Entry
from zinnia.models import Category
from zinnia.managers import entries_published
from zinnia.managers import authors_published


class EntrySitemap(Sitemap):
    """Sitemap for entries"""
    priority = 0.5
    changefreq = 'never'

    def items(self):
        return Entry.published.all()

    def lastmod(self, obj):
        return obj.last_update


class CategorySitemap(Sitemap):
    """Sitemap for categories"""
    changefreq = 'monthly'

    def cache(self, categories=[]):
        len_entries = float(Entry.published.count())
        self.cache_categories = {}
        for cat in categories:
            self.cache_categories[cat.pk] = \
                        entries_published(cat.entry_set).count() / len_entries

    def items(self):
        categories = Category.objects.all()
        self.cache(categories)
        return categories

    def lastmod(self, obj):
        entries = entries_published(obj.entry_set)
        if not entries:
            return None
        return entries[0].creation_date

    def priority(self, obj):
        priority = 0.5 + self.cache_categories[obj.pk]
        if priority > 1.0:
            priority = 1.0
        return '%.1f' % priority


class AuthorSitemap(Sitemap):
    """Sitemap for authors"""
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return authors_published()

    def lastmod(self, obj):
        entries = entries_published(obj.entry_set)
        if not entries:
            return None
        return entries[0].creation_date

    def location(self, obj):
        return reverse('zinnia:author_detail', args=[obj.username])


class TagSitemap(Sitemap):
    """Sitemap for tags"""
    changefreq = 'monthly'

    def cache(self, tags=[]):
        len_entries = float(Entry.published.count())
        self.cache_tags = {}
        for tag in tags:
            entries = TaggedItem.objects.get_by_model(Entry.published.all(), tag)
            self.cache_tags[tag.pk] = (entries, entries.count() / len_entries)

    def items(self):
        tags = Tag.objects.all()
        self.cache(tags)
        return tags

    def lastmod(self, obj):
        entries = self.cache_tags[obj.pk][0]
        if not entries:
            return None
        return entries[0].creation_date

    def priority(self, obj):
        priority = 0.5 + self.cache_tags[obj.pk][1]
        if priority > 1.0:
            priority = 1.0
        return '%.1f' % priority

    def location(self, obj):
        return reverse('zinnia:tagged_entry_list', args=[obj.name])

"""Sitemaps for Zinnia"""
from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from tagging.models import TaggedItem

from zinnia.models import Entry
from zinnia.models import Author
from zinnia.models import Category
from zinnia.managers import tags_published


class EntrySitemap(Sitemap):
    """Sitemap for entries"""
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        """Return published entries"""
        return Entry.published.all()

    def lastmod(self, obj):
        """Return last modification of an entry"""
        return obj.last_update


class CategorySitemap(Sitemap):
    """Sitemap for categories"""
    changefreq = 'monthly'

    def cache(self, categories):
        """Cache categorie's entries percent on total entries"""
        len_entries = float(Entry.published.count())
        self.cache_categories = {}
        for cat in categories:
            if len_entries:
                self.cache_categories[cat.pk] = cat.entries_published(
                    ).count() / len_entries
            else:
                self.cache_categories[cat.pk] = 0.0

    def items(self):
        """Return all categories with coeff"""
        categories = Category.objects.all()
        self.cache(categories)
        return categories

    def lastmod(self, obj):
        """Return last modification of a category"""
        entries = obj.entries_published()
        if not entries:
            return None
        return entries[0].creation_date

    def priority(self, obj):
        """Compute priority with cached coeffs"""
        priority = 0.5 + self.cache_categories[obj.pk]
        if priority > 1.0:
            priority = 1.0
        return '%.1f' % priority


class AuthorSitemap(Sitemap):
    """Sitemap for authors"""
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        """Return published authors"""
        return Author.published.all()

    def lastmod(self, obj):
        """Return last modification of an author"""
        entries = obj.entries_published()
        if not entries:
            return None
        return entries[0].creation_date

    def location(self, obj):
        """Return url of an author"""
        return reverse('zinnia_author_detail', args=[obj.username])


class TagSitemap(Sitemap):
    """Sitemap for tags"""
    changefreq = 'monthly'

    def cache(self, tags):
        """Cache tag's entries percent on total entries"""
        len_entries = float(Entry.published.count())
        self.cache_tags = {}
        for tag in tags:
            entries = TaggedItem.objects.get_by_model(
                Entry.published.all(), tag)
            self.cache_tags[tag.pk] = (entries, entries.count() / len_entries)

    def items(self):
        """Return all tags with coeff"""
        tags = tags_published()
        self.cache(tags)
        return tags

    def lastmod(self, obj):
        """Return last modification of a tag"""
        entries = self.cache_tags[obj.pk][0]
        return entries[0].creation_date

    def priority(self, obj):
        """Compute priority with cached coeffs"""
        priority = 0.5 + self.cache_tags[obj.pk][1]
        if priority > 1.0:
            priority = 1.0
        return '%.1f' % priority

    def location(self, obj):
        """Return url of a tag"""
        return reverse('zinnia_tag_detail', args=[obj.name])

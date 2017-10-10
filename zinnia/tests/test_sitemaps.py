"""Test cases for Zinnia's sitemaps"""
from django.contrib.sites.models import Site
from django.test import TestCase
from django.test.utils import override_settings

from zinnia.managers import PUBLISHED
from zinnia.models.author import Author
from zinnia.models.category import Category
from zinnia.models.entry import Entry
from zinnia.signals import disconnect_entry_signals
from zinnia.sitemaps import AuthorSitemap
from zinnia.sitemaps import CategorySitemap
from zinnia.sitemaps import EntrySitemap
from zinnia.sitemaps import TagSitemap
from zinnia.tests.utils import skip_if_custom_user


@skip_if_custom_user
@override_settings(
    ROOT_URLCONF='zinnia.tests.implementations.urls.default'
)
class SitemapsTestCase(TestCase):
    """Test cases for Sitemaps classes provided"""

    def setUp(self):
        disconnect_entry_signals()
        self.site = Site.objects.get_current()
        self.authors = [
            Author.objects.create(username='admin', email='admin@example.com'),
            Author.objects.create(username='user', email='user@example.com')]
        self.categories = [
            Category.objects.create(title='Category 1', slug='cat-1'),
            Category.objects.create(title='Category 2', slug='cat-2')]
        params = {'title': 'My entry 1', 'content': 'My content 1',
                  'tags': 'zinnia, test', 'slug': 'my-entry-1',
                  'status': PUBLISHED}
        self.entry_1 = Entry.objects.create(**params)
        self.entry_1.authors.add(*self.authors)
        self.entry_1.categories.add(*self.categories)
        self.entry_1.sites.add(self.site)

        params = {'title': 'My entry 2', 'content': 'My content 2',
                  'tags': 'zinnia', 'slug': 'my-entry-2',
                  'status': PUBLISHED}
        self.entry_2 = Entry.objects.create(**params)
        self.entry_2.authors.add(self.authors[0])
        self.entry_2.categories.add(self.categories[0])
        self.entry_2.sites.add(self.site)

        params = {'title': 'My entry draft', 'content': 'My content draft',
                  'tags': 'zinnia, tag', 'slug': 'my-entry-draft'}
        self.entry_draft = Entry.objects.create(**params)
        self.entry_draft.authors.add(self.authors[0])
        self.entry_draft.categories.add(self.categories[0])
        self.entry_draft.sites.add(self.site)

    def test_entry_sitemap(self):
        sitemap = EntrySitemap()
        with self.assertNumQueries(1):
            items = sitemap.items()
            self.assertEqual(len(items), 2)
        self.assertEqual(
            sitemap.lastmod(items[0]).replace(microsecond=0),
            self.entry_2.last_update.replace(microsecond=0))

    def test_category_sitemap(self):
        sitemap = CategorySitemap()
        with self.assertNumQueries(1):
            items = sitemap.items()
            self.assertEqual(len(items), 2)
        self.assertEqual(
            sitemap.lastmod(items[0]).replace(microsecond=0),
            self.entry_2.last_update.replace(microsecond=0))
        self.assertEqual(
            sitemap.lastmod(items[1]).replace(microsecond=0),
            self.entry_1.last_update.replace(microsecond=0))
        self.assertEqual(sitemap.priority(items[0]), '1.0')
        self.assertEqual(sitemap.priority(items[1]), '0.5')

    def test_author_sitemap(self):
        sitemap = AuthorSitemap()
        with self.assertNumQueries(1):
            items = sitemap.items()
            self.assertEqual(len(items), 2)
        self.assertEqual(
            sitemap.lastmod(items[0]).replace(microsecond=0),
            self.entry_2.last_update.replace(microsecond=0))
        self.assertEqual(
            sitemap.lastmod(items[1]).replace(microsecond=0),
            self.entry_1.last_update.replace(microsecond=0))
        self.assertEqual(sitemap.priority(items[0]), '1.0')
        self.assertEqual(sitemap.priority(items[1]), '0.5')

    def test_tag_sitemap(self):
        sitemap = TagSitemap()
        with self.assertNumQueries(3):
            items = sitemap.items()
            self.assertEqual(len(items), 2)
        self.assertEqual(
            sitemap.lastmod(items[1]).replace(microsecond=0),
            self.entry_2.last_update.replace(microsecond=0))
        self.assertEqual(
            sitemap.lastmod(items[0]).replace(microsecond=0),
            self.entry_1.last_update.replace(microsecond=0))
        self.assertEqual(sitemap.priority(items[1]), '1.0')
        self.assertEqual(sitemap.priority(items[0]), '0.5')
        self.assertEqual(sitemap.location(items[1]), '/tags/zinnia/')
        self.assertEqual(sitemap.location(items[0]), '/tags/test/')

    def test_empty_sitemap_issue_188(self):
        Entry.objects.all().delete()
        entry_sitemap = EntrySitemap()
        category_sitemap = CategorySitemap()
        author_sitemap = AuthorSitemap()
        tag_sitemap = TagSitemap()
        self.assertEqual(len(entry_sitemap.items()), 0)
        self.assertEqual(len(category_sitemap.items()), 0)
        self.assertEqual(len(author_sitemap.items()), 0)
        self.assertEqual(len(tag_sitemap.items()), 0)

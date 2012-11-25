"""Test cases for Zinnia's managers"""
from django.test import TestCase
from django.contrib.sites.models import Site

from tagging.models import Tag

from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.models.category import Category
from zinnia.tests.utils import datetime
from zinnia.managers import PUBLISHED
from zinnia.managers import tags_published
from zinnia.managers import entries_published


class ManagersTestCase(TestCase):

    def setUp(self):
        self.sites = [
            Site.objects.get_current(),
            Site.objects.create(domain='http://domain.com',
                                name='Domain.com')]
        self.authors = [
            Author.objects.create_user(username='webmaster',
                                       email='webmaster@example.com'),
            Author.objects.create_user(username='contributor',
                                       email='contributor@example.com')]
        self.categories = [
            Category.objects.create(title='Category 1',
                                    slug='category-1'),
            Category.objects.create(title='Category 2',
                                    slug='category-2')]

        params = {'title': 'My entry 1', 'content': 'My content 1',
                  'tags': 'zinnia, test', 'slug': 'my-entry-1',
                  'status': PUBLISHED}
        self.entry_1 = Entry.objects.create(**params)
        self.entry_1.authors.add(self.authors[0])
        self.entry_1.categories.add(*self.categories)
        self.entry_1.sites.add(*self.sites)

        params = {'title': 'My entry 2', 'content': 'My content 2',
                  'tags': 'zinnia, test', 'slug': 'my-entry-2'}
        self.entry_2 = Entry.objects.create(**params)
        self.entry_2.authors.add(*self.authors)
        self.entry_2.categories.add(self.categories[0])
        self.entry_2.sites.add(self.sites[0])

    def test_tags_published(self):
        self.assertEquals(tags_published().count(), Tag.objects.count())
        Tag.objects.create(name='out')
        self.assertNotEquals(tags_published().count(), Tag.objects.count())

    def test_author_published_manager_get_query_set(self):
        self.assertEquals(Author.published.count(), 1)
        self.entry_2.status = PUBLISHED
        self.entry_2.save()
        self.assertEquals(Author.published.count(), 2)
        self.entry_2.sites.remove(self.sites[0])
        self.entry_2.sites.add(self.sites[1])
        self.assertEquals(Author.published.count(), 1)

    def test_category_published_manager_get_query_set(self):
        category = Category.objects.create(
            title='Third Category', slug='third-category')
        self.assertEquals(Category.published.count(), 2)
        self.entry_2.categories.add(category)
        self.entry_2.status = PUBLISHED
        self.entry_2.save()
        self.assertEquals(Category.published.count(), 3)

    def test_entries_published(self):
        self.assertEquals(entries_published(Entry.objects.all()).count(), 1)
        self.entry_2.status = PUBLISHED
        self.entry_2.save()
        self.assertEquals(entries_published(Entry.objects.all()).count(), 2)
        self.entry_1.sites.clear()
        self.assertEquals(entries_published(Entry.objects.all()).count(), 1)
        self.entry_1.sites.add(*self.sites)
        self.entry_1.start_publication = datetime(2020, 1, 1)
        self.entry_1.save()
        self.assertEquals(entries_published(Entry.objects.all()).count(), 1)
        self.entry_1.start_publication = datetime(2000, 1, 1)
        self.entry_1.save()
        self.assertEquals(entries_published(Entry.objects.all()).count(), 2)
        self.entry_1.end_publication = datetime(2000, 1, 1)
        self.entry_1.save()
        self.assertEquals(entries_published(Entry.objects.all()).count(), 1)
        self.entry_1.end_publication = datetime(2020, 1, 1)
        self.entry_1.save()
        self.assertEquals(entries_published(Entry.objects.all()).count(), 2)

    def test_entry_published_manager_get_query_set(self):
        self.assertEquals(Entry.published.count(), 1)
        self.entry_2.status = PUBLISHED
        self.entry_2.save()
        self.assertEquals(Entry.published.count(), 2)
        self.entry_1.sites.clear()
        self.assertEquals(Entry.published.count(), 1)
        self.entry_1.sites.add(*self.sites)
        self.entry_1.start_publication = datetime(2020, 1, 1)
        self.entry_1.save()
        self.assertEquals(Entry.published.count(), 1)
        self.entry_1.start_publication = datetime(2000, 1, 1)
        self.entry_1.save()
        self.assertEquals(Entry.published.count(), 2)
        self.entry_1.end_publication = datetime(2000, 1, 1)
        self.entry_1.save()
        self.assertEquals(Entry.published.count(), 1)
        self.entry_1.end_publication = datetime(2020, 1, 1)
        self.entry_1.save()
        self.assertEquals(Entry.published.count(), 2)

    def test_entry_published_manager_on_site(self):
        self.assertEquals(Entry.published.on_site().count(), 2)
        self.entry_2.sites.clear()
        self.entry_2.sites.add(self.sites[1])
        self.assertEquals(Entry.published.on_site().count(), 1)
        self.entry_1.sites.clear()
        self.assertEquals(Entry.published.on_site().count(), 0)

    def test_entry_published_manager_basic_search(self):
        self.assertEquals(Entry.published.basic_search('My ').count(), 1)
        self.entry_2.status = PUBLISHED
        self.entry_2.save()
        self.assertEquals(Entry.published.basic_search('My ').count(), 2)
        self.assertEquals(Entry.published.basic_search('1').count(), 1)
        self.assertEquals(Entry.published.basic_search('content 1').count(), 2)

    def test_entry_published_manager_advanced_search(self):
        category = Category.objects.create(
            title='SimpleCategory', slug='simple')
        self.entry_2.categories.add(category)
        self.entry_2.tags = self.entry_2.tags + ', custom'
        self.entry_2.status = PUBLISHED
        self.entry_2.save()
        self.assertEquals(
            Entry.published.advanced_search('content').count(), 2)
        search = Entry.published.advanced_search('content 1')
        self.assertEquals(search.count(), 1)
        self.assertEquals(search.all()[0], self.entry_1)
        self.assertEquals(
            Entry.published.advanced_search('content 1 or 2').count(), 2)
        self.assertEquals(
            Entry.published.advanced_search('content 1 and 2').count(), 0)
        self.assertEquals(
            Entry.published.advanced_search('content 1 2').count(), 0)
        self.assertEquals(
            Entry.published.advanced_search('"My content" 1 or 2').count(), 2)
        self.assertEquals(
            Entry.published.advanced_search('-"My content" 2').count(), 0)
        search = Entry.published.advanced_search('content -1')
        self.assertEquals(search.count(), 1)
        self.assertEquals(search.all()[0], self.entry_2)
        self.assertEquals(Entry.published.advanced_search(
            'content category:SimpleCategory').count(), 1)
        self.assertEquals(Entry.published.advanced_search(
            'content category:simple').count(), 1)
        self.assertEquals(Entry.published.advanced_search(
            'content category:"Category 1"').count(), 2)
        self.assertEquals(Entry.published.advanced_search(
            'content category:"category-1"').count(), 2)
        self.assertEquals(Entry.published.advanced_search(
            'content category:"category-2"').count(), 1)
        self.assertEquals(Entry.published.advanced_search(
            'content tag:zinnia').count(), 2)
        self.assertEquals(Entry.published.advanced_search(
            'content tag:custom').count(), 1)
        self.assertEquals(Entry.published.advanced_search(
            'content author:webmaster').count(), 2)
        self.assertEquals(Entry.published.advanced_search(
            'content author:contributor').count(), 1)
        self.assertEquals(Entry.published.advanced_search(
            'content author:webmaster tag:zinnia').count(), 2)
        self.assertEquals(Entry.published.advanced_search(
            'content author:webmaster tag:custom').count(), 1)
        self.assertEquals(Entry.published.advanced_search(
            'content 1 or 2 author:webmaster').count(), 2)
        self.assertEquals(Entry.published.advanced_search(
            'content 1 or 2 author:webmaster').count(), 2)
        self.assertEquals(Entry.published.advanced_search(
            '(author:webmaster content) my').count(), 2)
        self.assertEquals(Entry.published.advanced_search(
            '(author:webmaster) or (author:contributor)').count(), 2)
        self.assertEquals(Entry.published.advanced_search(
            '(author:webmaster) (author:contributor)').count(), 0)
        self.assertEquals(Entry.published.advanced_search(
            '(author:webmaster content) 1').count(), 1)
        self.assertEquals(Entry.published.advanced_search(
            '(author:webmaster content) or 2').count(), 2)
        self.assertEquals(Entry.published.advanced_search(
            '(author:contributor content) or 1').count(), 2)
        self.assertEquals(Entry.published.advanced_search(
            '(author:contributor content) or 2').count(), 1)
        self.assertEquals(Entry.published.advanced_search(
            '(author:webmaster or ("hello world")) and 2').count(), 1)

        # Complex queries
        self.assertEquals(Entry.published.advanced_search(
            '(author:admin and "content 1") or author:webmaster').count(), 2)
        self.assertEquals(Entry.published.advanced_search(
            'author:admin and ("content 1" or author:webmaster)').count(), 0)
        self.assertEquals(Entry.published.advanced_search(
            'author:admin and "content 1" or author:webmaster').count(), 0)
        self.assertEquals(Entry.published.advanced_search(
            '-(author:webmaster and "content 1")').count(), 1)
        self.assertEquals(Entry.published.advanced_search(
            '-(-author:webmaster and "content 1")').count(), 2)
        self.assertEquals(Entry.published.advanced_search(
            'category:"category -1" or author:"web master"').count(), 0)
        self.assertEquals(Entry.published.advanced_search(
            'category:"category-1" or author:"webmaster"').count(), 2)

        # Wildcards
        self.assertEquals(Entry.published.advanced_search(
            'author:webm*').count(), 2)
        self.assertEquals(Entry.published.advanced_search(
            'author:*bmas*').count(), 2)
        self.assertEquals(Entry.published.advanced_search(
            'author:*master').count(), 2)
        self.assertEquals(Entry.published.advanced_search(
            'author:*master category:*ory-2').count(), 1)
        self.assertEquals(Entry.published.advanced_search(
            'author:*master or category:cate*').count(), 2)
        self.assertEquals(Entry.published.advanced_search(
            'category:*ate*').count(), 2)
        self.assertEquals(Entry.published.advanced_search(
            'author:"webmast*"').count(), 0)
        self.assertEquals(Entry.published.advanced_search(
            'tag:"zinnia*"').count(), 0)
        self.assertEquals(Entry.published.advanced_search(
            'tag:*inni*').count(), 2)

    def test_entry_published_manager_advanced_search_with_punctuation(self):
        self.entry_2.content = 'How are you today ? Fine thank you ! OK.'
        self.entry_2.status = PUBLISHED
        self.entry_2.save()
        self.assertEquals(Entry.published.advanced_search(
            'today ?').count(), 1)
        self.assertEquals(Entry.published.advanced_search(
            'today or ! or .').count(), 1)
        self.assertEquals(Entry.published.advanced_search(
            '"you today ?"').count(), 1)

    def test_entry_published_manager_search(self):
        self.entry_2.content = self.entry_2.content + ' * '
        self.entry_2.status = PUBLISHED
        self.entry_2.save()
        # Be sure that basic_search does not return
        # the same results of advanced_search
        self.assertNotEquals(
            Entry.published.basic_search('content 1').count(),
            Entry.published.advanced_search('content 1').count())
        # Now check the fallback with the '*' pattern
        # which will fails advanced search
        self.assertEquals(Entry.published.search('*').count(), 1)

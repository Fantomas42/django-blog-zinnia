"""Unit tests for zinnia"""
from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.comments.models import Comment

from tagging.models import Tag
from zinnia.models import Entry
from zinnia.models import Category
from zinnia.managers import DRAFT, HIDDEN, PUBLISHED
from zinnia.managers import tags_published
from zinnia.managers import entries_published
from zinnia.managers import authors_published

class ManagersTestCase(TestCase):

    def setUp(self):
        self.sites = [Site.objects.get_current(),
                      Site.objects.create(domain='http://domain.com',
                                          name='Domain.com')]
        self.authors = [User.objects.create_user(username='webmaster',
                                                 email='webmaster@example.com'),
                        User.objects.create_user(username='contributor',
                                                 email='contributor@example.com')]
        self.categories = [Category.objects.create(title='Category 1',
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

    def test_authors_published(self):
        self.assertEquals(authors_published().count(), 1)
        self.entry_2.status = PUBLISHED
        self.entry_2.save()
        self.assertEquals(authors_published().count(), 2)

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

    def test_entry_published_manager_search(self):
        self.assertEquals(Entry.published.search('My ').count(), 1)
        self.entry_2.status = PUBLISHED
        self.entry_2.save()
        self.assertEquals(Entry.published.search('My ').count(), 2)
        self.assertEquals(Entry.published.search('1').count(), 1)
        self.assertEquals(Entry.published.search('content 1').count(), 2)


class EntryTestCase(TestCase):

    def setUp(self):
        params = {'title': 'My entry',
                  'content': 'My content',
                  'tags': 'zinnia, test',
                  'slug': 'my-entry'}
        self.entry = Entry.objects.create(**params)


    def test_html_content(self):
        self.assertEquals(self.entry.html_content, '<p>My content</p>')

        self.entry.content = """Hello world !
        this is my content"""
        self.assertEquals(self.entry.html_content,
                          '<p>Hello world !<br />        this is my content</p>')

    def test_comments(self):
        site = Site.objects.get_current()

        self.assertEquals(self.entry.comments.count(), 0)
        Comment.objects.create(comment='My Comment 1',
                               content_object=self.entry,
                               site=site)
        self.assertEquals(self.entry.comments.count(), 1)
        Comment.objects.create(comment='My Comment 2',
                               content_object=self.entry,
                               site=site, is_public=False)
        self.assertEquals(self.entry.comments.count(), 1)
        Comment.objects.create(comment='My Comment 3',
                               content_object=self.entry,
                               site=Site.objects.create(domain='http://toto.com',
                                                        name='Toto.com'))
        self.assertEquals(self.entry.comments.count(), 2)

    def test_word_count(self):
        self.assertEquals(self.entry.word_count, 2)

    def test_is_actual(self):
        self.assertTrue(self.entry.is_actual)
        self.entry.start_publication = datetime(2020, 3, 15)
        self.assertFalse(self.entry.is_actual)
        self.entry.start_publication = datetime.now()
        self.assertTrue(self.entry.is_actual)
        self.entry.end_publication = datetime(2000, 3, 15)
        self.assertFalse(self.entry.is_actual)

    def test_is_visible(self):
        self.assertFalse(self.entry.is_visible)
        self.entry.status = PUBLISHED
        self.assertTrue(self.entry.is_visible)
        self.entry.start_publication = datetime(2020, 3, 15)
        self.assertFalse(self.entry.is_visible)

    def test_short_url(self):
        pass

    def test_previous_entry(self):
        self.assertFalse(self.entry.previous_entry)
        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'tags': 'zinnia, test',
                  'slug': 'my-second-entry',
                  'creation_date': datetime(2000, 1, 1),
                  'status': PUBLISHED}
        self.second_entry = Entry.objects.create(**params)
        self.second_entry.sites.add(Site.objects.get_current())
        self.assertEquals(self.entry.previous_entry, self.second_entry)
        params = {'title': 'My third entry',
                  'content': 'My third content',
                  'tags': 'zinnia, test',
                  'slug': 'my-third-entry',
                  'creation_date': datetime(2001, 1, 1),
                  'status': PUBLISHED}
        self.third_entry = Entry.objects.create(**params)
        self.third_entry.sites.add(Site.objects.get_current())
        self.assertEquals(self.entry.previous_entry, self.third_entry)
        self.assertEquals(self.third_entry.previous_entry, self.second_entry)

    def test_next_entry(self):
        self.assertFalse(self.entry.next_entry)
        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'tags': 'zinnia, test',
                  'slug': 'my-second-entry',
                  'creation_date': datetime(2100, 1, 1),
                  'status': PUBLISHED}
        self.second_entry = Entry.objects.create(**params)
        self.second_entry.sites.add(Site.objects.get_current())
        self.assertEquals(self.entry.next_entry, self.second_entry)
        params = {'title': 'My third entry',
                  'content': 'My third content',
                  'tags': 'zinnia, test',
                  'slug': 'my-third-entry',
                  'creation_date': datetime(2050, 1, 1),
                  'status': PUBLISHED}
        self.third_entry = Entry.objects.create(**params)
        self.third_entry.sites.add(Site.objects.get_current())
        self.assertEquals(self.entry.next_entry, self.third_entry)
        self.assertEquals(self.third_entry.next_entry, self.second_entry)

    def test_related_published_set(self):
        self.assertFalse(self.entry.related_published_set)
        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'tags': 'zinnia, test',
                  'slug': 'my-second-entry',
                  'status': PUBLISHED}
        self.second_entry = Entry.objects.create(**params)
        self.second_entry.related.add(self.entry)
        self.assertEquals(len(self.entry.related_published_set), 0)
        
        self.second_entry.sites.add(Site.objects.get_current())
        self.assertEquals(len(self.entry.related_published_set), 1)
        self.assertEquals(len(self.second_entry.related_published_set), 0)
        
        self.entry.status = PUBLISHED
        self.entry.save()
        self.entry.sites.add(Site.objects.get_current())
        self.assertEquals(len(self.entry.related_published_set), 1)
        self.assertEquals(len(self.second_entry.related_published_set), 1)
        

class CategoryTestCase(TestCase):

    def setUp(self):
        self.site = Site.objects.get_current()
        self.categories = [Category.objects.create(title='Category 1',
                                                   slug='category-1'),
                           Category.objects.create(title='Category 2',
                                                   slug='category-2')]
        params = {'title': 'My entry',
                  'content': 'My content',
                  'tags': 'zinnia, test',
                  'slug': 'my-entry'}

        self.entry = Entry.objects.create(**params)
        self.entry.categories.add(*self.categories)
        self.entry.sites.add(self.site)

    def test_entries_published_set(self):
        category = self.categories[0]
        self.assertEqual(category.entries_published_set().count(), 0)
        self.entry.status = PUBLISHED
        self.entry.save()
        self.assertEqual(category.entries_published_set().count(), 1)

        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'tags': 'zinnia, test',
                  'status': PUBLISHED,
                  'slug': 'my-second-entry'}

        new_entry = Entry.objects.create(**params)
        new_entry.sites.add(self.site)
        new_entry.categories.add(self.categories[0])

        self.assertEqual(self.categories[0].entries_published_set().count(), 2)
        self.assertEqual(self.categories[1].entries_published_set().count(), 1)




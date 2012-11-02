"""Test cases for Zinnia's Author"""
from django.test import TestCase
from django.contrib.sites.models import Site

from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.managers import PUBLISHED


class AuthorTestCase(TestCase):

    def setUp(self):
        self.site = Site.objects.get_current()
        self.author = Author.objects.create_user(
            'webmaster', 'webmaster@example.com')
        params = {'title': 'My entry',
                  'content': 'My content',
                  'tags': 'zinnia, test',
                  'slug': 'my-entry'}

        self.entry = Entry.objects.create(**params)
        self.entry.authors.add(self.author)
        self.entry.sites.add(self.site)

    def test_entries_published(self):
        self.assertEqual(self.author.entries_published().count(), 0)
        self.entry.status = PUBLISHED
        self.entry.save()
        self.assertEqual(self.author.entries_published().count(), 1)

    def test_unicode(self):
        self.assertEqual(self.author.__unicode__(),
                         'webmaster')
        self.author.first_name = 'John'
        self.author.last_name = 'Doe'
        self.author.save()
        self.assertEqual(self.author.__unicode__(),
                         'John Doe')

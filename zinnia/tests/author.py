"""Test cases for Zinnia's Author"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from zinnia.models import Entry
from zinnia.models import Author
from zinnia.managers import PUBLISHED



class AuthorTestCase(TestCase):

    def setUp(self):
        self.site = Site.objects.get_current()
        self.user = User.objects.create_user(
            'webmaster', 'webmaster@example.com')
        params = {'title': 'My entry',
                  'content': 'My content',
                  'tags': 'zinnia, test',
                  'slug': 'my-entry'}

        self.entry = Entry.objects.create(**params)
        self.entry.authors.add(self.user)
        self.entry.sites.add(self.site)
        self.author = Author.objects.get(username='webmaster')

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

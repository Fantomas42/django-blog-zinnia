"""Test cases for Zinnia's Author"""
from django.test import TestCase
from django.contrib.sites.models import Site
from django.contrib.auth.tests.utils import skipIfCustomUser
from django.contrib.auth import get_user_model

from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.managers import PUBLISHED


@skipIfCustomUser
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

    def test_str(self):
        self.assertEqual(self.author.__str__(),
                         'webmaster')
        self.author.first_name = 'John'
        self.assertEqual(self.author.__str__(),
                         'John')
        self.author.last_name = 'Doe'
        self.assertEqual(self.author.__str__(),
                         'John Doe')

    def test_for_pollution(self):
        self.assertEqual(get_user_model(),
                         get_user_model().objects.model)
        self.assertNotEqual(get_user_model().objects.model,
                            Author)

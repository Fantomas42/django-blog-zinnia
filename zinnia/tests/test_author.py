"""Test cases for Zinnia's Author"""
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase

from zinnia.managers import PUBLISHED
from zinnia.models.author import Author
from zinnia.models.entry import Entry
from zinnia.signals import disconnect_entry_signals
from zinnia.tests.utils import skip_if_custom_user


@skip_if_custom_user
class AuthorTestCase(TestCase):

    def setUp(self):
        disconnect_entry_signals()
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
        self.author.last_name = 'Doe'
        self.assertEqual(self.author.__str__(),
                         'Doe')
        self.author.first_name = 'John'
        self.assertEqual(self.author.__str__(),
                         'John')

    def test_manager_pollution(self):
        """
        https://github.com/Fantomas42/django-blog-zinnia/pull/307
        """
        self.assertNotEqual(get_user_model().objects.model,
                            Author)

"""Test cases for Zinnia's long_enought spam checker"""
from django.test import TestCase
from django.contrib import comments
from django.contrib.sites.models import Site

from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.managers import PUBLISHED
from zinnia.spam_checker.backends.long_enough import backend


class LongEnoughTestCase(TestCase):
    """Test cases for zinnia.spam_checker.long_enough"""

    def setUp(self):
        self.site = Site.objects.get_current()
        self.author = Author.objects.create(username='admin',
                                            email='admin@example.com')

        params = {'title': 'My test entry',
                  'content': 'My test entry',
                  'slug': 'my-test-entry',
                  'status': PUBLISHED}
        self.entry = Entry.objects.create(**params)
        self.entry.sites.add(self.site)
        self.entry.authors.add(self.author)

    def test_long_enough(self):
        comment = comments.get_model().objects.create(
            comment='My Comment', user=self.author, is_public=True,
            content_object=self.entry, site=self.site)
        self.assertEquals(backend(comment, self.entry, {}), True)

        comment.comment = 'Hello I just wanted to thank for great article'
        comment.save()
        self.assertEquals(backend(comment, self.entry, {}), False)

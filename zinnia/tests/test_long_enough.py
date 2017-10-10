"""Test cases for Zinnia's long_enought spam checker"""
from django.contrib.sites.models import Site
from django.test import TestCase
from django.utils import timezone

import django_comments as comments

from zinnia.managers import PUBLISHED
from zinnia.models.author import Author
from zinnia.models.entry import Entry
from zinnia.signals import disconnect_discussion_signals
from zinnia.signals import disconnect_entry_signals
from zinnia.spam_checker.backends.long_enough import backend
from zinnia.tests.utils import skip_if_custom_user


@skip_if_custom_user
class LongEnoughTestCase(TestCase):
    """Test cases for zinnia.spam_checker.long_enough"""

    def setUp(self):
        disconnect_entry_signals()
        disconnect_discussion_signals()
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
            content_object=self.entry, site=self.site,
            submit_date=timezone.now())
        self.assertEqual(backend(comment, self.entry, {}), True)

        comment.comment = 'Hello I just wanted to thank for great article'
        comment.save()
        self.assertEqual(backend(comment, self.entry, {}), False)

"""Test cases for Zinnia's signals"""
from django.contrib.sites.models import Site
from django.test import TestCase
from django.utils import timezone

import django_comments as comments

from zinnia.managers import PUBLISHED
from zinnia.models.entry import Entry
from zinnia.signals import connect_discussion_signals
from zinnia.signals import disconnect_discussion_signals
from zinnia.signals import disconnect_entry_signals


class CommentDenormalizationTestCase(TestCase):

    def setUp(self):
        disconnect_entry_signals()
        disconnect_discussion_signals()
        params = {'title': 'My entry',
                  'status': PUBLISHED,
                  'slug': 'my-entry'}
        self.entry = Entry.objects.create(**params)
        self.site = Site.objects.get_current()

    def test_count_after_deletion_issue_283(self):
        comment_klass = comments.get_model()
        connect_discussion_signals()

        comment_klass.objects.create(
            comment='My Comment 1', site=self.site,
            content_object=self.entry, submit_date=timezone.now())
        comment_klass.objects.create(
            comment='My Comment 2', site=self.site,
            content_object=self.entry, submit_date=timezone.now())

        # It's normal, the signals are not catched on the creation
        self.assertEqual(self.entry.comment_count, 0)
        self.entry.comment_count = 2
        self.entry.save()

        comment_klass.objects.all().delete()
        self.assertEqual(comment_klass.objects.count(), 0)

        entry_reloaded = Entry.objects.get(pk=self.entry.pk)
        self.assertEqual(entry_reloaded.comment_count, 0)

        disconnect_discussion_signals()

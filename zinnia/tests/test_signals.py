"""Test cases for Zinnia's signals"""
from django.test import TestCase

import zinnia.signals
from zinnia import settings
from zinnia.managers import DRAFT
from zinnia.managers import PUBLISHED
from zinnia.models.entry import Entry
from zinnia.signals import disable_for_loaddata
from zinnia.signals import disconnect_discussion_signals
from zinnia.signals import disconnect_entry_signals
from zinnia.signals import ping_directories_handler
from zinnia.signals import ping_external_urls_handler


class SignalsTestCase(TestCase):
    """Test cases for signals"""

    def setUp(self):
        disconnect_entry_signals()
        disconnect_discussion_signals()

    def test_disable_for_loaddata(self):
        self.top = 0

        @disable_for_loaddata
        def make_top():
            self.top += 1

        def call():
            return make_top()

        call()
        self.assertEqual(self.top, 1)
        # Okay the command is executed

    def test_ping_directories_handler(self):
        # Set up a stub around DirectoryPinger
        self.top = 0

        def fake_pinger(*ka, **kw):
            self.top += 1

        original_pinger = zinnia.signals.DirectoryPinger
        zinnia.signals.DirectoryPinger = fake_pinger

        params = {'title': 'My entry',
                  'content': 'My content',
                  'status': PUBLISHED,
                  'slug': 'my-entry'}
        entry = Entry.objects.create(**params)
        self.assertEqual(entry.is_visible, True)
        settings.PING_DIRECTORIES = ()
        ping_directories_handler('sender', **{'instance': entry})
        self.assertEqual(self.top, 0)
        settings.PING_DIRECTORIES = ('toto',)
        settings.SAVE_PING_DIRECTORIES = True
        ping_directories_handler('sender', **{'instance': entry})
        self.assertEqual(self.top, 1)
        entry.status = DRAFT
        ping_directories_handler('sender', **{'instance': entry})
        self.assertEqual(self.top, 1)

        # Remove stub
        zinnia.signals.DirectoryPinger = original_pinger

    def test_ping_external_urls_handler(self):
        # Set up a stub around ExternalUrlsPinger
        self.top = 0

        def fake_pinger(*ka, **kw):
            self.top += 1

        self.original_pinger = zinnia.signals.ExternalUrlsPinger
        zinnia.signals.ExternalUrlsPinger = fake_pinger

        params = {'title': 'My entry',
                  'content': 'My content',
                  'status': PUBLISHED,
                  'slug': 'my-entry'}
        entry = Entry.objects.create(**params)
        self.assertEqual(entry.is_visible, True)
        settings.SAVE_PING_EXTERNAL_URLS = False
        ping_external_urls_handler('sender', **{'instance': entry})
        self.assertEqual(self.top, 0)
        settings.SAVE_PING_EXTERNAL_URLS = True
        ping_external_urls_handler('sender', **{'instance': entry})
        self.assertEqual(self.top, 1)
        entry.status = 0
        ping_external_urls_handler('sender', **{'instance': entry})
        self.assertEqual(self.top, 1)

        # Remove stub
        zinnia.signals.ExternalUrlsPinger = self.original_pinger

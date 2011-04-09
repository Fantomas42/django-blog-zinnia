"""Test cases for Zinnia's moderator"""
from django.core import mail
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType

from zinnia import moderator
from zinnia.models import Entry
from zinnia.managers import PUBLISHED
from zinnia.moderator import EntryCommentModerator


class EntryCommentModeratorTestCase(TestCase):
    """Test cases for the moderator"""

    def setUp(self):
        self.notification_recipients = moderator.MAIL_COMMENT_NOTIFICATION_RECIPIENTS
        moderator.MAIL_COMMENT_NOTIFICATION_RECIPIENTS = ['admin@example.com']
        self.site = Site.objects.get_current()
        self.author = User.objects.create(username='admin',
                                          email='admin@example.com')
        self.entry_ct_id = ContentType.objects.get_for_model(Entry).pk

        params = {'title': 'My test entry',
                  'content': 'My test entry',
                  'slug': 'my-test-entry',
                  'status': PUBLISHED}
        self.entry = Entry.objects.create(**params)
        self.entry.sites.add(self.site)
        self.entry.authors.add(self.author)

    def tearDown(self):
        moderator.MAIL_COMMENT_NOTIFICATION_RECIPIENTS = self.notification_recipients

    def test_email(self):
        comment = Comment.objects.create(comment='My Comment',
                                         user=self.author, is_public=True,
                                         content_object=self.entry,
                                         site=self.site)
        self.assertEquals(len(mail.outbox), 0)
        moderator = EntryCommentModerator(Entry)
        moderator.email(comment, self.entry, 'request')
        self.assertEquals(len(mail.outbox), 1)

    def test_email_reply(self):
        comment = Comment.objects.create(comment='My Comment 1',
                                         user=self.author, is_public=True,
                                         content_object=self.entry,
                                         site=self.site)
        moderator = EntryCommentModerator(Entry)
        moderator.email_notification_reply = True
        moderator.email_reply(comment, self.entry, 'request')
        self.assertEquals(len(mail.outbox), 0)

        comment = Comment.objects.create(comment='My Comment 2',
                                         user_email='user_1@example.com',
                                         content_object=self.entry,
                                         is_public=True, site=self.site)
        moderator.email_reply(comment, self.entry, 'request')
        self.assertEquals(len(mail.outbox), 0)

        comment = Comment.objects.create(comment='My Comment 3',
                                         user_email='user_2@example.com',
                                         content_object=self.entry,
                                         is_public=True, site=self.site)
        moderator.email_reply(comment, self.entry, 'request')
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].to, [u'user_1@example.com'])

        comment = Comment.objects.create(comment='My Comment 4',
                                         user=self.author, is_public=True,
                                         content_object=self.entry,
                                         site=self.site)
        moderator.email_reply(comment, self.entry, 'request')
        self.assertEquals(len(mail.outbox), 2)
        self.assertEquals(mail.outbox[1].to, [u'user_1@example.com',
                                              u'user_2@example.com'])

        pingback = Comment.objects.create(comment='My pingback',
                                          user=self.author, is_public=True,
                                          content_object=self.entry,
                                          site=self.site)
        pingback.flags.create(user=self.author, flag='pingback')
        moderator.email_reply(pingback, self.entry, 'request')
        self.assertEquals(len(mail.outbox), 2)

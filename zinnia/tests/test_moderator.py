"""Test cases for Zinnia's moderator"""
from django.core import mail
from django.test import TestCase
from django.utils import timezone

try:
    import django_comments as comments
except ImportError:
    from django.contrib import comments

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

try:
    from django_comments.forms import CommentForm
except ImportError:
    from django.contrib.comments.forms import CommentForm

from django.test.utils import restore_template_loaders
from django.test.utils import setup_test_template_loader

try:
    from django_comments.moderation import moderator as moderator_stack
except ImportError:
    from django.contrib.comments.moderation import moderator as moderator_stack

from django.contrib.auth.tests.utils import skipIfCustomUser

from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.managers import PUBLISHED
from zinnia.moderator import EntryCommentModerator
from zinnia.signals import connect_discussion_signals
from zinnia.signals import disconnect_discussion_signals
from zinnia.signals import disconnect_entry_signals


@skipIfCustomUser
class CommentModeratorTestCase(TestCase):
    """Test cases for the moderator"""

    def setUp(self):
        disconnect_entry_signals()
        disconnect_discussion_signals()
        setup_test_template_loader(
            {'comments/comment_authors_email.txt': '',
             'comments/comment_notification_email.txt': '',
             'comments/comment_reply_email.txt': ''})

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

    def tearDown(self):
        restore_template_loaders()

    def test_email(self):
        comment = comments.get_model().objects.create(
            comment='My Comment', user=self.author, is_public=True,
            content_object=self.entry, submit_date=timezone.now(),
            site=self.site)
        self.assertEqual(len(mail.outbox), 0)
        moderator = EntryCommentModerator(Entry)
        moderator.email_reply = False
        moderator.email_authors = False
        moderator.mail_comment_notification_recipients = []
        moderator.email(comment, self.entry, 'request')
        self.assertEqual(len(mail.outbox), 0)
        moderator.email_reply = True
        moderator.email_authors = True
        moderator.mail_comment_notification_recipients = ['admin@example.com']
        moderator.email(comment, self.entry, 'request')
        self.assertEqual(len(mail.outbox), 1)

    def test_do_email_notification(self):
        comment = comments.get_model().objects.create(
            comment='My Comment', user=self.author, is_public=True,
            content_object=self.entry, submit_date=timezone.now(),
            site=self.site)
        self.assertEqual(len(mail.outbox), 0)
        moderator = EntryCommentModerator(Entry)
        moderator.mail_comment_notification_recipients = ['admin@example.com']
        moderator.do_email_notification(comment, self.entry, 'request')
        self.assertEqual(len(mail.outbox), 1)

    def test_do_email_authors(self):
        comment = comments.get_model().objects.create(
            comment='My Comment', user=self.author, is_public=True,
            content_object=self.entry, submit_date=timezone.now(),
            site=self.site)
        self.assertEqual(len(mail.outbox), 0)
        moderator = EntryCommentModerator(Entry)
        moderator.email_authors = True
        moderator.mail_comment_notification_recipients = [
            'admin@example.com', 'webmaster@example.com']
        moderator.do_email_authors(comment, self.entry, 'request')
        self.assertEqual(len(mail.outbox), 0)
        moderator.mail_comment_notification_recipients = []
        moderator.do_email_authors(comment, self.entry, 'request')
        self.assertEqual(len(mail.outbox), 1)

    def test_do_email_authors_without_email(self):
        """
        https://github.com/Fantomas42/django-blog-zinnia/issues/145
        """
        comment = comments.get_model().objects.create(
            comment='My Comment', user=self.author, is_public=True,
            content_object=self.entry, submit_date=timezone.now(),
            site=self.site)
        self.assertEqual(len(mail.outbox), 0)
        moderator = EntryCommentModerator(Entry)
        moderator.email_authors = True
        moderator.mail_comment_notification_recipients = []
        contributor = Author.objects.create(username='contributor',
                                            email='contrib@example.com')
        self.entry.authors.add(contributor)
        moderator.do_email_authors(comment, self.entry, 'request')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            set(mail.outbox[0].to),
            set(['admin@example.com', 'contrib@example.com']))
        mail.outbox = []
        contributor.email = ''
        contributor.save()
        moderator.do_email_authors(comment, self.entry, 'request')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['admin@example.com'])

    def test_do_email_reply(self):
        comment = comments.get_model().objects.create(
            comment='My Comment 1', user=self.author, is_public=True,
            content_object=self.entry, submit_date=timezone.now(),
            site=self.site)
        moderator = EntryCommentModerator(Entry)
        moderator.email_notification_reply = True
        moderator.mail_comment_notification_recipients = [
            'admin@example.com', 'webmaster@example.com']
        moderator.do_email_reply(comment, self.entry, 'request')
        self.assertEqual(len(mail.outbox), 0)

        comment = comments.get_model().objects.create(
            comment='My Comment 2', user_email='user_1@example.com',
            content_object=self.entry, is_public=True,
            submit_date=timezone.now(), site=self.site)
        moderator.do_email_reply(comment, self.entry, 'request')
        self.assertEqual(len(mail.outbox), 0)

        comment = comments.get_model().objects.create(
            comment='My Comment 3', user_email='user_2@example.com',
            content_object=self.entry, is_public=True,
            submit_date=timezone.now(), site=self.site)
        moderator.do_email_reply(comment, self.entry, 'request')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].bcc, ['user_1@example.com'])

        comment = comments.get_model().objects.create(
            comment='My Comment 4', user=self.author, is_public=True,
            content_object=self.entry, submit_date=timezone.now(),
            site=self.site)
        moderator.do_email_reply(comment, self.entry, 'request')
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            set(mail.outbox[1].bcc),
            set(['user_1@example.com', 'user_2@example.com']))

    def test_moderate(self):
        comment = comments.get_model().objects.create(
            comment='My Comment', user=self.author, is_public=True,
            content_object=self.entry, submit_date=timezone.now(),
            site=self.site)
        moderator = EntryCommentModerator(Entry)
        moderator.auto_moderate_comments = True
        moderator.spam_checker_backends = ()
        self.assertTrue(moderator.moderate(comment, self.entry, 'request'))
        moderator.auto_moderate_comments = False
        self.assertFalse(moderator.moderate(comment, self.entry, 'request'))
        moderator.spam_checker_backends = (
            'zinnia.spam_checker.backends.all_is_spam',)
        self.assertTrue(moderator.moderate(comment, self.entry, 'request'))

    def test_moderate_comment_on_entry_without_author(self):
        self.entry.authors.clear()
        comment = comments.get_model().objects.create(
            comment='My Comment', user=self.author, is_public=True,
            content_object=self.entry, submit_date=timezone.now(),
            site=self.site)
        moderator = EntryCommentModerator(Entry)
        moderator.auto_moderate_comments = False
        moderator.spam_checker_backends = (
            'zinnia.spam_checker.backends.all_is_spam',)
        self.assertTrue(moderator.moderate(comment, self.entry, 'request'))

    def test_integrity_error_on_duplicate_spam_comments(self):
        class AllIsSpamModerator(EntryCommentModerator):
            spam_checker_backends = [
                'zinnia.spam_checker.backends.all_is_spam']

        moderator_stack.unregister(Entry)
        moderator_stack.register(Entry, AllIsSpamModerator)

        datas = {'name': 'Jim Bob',
                 'email': 'jim.bob@example.com',
                 'url': '',
                 'comment': 'This is my comment'}

        f = CommentForm(self.entry)
        datas.update(f.initial)
        url = reverse('comments-post-comment')
        self.assertEqual(self.entry.comment_count, 0)
        connect_discussion_signals()
        self.client.post(url, datas)
        self.client.post(url, datas)
        disconnect_discussion_signals()
        self.assertEqual(comments.get_model().objects.count(), 1)
        entry_reloaded = Entry.objects.get(pk=self.entry.pk)
        self.assertEqual(entry_reloaded.comment_count, 0)

    def test_comment_count_denormalization(self):
        class AllIsSpamModerator(EntryCommentModerator):
            spam_checker_backends = [
                'zinnia.spam_checker.backends.all_is_spam']

        class NoMailNoSpamModerator(EntryCommentModerator):
            def email(self, *ka, **kw):
                pass

            def moderate(self, *ka, **kw):
                return False

        datas = {'name': 'Jim Bob',
                 'email': 'jim.bob@example.com',
                 'url': '',
                 'comment': 'This is my comment'}

        f = CommentForm(self.entry)
        datas.update(f.initial)
        url = reverse('comments-post-comment')

        moderator_stack.unregister(Entry)
        moderator_stack.register(Entry, AllIsSpamModerator)

        self.assertEqual(self.entry.comment_count, 0)
        connect_discussion_signals()
        self.client.post(url, datas)
        entry_reloaded = Entry.objects.get(pk=self.entry.pk)
        self.assertEqual(entry_reloaded.comment_count, 0)

        moderator_stack.unregister(Entry)
        moderator_stack.register(Entry, NoMailNoSpamModerator)

        datas['comment'] = 'This a published comment'
        self.client.post(url, datas)
        disconnect_discussion_signals()
        entry_reloaded = Entry.objects.get(pk=self.entry.pk)
        self.assertEqual(entry_reloaded.comment_count, 1)

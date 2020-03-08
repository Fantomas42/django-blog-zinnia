"""Moderator of Zinnia comments"""
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.template import loader
from django.utils.translation import activate
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from django_comments.moderation import CommentModerator

from zinnia.settings import AUTO_CLOSE_COMMENTS_AFTER
from zinnia.settings import AUTO_MODERATE_COMMENTS
from zinnia.settings import MAIL_COMMENT_AUTHORS
from zinnia.settings import MAIL_COMMENT_NOTIFICATION_RECIPIENTS
from zinnia.settings import MAIL_COMMENT_REPLY
from zinnia.settings import PROTOCOL
from zinnia.settings import SPAM_CHECKER_BACKENDS
from zinnia.spam_checker import check_is_spam


class EntryCommentModerator(CommentModerator):
    """
    Moderate the comments on entries.
    """
    email_reply = MAIL_COMMENT_REPLY
    email_authors = MAIL_COMMENT_AUTHORS
    enable_field = 'comment_enabled'
    auto_close_field = 'start_publication'
    close_after = AUTO_CLOSE_COMMENTS_AFTER
    spam_checker_backends = SPAM_CHECKER_BACKENDS
    auto_moderate_comments = AUTO_MODERATE_COMMENTS
    mail_comment_notification_recipients = MAIL_COMMENT_NOTIFICATION_RECIPIENTS

    def moderate(self, comment, entry, request):
        """
        Determine if a new comment should be marked as non-public
        and await approval.
        Return ``True`` to put the comment into the moderator queue,
        or ``False`` to allow it to be showed up immediately.
        """
        if self.auto_moderate_comments:
            return True

        if check_is_spam(comment, entry, request,
                         self.spam_checker_backends):
            return True

        return False

    def email(self, comment, entry, request):
        """
        Send email notifications needed.
        """
        current_language = get_language()
        try:
            activate(settings.LANGUAGE_CODE)
            site = Site.objects.get_current()
            if self.auto_moderate_comments or comment.is_public:
                self.do_email_notification(comment, entry, site)
            if comment.is_public:
                self.do_email_authors(comment, entry, site)
                self.do_email_reply(comment, entry, site)
        finally:
            activate(current_language)

    def do_email_notification(self, comment, entry, site):
        """
        Send email notification of a new comment to site staff.
        """
        if not self.mail_comment_notification_recipients:
            return

        template = loader.get_template(
            'comments/zinnia/entry/email/notification.txt')
        context = {
            'comment': comment,
            'entry': entry,
            'site': site,
            'protocol': PROTOCOL
        }
        subject = _('[%(site)s] New comment posted on "%(title)s"') % \
            {'site': site.name, 'title': entry.title}
        message = template.render(context)

        send_mail(
            subject, message,
            settings.DEFAULT_FROM_EMAIL,
            self.mail_comment_notification_recipients,
            fail_silently=not settings.DEBUG
        )

    def do_email_authors(self, comment, entry, site):
        """
        Send email notification of a new comment to
        the authors of the entry.
        """
        if not self.email_authors:
            return

        exclude_list = self.mail_comment_notification_recipients + ['']
        recipient_list = (
            set([author.email for author in entry.authors.all()])
            - set(exclude_list)
        )
        if not recipient_list:
            return

        template = loader.get_template(
            'comments/zinnia/entry/email/authors.txt')
        context = {
            'comment': comment,
            'entry': entry,
            'site': site,
            'protocol': PROTOCOL
        }
        subject = _('[%(site)s] New comment posted on "%(title)s"') % \
            {'site': site.name, 'title': entry.title}
        message = template.render(context)

        send_mail(
            subject, message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=not settings.DEBUG
        )

    def do_email_reply(self, comment, entry, site):
        """
        Send email notification of a new comment to
        the authors of the previous comments.
        """
        if not self.email_reply:
            return

        exclude_list = (
            self.mail_comment_notification_recipients
            + [author.email for author in entry.authors.all()]
            + [comment.email]
        )
        recipient_list = (
            set([other_comment.email
                 for other_comment in entry.comments
                 if other_comment.email])
            - set(exclude_list)
        )
        if not recipient_list:
            return

        template = loader.get_template(
            'comments/zinnia/entry/email/reply.txt')
        context = {
            'comment': comment,
            'entry': entry,
            'site': site,
            'protocol': PROTOCOL
        }
        subject = _('[%(site)s] New comment posted on "%(title)s"') % \
            {'site': site.name, 'title': entry.title}
        message = template.render(context)

        mail = EmailMessage(
            subject, message,
            settings.DEFAULT_FROM_EMAIL,
            bcc=recipient_list)
        mail.send(fail_silently=not settings.DEBUG)

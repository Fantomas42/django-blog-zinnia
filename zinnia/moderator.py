"""Moderator of Zinnia comments"""
from django.conf import settings
from django.template import Context
from django.template import loader
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.contrib.sites.models import Site
from django.utils.translation import activate
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
from django.contrib.comments.moderation import CommentModerator

from zinnia.settings import PROTOCOL
from zinnia.settings import MAIL_COMMENT_REPLY
from zinnia.settings import MAIL_COMMENT_AUTHORS
from zinnia.settings import AUTO_MODERATE_COMMENTS
from zinnia.settings import AUTO_CLOSE_COMMENTS_AFTER
from zinnia.settings import MAIL_COMMENT_NOTIFICATION_RECIPIENTS
from zinnia.settings import SPAM_CHECKER_BACKENDS
from zinnia.spam_checker import check_is_spam


class EntryCommentModerator(CommentModerator):
    """Moderate the comment of Entry"""
    email_reply = MAIL_COMMENT_REPLY
    email_authors = MAIL_COMMENT_AUTHORS
    enable_field = 'comment_enabled'
    auto_close_field = 'start_publication'
    close_after = AUTO_CLOSE_COMMENTS_AFTER
    spam_checker_backends = SPAM_CHECKER_BACKENDS
    auto_moderate_comments = AUTO_MODERATE_COMMENTS
    mail_comment_notification_recipients = MAIL_COMMENT_NOTIFICATION_RECIPIENTS

    def email(self, comment, content_object, request):
        if comment.is_public:
            current_language = get_language()
            try:
                activate(settings.LANGUAGE_CODE)
                if self.mail_comment_notification_recipients:
                    self.do_email_notification(comment, content_object,
                                               request)
                if self.email_authors:
                    self.do_email_authors(comment, content_object,
                                          request)
                if self.email_reply:
                    self.do_email_reply(comment, content_object, request)
            finally:
                activate(current_language)

    def do_email_notification(self, comment, content_object, request):
        """Send email notification of a new comment to site staff when email
        notifications have been requested."""
        site = Site.objects.get_current()
        template = loader.get_template(
            'comments/comment_notification_email.txt')
        context = Context({'comment': comment, 'site': site,
                           'protocol': PROTOCOL,
                           'content_object': content_object})
        subject = _('[%(site)s] New comment posted on "%(title)s"') % \
            {'site': site.name, 'title': content_object.title}
        message = template.render(context)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                  self.mail_comment_notification_recipients,
                  fail_silently=not settings.DEBUG)

    def do_email_authors(self, comment, content_object, request):
        """Send email notification of a new comment to the authors of the
        entry when email notifications have been requested."""
        exclude_list = self.mail_comment_notification_recipients + ['']
        recipient_list = set(
            [author.email for author in content_object.authors.all()]) - \
            set(exclude_list)
        if recipient_list:
            site = Site.objects.get_current()
            template = loader.get_template(
                'comments/comment_authors_email.txt')
            context = Context({'comment': comment, 'site': site,
                               'protocol': PROTOCOL,
                               'content_object': content_object})
            subject = _('[%(site)s] New comment posted on "%(title)s"') % \
                {'site': site.name, 'title': content_object.title}
            message = template.render(context)
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                      recipient_list, fail_silently=not settings.DEBUG)

    def do_email_reply(self, comment, content_object, request):
        """Send email notification of a new comment to the authors of
        the previous comments when email notifications have been requested."""
        exclude_list = self.mail_comment_notification_recipients + \
            [author.email for author in content_object.authors.all()] + \
            [comment.email]
        recipient_list = set(
            [other_comment.email for other_comment in content_object.comments
             if other_comment.email]) - set(exclude_list)
        if recipient_list:
            site = Site.objects.get_current()
            template = loader.get_template('comments/comment_reply_email.txt')
            context = Context({'comment': comment, 'site': site,
                               'protocol': PROTOCOL,
                               'content_object': content_object})
            subject = _('[%(site)s] New comment posted on "%(title)s"') % \
                {'site': site.name, 'title': content_object.title}
            message = template.render(context)
            mail = EmailMessage(subject, message,
                                settings.DEFAULT_FROM_EMAIL,
                                bcc=recipient_list)
            mail.send(fail_silently=not settings.DEBUG)

    def moderate(self, comment, content_object, request):
        """Determine whether a given comment on a given object should be
        allowed to show up immediately, or should be marked non-public
        and await approval."""
        if self.auto_moderate_comments:
            return True

        if check_is_spam(comment, content_object, request,
                         self.spam_checker_backends):
            return True

        return False

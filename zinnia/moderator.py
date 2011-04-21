"""Moderator of Zinnia comments
   Based on Akismet for checking spams."""
from django.conf import settings
from django.template import Context
from django.template import loader
from django.core.mail import send_mail
from django.utils.encoding import smart_str
from django.contrib.sites.models import Site
from django.utils.translation import activate
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
from django.contrib.comments.moderation import CommentModerator

from zinnia.settings import PROTOCOL
from zinnia.settings import MAIL_COMMENT_REPLY
from zinnia.settings import AUTO_MODERATE_COMMENTS
from zinnia.settings import AUTO_CLOSE_COMMENTS_AFTER
from zinnia.settings import MAIL_COMMENT_NOTIFICATION_RECIPIENTS
from zinnia.settings import AKISMET_COMMENT

AKISMET_API_KEY = getattr(settings, 'AKISMET_SECRET_API_KEY', '')


class EntryCommentModerator(CommentModerator):
    """Moderate the comment of Entry"""
    email_reply = MAIL_COMMENT_REPLY
    enable_field = 'comment_enabled'
    auto_close_field = 'start_publication'
    close_after = AUTO_CLOSE_COMMENTS_AFTER
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
                  {'site': site.name,
                   'title': content_object.title}
        message = template.render(context)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                  self.mail_comment_notification_recipients,
                  fail_silently=not settings.DEBUG)

    def do_email_reply(self, comment, content_object, request):
        """Send email notification of a new comment to the authors of
        the previous comments when email notifications have been requested."""
        exclude_list = self.mail_comment_notification_recipients + \
                       [comment.userinfo['email']]
        recipient_list = set([comment.userinfo['email']
                              for comment in content_object.comments
                              if comment.userinfo['email']]) ^ \
                              set(exclude_list)

        if recipient_list:
            site = Site.objects.get_current()
            template = loader.get_template('comments/comment_reply_email.txt')
            context = Context({'comment': comment, 'site': site,
                               'protocol': PROTOCOL,
                               'content_object': content_object})
            subject = _('[%(site)s] New comment posted on "%(title)s"') % \
                      {'site': site.name,
                       'title': content_object.title}
            message = template.render(context)
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                      recipient_list, fail_silently=not settings.DEBUG)

    def moderate(self, comment, content_object, request):
        """Determine whether a given comment on a given object should be
        allowed to show up immediately, or should be marked non-public
        and await approval."""
        if self.auto_moderate_comments:
            return True

        if not AKISMET_COMMENT or not AKISMET_API_KEY:
            return False

        try:
            from akismet import Akismet
            from akismet import APIKeyError
        except ImportError:
            return False

        akismet = Akismet(key=AKISMET_API_KEY,
                          blog_url='%s://%s/' % (
                              PROTOCOL, Site.objects.get_current().domain))
        if akismet.verify_key():
            akismet_data = {
                'user_ip': request.META.get('REMOTE_ADDR', ''),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'referrer': request.META.get('HTTP_REFERER', 'unknown'),
                'permalink': content_object.get_absolute_url(),
                'comment_type': 'comment',
                'comment_author': smart_str(comment.userinfo.get('name', '')),
                'comment_author_email': smart_str(comment.userinfo.get(
                    'email', '')),
                'comment_author_url': smart_str(comment.userinfo.get(
                    'url', '')),
            }
            is_spam = akismet.comment_check(smart_str(comment.comment),
                                            data=akismet_data,
                                            build_data=True)
            if is_spam:
                comment.save()
                user = comment.content_object.authors.all()[0]
                comment.flags.create(user=user, flag='spam')
            return is_spam
        raise APIKeyError('Your Akismet API key is invalid.')

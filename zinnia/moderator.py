"""Moderator of Zinnia comments
   Based on Akismet for checking spams."""
from django.conf import settings
from django.template import Context
from django.template import loader
from django.core.mail import send_mail
from django.utils.encoding import smart_str
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.contrib.comments.moderation import CommentModerator

from zinnia.settings import PROTOCOL
from zinnia.settings import MAIL_COMMENT
from zinnia.settings import MAIL_COMMENT_REPLY
from zinnia.settings import AKISMET_COMMENT


AKISMET_API_KEY = getattr(settings, 'AKISMET_SECRET_API_KEY', '')

class EntryCommentModerator(CommentModerator):
    """Moderate the comment of Entry"""
    email_notification = MAIL_COMMENT
    email_notification_reply = MAIL_COMMENT_REPLY
    enable_field = 'comment_enabled'

    def email(self, comment, content_object, request):
        if comment.is_public:
            super(EntryCommentModerator, self).email(comment, content_object, request)
            self.email_reply(comment, content_object, request)

    def email_reply(self, comment, content_object, request):
        """Send email notification of a new comment to site staff when email
        notifications have been requested."""
        if not self.email_notification_reply:
            return

        exclude_list = [manager_tuple[1] for manager_tuple
                        in settings.MANAGERS] + [comment.user_email,]
        recipient_list = set([comment.userinfo['email']
                              for comment in content_object.comments
                              if comment.userinfo['email']]) ^ set(exclude_list)

        if recipient_list:
            site = Site.objects.get_current()
            t = loader.get_template('comments/comment_reply_email.txt')
            c = Context({'comment': comment, 'site': site,
                         'protocol': PROTOCOL,
                         'content_object': content_object})
            subject = _('[%(site)s] New comment posted on "%(title)s"') % \
                      {'site': site.name,
                       'title': content_object.title}
            message = t.render(c)
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                      recipient_list, fail_silently=not settings.DEBUG)

    def moderate(self, comment, content_object, request):
        """Need to pass Akismet test"""
        if not AKISMET_COMMENT:
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
                'comment_author_email': smart_str(comment.userinfo.get('email', '')),
                'comment_author_url': smart_str(comment.userinfo.get('url', '')),
            }
            is_spam = akismet.comment_check(smart_str(comment.comment),
                                            data=akismet_data,
                                            build_data=True)
            if is_spam:
                comment.save()
                user = comment.content_object.authors.all()[0]
                comment.flags.create(user=user, flag='spam')
            return is_spam
        raise APIKeyError("Your Akismet API key is invalid.")


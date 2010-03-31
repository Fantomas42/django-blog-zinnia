"""Moderator of Zinnia comments
   Based on Akismet for checking spams
   Need to override the default Moderator,
   for getting request in parameters."""
from django.conf import settings
from django.utils.encoding import smart_str
from django.contrib.sites.models import Site
from django.db.models import signals
from django.contrib import comments
from django.contrib.comments.signals import comment_will_be_posted
from django.contrib.comments.moderation import Moderator
from django.contrib.comments.moderation import CommentModerator

from zinnia.settings import MAIL_COMMENT
from zinnia.settings import AKISMET_COMMENT


AKISMET_API_KEY = getattr(settings, 'AKISMET_API_KEY', '')

class EntryCommentModerator(CommentModerator):
    """Moderate the comment of Entry"""
    email_notification = MAIL_COMMENT
    enable_field = 'comment_enabled'

    def email(self, comment, content_object):
        if comment.is_public:
            super(EntryCommentModerator, self).email(comment, content_object)

    def moderate_akismet(self, comment, content_object, request):
        """Need to pass Akismet test"""
        if not AKISMET_COMMENT:
            return False

        try:
            from akismet import Akismet
            from akismet import APIKeyError
        except ImportError:
            return False

        akismet = Akismet(key=AKISMET_API_KEY,
                    blog_url='http://%s/' % Site.objects.get_current().domain)
        if akismet.verify_key():
            akismet_data = {
                'user_ip': request.META.get('REMOTE_ADDR', ''),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'referrer': request.META.get('HTTP_REFERER', 'unknown'),
                'permalink': content_object.get_absolute_url(),
                'comment_type': 'comment',
                'comment_author': comment.userinfo.get('name', ''),
                'comment_author_email': comment.userinfo.get('email', ''),
                'comment_author_url': comment.userinfo.get('url', ''),
            }
            return akismet.comment_check(smart_str(comment.comment),
                                         data=akismet_data,
                                         build_data=True)
        raise APIKeyError("Your Akismet API key is invalid.")


class EntryModerator(Moderator):
    """Moderator for Entry"""

    def connect(self):
        comment_will_be_posted.connect(self.pre_save_moderation,
                                        sender=comments.get_model())
        signals.post_save.connect(self.post_save_moderation,
                                    sender=comments.get_model())

    def pre_save_moderation(self, sender, comment, request, **kwargs):
        """Overriding the existing method by passing request to allow"""
        super(EntryModerator, self).pre_save_moderation(sender, comment,
                                                        **kwargs)

        moderation_class = self._registry[comment.content_type.model_class()]
        if moderation_class.moderate_akismet(comment, comment.content_object,
                                            request):
            comment.is_public = False

moderator = EntryModerator()

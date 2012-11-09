"""TypePad spam checker backend for Zinnia"""
from django.conf import settings
from django.utils.encoding import smart_str
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured

from zinnia.settings import PROTOCOL

try:
    from akismet import Akismet
    from akismet import APIKeyError
except ImportError:
    raise ImproperlyConfigured('akismet module is not available')

if not getattr(settings, 'TYPEPAD_SECRET_API_KEY', ''):
    raise ImproperlyConfigured('You have to set TYPEPAD_SECRET_API_KEY')

TYPEPAD_API_KEY = settings.TYPEPAD_SECRET_API_KEY


class TypePad(Akismet):
    """TypePad version of the Akismet module"""
    baseurl = 'api.antispam.typepad.com/1.1/'


def backend(comment, content_object, request):
    """TypePad spam checker backend for Zinnia"""
    blog_url = '%s://%s/' % (PROTOCOL, Site.objects.get_current().domain)

    typepad = TypePad(key=TYPEPAD_API_KEY, blog_url=blog_url)

    if not typepad.verify_key():
        raise APIKeyError('Your Typepad API key is invalid.')

    typepad_data = {
        'user_ip': request.META.get('REMOTE_ADDR', ''),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'referrer': request.META.get('HTTP_REFERER', 'unknown'),
        'permalink': content_object.get_absolute_url(),
        'comment_type': 'comment',
        'comment_author': smart_str(comment.name),
        'comment_author_email': smart_str(comment.email),
        'comment_author_url': smart_str(comment.url),
    }
    is_spam = typepad.comment_check(smart_str(comment.comment),
                                    data=typepad_data, build_data=True)
    return is_spam

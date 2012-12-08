"""Comment flags for Zinnia"""
from django.contrib.auth.models import User
from django.utils.functional import memoize

from zinnia.settings import COMMENT_FLAG_USER_ID

PINGBACK = 'pingback'
TRACKBACK = 'trackback'

user_flagger_ = {}


def _get_user_flagger():
    try:
        user = User.objects.get(pk=COMMENT_FLAG_USER_ID)
    except User.DoesNotExist:
        user = User.objects.create_user('Zinnia-Flagger')
    return user

get_user_flagger = memoize(_get_user_flagger, user_flagger_, 0)

"""Comment flags for Zinnia"""
from django.contrib.auth import get_user_model
from django.utils.functional import memoize

from zinnia.settings import COMMENT_FLAG_USER_ID

PINGBACK = 'pingback'
TRACKBACK = 'trackback'
FLAGGER_USERNAME = 'Zinnia-Flagger'

user_flagger_ = {}


def _get_user_flagger():
    User = get_user_model()
    try:
        user = User.objects.get(pk=COMMENT_FLAG_USER_ID)
    except User.DoesNotExist:
        try:
            user = User.objects.get(username=FLAGGER_USERNAME)
        except User.DoesNotExist:
            user = User.objects.create_user(FLAGGER_USERNAME)
    return user

get_user_flagger = memoize(_get_user_flagger, user_flagger_, 0)

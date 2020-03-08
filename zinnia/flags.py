"""Comment flags for Zinnia"""
from functools import lru_cache

from django.contrib.auth import get_user_model

from zinnia.settings import COMMENT_FLAG_USER_ID

PINGBACK = 'pingback'
TRACKBACK = 'trackback'
FLAGGER_USERNAME = 'Zinnia-Flagger'


@lru_cache(1)
def get_user_flagger():
    """
    Return an User instance used by the system
    when flagging a comment as trackback or pingback.
    """
    user_klass = get_user_model()
    try:
        user = user_klass.objects.get(pk=COMMENT_FLAG_USER_ID)
    except user_klass.DoesNotExist:
        try:
            user = user_klass.objects.get(
                **{user_klass.USERNAME_FIELD: FLAGGER_USERNAME})
        except user_klass.DoesNotExist:
            user = user_klass.objects.create_user(FLAGGER_USERNAME)
    return user

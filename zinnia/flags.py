"""Comment flags for Zinnia"""
from django.utils.lru_cache import lru_cache
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
    User = get_user_model()
    try:
        user = User.objects.get(pk=COMMENT_FLAG_USER_ID)
    except User.DoesNotExist:
        try:
            user = User.objects.get(**{User.USERNAME_FIELD: FLAGGER_USERNAME})
        except User.DoesNotExist:
            user = User.objects.create_user(FLAGGER_USERNAME)
    return user

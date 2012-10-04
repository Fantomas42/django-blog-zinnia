"""Comment flags for Zinnia"""
from django.contrib.auth.models import User
from django.utils.functionnal import memoize

from zinnia.settings import COMMENT_FLAG_USER_ID


user_flagger_ = {}


@memoize(user_flagger_, 0)
def get_user_flagger():
    try:
        user = User.objects.get(pk=COMMENT_FLAG_USER_ID)
    except User.DoesNotExist:
        user = User.objects.create_user('Zinnia-Flagger')
    return user

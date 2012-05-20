"""Long enough spam checker backend for Zinnia"""
from zinnia.settings import COMMENT_MIN_WORDS


def backend(comment, content_object, request):
    """Backend checking if the comment posted is long enough to be public.
    Generally a comments with few words is useless. The will avoid
    comments like this :

    - First !
    - I don't like.
    - Check http://spam-ads.com/
    """
    return len(comment.comment.split()) < COMMENT_MIN_WORDS

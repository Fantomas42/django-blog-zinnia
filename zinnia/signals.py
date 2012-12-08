"""Signal handlers of Zinnia"""
import inspect
from functools import wraps

from django.db.models import F
from django.dispatch import Signal
from django.contrib import comments
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.contrib.comments.signals import comment_was_posted
from django.contrib.comments.signals import comment_was_flagged

from zinnia import settings
from zinnia.models.entry import Entry

comment_model = comments.get_model()
ENTRY_PS_PING_DIRECTORIES = 'zinnia.entry.post_save.ping_directories'
ENTRY_PS_PING_EXTERNAL_URLS = 'zinnia.entry.post_save.ping_external_urls'
COMMENT_PS_COUNT_DISCUSSIONS = 'zinnia.comment.post_save.count_discussions'
COMMENT_PD_COUNT_DISCUSSIONS = 'zinnia.comment.pre_delete.count_discussions'
COMMENT_WF_COUNT_DISCUSSIONS = 'zinnia.comment.was_flagged.count_discussions'
COMMENT_WP_COUNT_COMMENTS = 'zinnia.comment.was_posted.count_comments'
PINGBACK_WP_COUNT_PINGBACKS = 'zinnia.pingback.was_flagged.count_pingbacks'
TRACKBACK_WP_COUNT_TRACKBACKS = 'zinnia.trackback.was_flagged.count_trackbacks'

pingback_was_posted = Signal(providing_args=['pingback', 'entry'])
trackback_was_posted = Signal(providing_args=['trackback', 'entry'])


def disable_for_loaddata(signal_handler):
    """
    Decorator for disabling signals sent by 'post_save'
    on loaddata command.
    http://code.djangoproject.com/ticket/8399
    """
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        for fr in inspect.stack():
            if inspect.getmodulename(fr[1]) == 'loaddata':
                return
        signal_handler(*args, **kwargs)

    return wrapper


@disable_for_loaddata
def ping_directories_handler(sender, **kwargs):
    """
    Ping directories when an entry is saved.
    """
    entry = kwargs['instance']

    if entry.is_visible and settings.SAVE_PING_DIRECTORIES:
        from zinnia.ping import DirectoryPinger

        for directory in settings.PING_DIRECTORIES:
            DirectoryPinger(directory, [entry])


@disable_for_loaddata
def ping_external_urls_handler(sender, **kwargs):
    """
    Ping externals URLS when an entry is saved.
    """
    entry = kwargs['instance']

    if entry.is_visible and settings.SAVE_PING_EXTERNAL_URLS:
        from zinnia.ping import ExternalUrlsPinger

        ExternalUrlsPinger(entry)


def count_discussions_handler(sender, **kwargs):
    """
    Update the count of each type of discussion on an entry.
    """
    if kwargs.get('instance') and kwargs.get('created'):
        # The signal is emitted by the comment creation,
        # so we do nothing, comment_was_posted is used instead.
        return

    comment = 'comment' in kwargs and kwargs['comment'] or kwargs['instance']
    entry = comment.content_object

    if isinstance(entry, Entry):
        entry.comment_count = entry.comments.count()
        entry.pingback_count = entry.pingbacks.count()
        entry.trackback_count = entry.trackbacks.count()
        entry.save(force_update=True)


def count_comments_handler(sender, **kwargs):
    """
    Update Entry.comment_count when a comment was posted.
    """
    entry = kwargs['comment'].content_object
    if isinstance(entry, Entry):
        entry.comment_count = F('comment_count') + 1
        entry.save(force_update=True)


def count_pingbacks_handler(sender, **kwargs):
    """
    Update Entry.pingback_count when a pingback was posted.
    """
    entry = kwargs['entry']
    entry.pingback_count = F('pingback_count') + 1
    entry.save(force_update=True)


def count_trackbacks_handler(sender, **kwargs):
    """
    Update Entry.trackback_count when a trackback was posted.
    """
    entry = kwargs['entry']
    entry.trackback_count = F('trackback_count') + 1
    entry.save(force_update=True)


def connect_entry_signals():
    """
    Connect all the signals on Entry model.
    """
    post_save.connect(
        ping_directories_handler, sender=Entry,
        dispatch_uid=ENTRY_PS_PING_DIRECTORIES)
    post_save.connect(
        ping_external_urls_handler, sender=Entry,
        dispatch_uid=ENTRY_PS_PING_EXTERNAL_URLS)


def disconnect_entry_signals():
    """
    Disconnect all the signals on Entry model.
    """
    post_save.disconnect(
        sender=Entry,
        dispatch_uid=ENTRY_PS_PING_DIRECTORIES)
    post_save.disconnect(
        sender=Entry,
        dispatch_uid=ENTRY_PS_PING_EXTERNAL_URLS)


def connect_discussion_signals():
    """
    Connect all the signals on the Comment model to
    maintains a valid discussion count on each entries
    when an action is done with the comments.
    """
    post_save.connect(
        count_discussions_handler, sender=comment_model,
        dispatch_uid=COMMENT_PS_COUNT_DISCUSSIONS)
    pre_delete.connect(
        count_discussions_handler, sender=comment_model,
        dispatch_uid=COMMENT_PD_COUNT_DISCUSSIONS)
    comment_was_flagged.connect(
        count_discussions_handler, sender=comment_model,
        dispatch_uid=COMMENT_WF_COUNT_DISCUSSIONS)
    comment_was_posted.connect(
        count_comments_handler, sender=comment_model,
        dispatch_uid=COMMENT_WP_COUNT_COMMENTS)
    pingback_was_posted.connect(
        count_pingbacks_handler, sender=comment_model,
        dispatch_uid=PINGBACK_WP_COUNT_PINGBACKS)
    trackback_was_posted.connect(
        count_trackbacks_handler, sender=comment_model,
        dispatch_uid=TRACKBACK_WP_COUNT_TRACKBACKS)


def disconnect_discussion_signals():
    """
    Disconnect all the signals on Comment model
    provided by Zinnia.
    """
    post_save.disconnect(
        sender=comment_model,
        dispatch_uid=COMMENT_PS_COUNT_DISCUSSIONS)
    pre_delete.disconnect(
        sender=comment_model,
        dispatch_uid=COMMENT_PD_COUNT_DISCUSSIONS)
    comment_was_flagged.disconnect(
        sender=comment_model,
        dispatch_uid=COMMENT_WF_COUNT_DISCUSSIONS)
    comment_was_posted.disconnect(
        sender=comment_model,
        dispatch_uid=COMMENT_WP_COUNT_COMMENTS)
    pingback_was_posted.disconnect(
        sender=comment_model,
        dispatch_uid=PINGBACK_WP_COUNT_PINGBACKS)
    trackback_was_posted.disconnect(
        sender=comment_model,
        dispatch_uid=TRACKBACK_WP_COUNT_TRACKBACKS)

"""Signal handlers of Zinnia"""
from django.db.models.signals import post_save

from zinnia import settings


def ping_directories_handler(sender, **kwargs):
    """Ping Directories when an entry is saved"""
    entry = kwargs['instance']

    if entry.is_visible and settings.SAVE_PING_DIRECTORIES:
        from zinnia.ping import DirectoryPinger

        for directory in settings.PING_DIRECTORIES:
            DirectoryPinger(directory, [entry])


def ping_external_urls_handler(sender, **kwargs):
    """Ping Externals URLS when an entry is saved"""
    entry = kwargs['instance']

    if entry.is_visible and settings.SAVE_PING_EXTERNAL_URLS:
        from zinnia.ping import ExternalUrlsPinger

        ExternalUrlsPinger(entry)


def disconnect_zinnia_signals():
    """Disconnect all the signals provided by Zinnia"""
    from zinnia.models import Entry

    post_save.disconnect(
        sender=Entry, dispatch_uid='zinnia.entry.post_save.ping_directories')
    post_save.disconnect(
        sender=Entry, dispatch_uid='zinnia.entry.post_save.ping_external_urls')

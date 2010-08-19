"""Signal handlers of Zinnia"""
from zinnia import settings

def ping_directories_handler(sender, **kwargs):
    """Ping Directories when an entry is saved"""
    entry = kwargs['instance']

    if entry.is_visible and settings.SAVE_PING_DIRECTORIES:
        from zinnia.ping import DirectoryPinger

        for directory in settings.PING_DIRECTORIES:
            DirectoryPinger(directory, [entry,])


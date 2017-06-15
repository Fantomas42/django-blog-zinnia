"""Apps for Zinnia"""
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ZinniaConfig(AppConfig):
    """
    Config for Zinnia application.
    """
    name = 'zinnia'
    label = 'zinnia'
    verbose_name = _('Weblog')

    def ready(self):
        from django_comments.moderation import moderator

        import swapper

        from zinnia.signals import connect_entry_signals
        from zinnia.signals import connect_discussion_signals
        from zinnia.moderator import EntryCommentModerator

        entry_klass = swapper.load_model('zinnia', 'Entry')
        # Register the comment moderator on Entry
        moderator.register(entry_klass, EntryCommentModerator)
        # Connect the signals
        connect_entry_signals()
        connect_discussion_signals()

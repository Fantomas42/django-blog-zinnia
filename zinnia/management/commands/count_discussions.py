"""
Management command for re-counting the discussions on Entry.
"""
import sys

from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str

from zinnia.models.entry import Entry
from zinnia.signals import disconnect_entry_signals


class Command(BaseCommand):
    """
    Command for re-counting the discussions on entries
    in case of problems.
    """
    help = 'Refresh all the discussion counts on entries'

    def write_out(self, message, verbosity_level=1):
        """
        Convenient method for outputing.
        """
        if self.verbosity and self.verbosity >= verbosity_level:
            sys.stdout.write(smart_str(message))
            sys.stdout.flush()

    def handle(self, *args, **options):
        disconnect_entry_signals()
        self.verbosity = int(options.get('verbosity', 1))
        for entry in Entry.objects.all():
            self.write_out('Processing %s\n' % entry.title)
            changed = False
            comment_count = entry.comments.count()
            pingback_count = entry.pingbacks.count()
            trackback_count = entry.trackbacks.count()

            if entry.comment_count != comment_count:
                changed = True
                self.write_out('- %s comments found, %s before\n' % (
                    comment_count, entry.comment_count))
                entry.comment_count = comment_count

            if entry.pingback_count != pingback_count:
                changed = True
                self.write_out('- %s pingbacks found, %s before\n' % (
                    pingback_count, entry.pingback_count))
                entry.pingback_count = pingback_count

            if entry.trackback_count != trackback_count:
                changed = True
                self.write_out('- %s trackbacks found, %s before\n' % (
                    trackback_count, entry.trackback_count))
                entry.trackback_count = trackback_count

            if changed:
                self.write_out('- Updating...\n')
                entry.save()

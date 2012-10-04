"""Spam cleanup command module for Zinnia"""
from django.contrib import comments
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import NoArgsCommand

from zinnia.flags import SPAM
from zinnia.models.entry import Entry


class Command(NoArgsCommand):
    """Command object for removing comments
    flagged as spam"""
    help = "Remove entry's comments flagged as spam."

    def handle_noargs(self, **options):
        verbosity = int(options.get('verbosity', 1))

        content_type = ContentType.objects.get_for_model(Entry)
        spams = comments.get_model().objects.filter(is_public=False,
                                                    content_type=content_type,
                                                    flags__flag=SPAM)
        spams_count = spams.count()
        spams.delete()

        if verbosity:
            print '%i spam comments deleted.' % spams_count

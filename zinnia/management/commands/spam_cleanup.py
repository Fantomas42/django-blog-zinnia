"""Spam cleanup command module for Zinnia"""
from django.contrib import comments
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import NoArgsCommand

from zinnia.models.entry import Entry


class Command(NoArgsCommand):
    """
    Command object for removing comments
    marked as non-public and removed.
    """
    help = "Delete the entries's comments marked as non-public and removed."

    def handle_noargs(self, **options):
        verbosity = int(options.get('verbosity', 1))

        content_type = ContentType.objects.get_for_model(Entry)
        spams = comments.get_model().objects.filter(
            is_public=False, is_removed=True,
            content_type=content_type)
        spams_count = spams.count()
        spams.delete()

        if verbosity:
            print '%i spam comments deleted.' % spams_count

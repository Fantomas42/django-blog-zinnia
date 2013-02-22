"""Views for Zinnia random entry"""
from django.views.generic.base import RedirectView

from zinnia.models.entry import Entry


class EntryRandom(RedirectView):
    """
    View for handling a random entry
    simply do a redirection after the random selection
    """
    permanent = False

    def get_redirect_url(self, **kwargs):
        """
        Get entry corresponding to 'pk' and
        return the get_absolute_url of the entry
        """
        entry = Entry.published.all().order_by('?')[0]
        return entry.get_absolute_url()

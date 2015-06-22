"""Views for Zinnia shortlink"""
from django.shortcuts import get_object_or_404
from django.views.generic.base import RedirectView

from zinnia.models.entry import Entry


class EntryShortLink(RedirectView):
    """
    View for handling the shortlink of an Entry,
    simply do a redirection.
    """
    permanent = True

    def get_redirect_url(self, **kwargs):
        """
        Get entry corresponding to 'pk' encoded in base36
        in the 'token' variable and return the get_absolute_url
        of the entry.
        """
        entry = get_object_or_404(Entry.published, pk=int(kwargs['token'], 36))
        return entry.get_absolute_url()

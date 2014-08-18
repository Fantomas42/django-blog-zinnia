"""Views for Zinnia shortlink"""
from django.http import Http404
from django.views.generic.base import RedirectView
from django.utils.translation import ugettext as _

from zinnia.models.entry import Entry
from zinnia.views.mixins.entry_preview import EntryPreviewMixin


class EntryShortLinkMixin(object):
    """
    Mixin implementing the preview of Entries.
    """

    def get_object(self, queryset=None):
        try:
            return queryset.get()
        except Entry.DoesNotExist:
            raise Http404(_('No entry found matching the query'))


class EntryShortLink(RedirectView, EntryPreviewMixin, EntryShortLinkMixin):
    """
    View for handling the shortlink of an Entry,
    simply do a redirection.
    """

    def get_redirect_url(self, **kwargs):
        """
        Get entry corresponding to 'pk' encoded in base36
        in the 'token' variable and return the get_absolute_url
        of the entry.
        """
        pk = int(kwargs['token'], 36)
        entry = self.get_object(Entry.objects.filter(pk=pk))
        return entry.get_absolute_url()

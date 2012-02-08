"""Views for Zinnia channels"""
from django.views.generic.list_detail import object_list

from zinnia.models import Entry


def entry_channel(request, query, **kwargs):
    """View for displaying a custom selection of entries
    based on a search pattern, useful for SEO/SMO pages"""
    queryset = Entry.published.search(query)
    return object_list(request, queryset=queryset,
                       **kwargs)

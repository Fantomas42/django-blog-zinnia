"""Views for zinnia entries"""
from django.views.generic.list_detail import object_list

from zinnia.models import Entry

def entry_channel(request, query, *ka, **kw):
    """Display a custom selection of entries"""
    queryset = Entry.published.search(query)
    return object_list(request, queryset=queryset,
                       *ka, **kw)


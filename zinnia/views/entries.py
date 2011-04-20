"""Views for Zinnia entries"""
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from django.views.generic.date_based import archive_year
from django.views.generic.date_based import archive_month
from django.views.generic.date_based import archive_day
from django.views.generic.date_based import object_detail

from zinnia.models import Entry
from zinnia.views.decorators import protect_entry
from zinnia.views.decorators import update_queryset


entry_index = update_queryset(object_list, Entry.published.all)

entry_year = update_queryset(archive_year, Entry.published.all)

entry_month = update_queryset(archive_month, Entry.published.all)

entry_day = update_queryset(archive_day, Entry.published.all)

entry_detail = protect_entry(object_detail)


def entry_shortlink(request, object_id):
    """
    Redirect to the 'get_absolute_url' of an Entry,
    accordingly to 'object_id' argument
    """
    entry = get_object_or_404(Entry, pk=object_id)
    return redirect(entry, permanent=True)

"""Views for Zinnia archives

TODO: 1. Switch to class-based views
      2. Implement pagination
      3. Implement custom template name for the date
      4. Better archive_week view
         - Offset -1 from the week URL
         - Use European convention
         - End date in context
         - Review template
"""
from datetime import date

from django.views.generic.list_detail import object_list
from django.views.generic.date_based import archive_year
from django.views.generic.date_based import archive_week
from django.views.generic.date_based import archive_month
from django.views.generic.date_based import archive_day

from zinnia.models import Entry
from zinnia.views.decorators import update_queryset


entry_index = update_queryset(object_list, Entry.published.all)

entry_year = update_queryset(archive_year, Entry.published.all)

entry_week = update_queryset(archive_week, Entry.published.all)

entry_month = update_queryset(archive_month, Entry.published.all)

entry_day = update_queryset(archive_day, Entry.published.all)


def entry_today(request, **kwargs):
    """View for the entries of the day, the entry_day view
    is just used with the parameters of the current date."""
    today = date.today()
    kwargs.update({'year': today.year,
                   'month': today.month,
                   'day': today.day})
    if not kwargs.get('template_name'):
        kwargs['template_name'] = 'zinnia/entry_archive_today.html'

    return entry_day(request, **kwargs)

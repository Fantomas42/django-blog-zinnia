"""Views for Zinnia archives

TODO: 1. Switch to class-based views OK
      2. Implement pagination OK
      3. Implement custom template name for the date
      4. Better archive_week view
         - Offset -1 from the week URL
         - Use European convention
         - End date in context
         - Review template
"""
from django.views.generic.dates import ArchiveIndexView
from django.views.generic.dates import YearArchiveView
from django.views.generic.dates import MonthArchiveView
from django.views.generic.dates import WeekArchiveView
from django.views.generic.dates import DayArchiveView
from django.views.generic.dates import TodayArchiveView

from zinnia.models import Entry
from zinnia.views.mixins import ArchiveMixin
from zinnia.views.mixins import CallableQuerysetMixin


class ArchiveCallableQuerysetMixin(ArchiveMixin, CallableQuerysetMixin):
    """Mixin combinating the ArchiveMixin configuration,
    and a callable queryset to force her update"""
    queryset = Entry.published.all


class EntryIndex(ArchiveCallableQuerysetMixin, ArchiveIndexView):
    """View returning the archive index"""
    context_object_name = 'entry_list'


class EntryYear(ArchiveCallableQuerysetMixin, YearArchiveView):
    """View returning the archive for a year"""
    make_object_list = True


class EntryMonth(ArchiveCallableQuerysetMixin, MonthArchiveView):
    """View returning the archive for a month"""


class EntryWeek(ArchiveCallableQuerysetMixin, WeekArchiveView):
    """View returning the archive for a week"""


class EntryDay(ArchiveCallableQuerysetMixin, DayArchiveView):
    """View returning the archive for a day"""


class EntryToday(ArchiveCallableQuerysetMixin, TodayArchiveView):
    """View returning the archive for the current day"""
    template_name_suffix = '_archive_today'

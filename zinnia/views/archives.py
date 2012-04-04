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
from zinnia.settings import PAGINATION
from zinnia.settings import ALLOW_EMPTY
from zinnia.settings import ALLOW_FUTURE
from zinnia.views.mixins import CallableQuerysetMixin


class ArchiveMixin(CallableQuerysetMixin):
    """Base configuration for the archives"""
    queryset = Entry.published.all
    paginate_by = PAGINATION
    allow_empty = ALLOW_EMPTY
    allow_future = ALLOW_FUTURE
    date_field = 'creation_date'
    month_format = '%m'


class EntryIndex(ArchiveMixin, ArchiveIndexView):
    """View returning the archive index"""


class EntryYear(ArchiveMixin, YearArchiveView):
    """View returning the archive for a year"""
    make_object_list = True


class EntryMonth(ArchiveMixin, MonthArchiveView):
    """View returning the archive for a month"""


class EntryWeek(ArchiveMixin, WeekArchiveView):
    """View returning the archive for a week"""


class EntryDay(ArchiveMixin, DayArchiveView):
    """View returning the archive for a day"""


class EntryToday(ArchiveMixin, TodayArchiveView):
    """View returning the archive for the current day"""
    template_name_suffix = '_archive_today'

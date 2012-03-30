"""Views for Zinnia archives

TODO:
      1. Implement pagination
      2. Implement custom template name for the date
      3. Better archive_week view
         - Offset -1 from the week URL
         - Use European convention
         - End date in context
         - Review template
"""

from zinnia.models import Entry


# Update
from django.views.generic import ListView
from django.views.generic.dates import YearArchiveView, WeekArchiveView, MonthArchiveView, DayArchiveView, TodayArchiveView

from zinnia.settings import PAGINATION, ALLOW_EMPTY, ALLOW_FUTURE

class ArchiveMixin(object):
  queryset = Entry.published.all()
  context_object_name = 'queryset'


class EntryIndex(ArchiveMixin,ListView):
  paginate_by = PAGINATION
  template_name = 'zinnia/entry_archive.html'


class ArchiveDateMixin(ArchiveMixin):
  date_field = 'creation_date'
  allow_empty = ALLOW_EMPTY
  allow_future = ALLOW_FUTURE

class EntryYear(ArchiveDateMixin,YearArchiveView):
  make_object_list = True

class EntryWeek(ArchiveDateMixin,WeekArchiveView):
  pass

class EntryMonth(ArchiveDateMixin,MonthArchiveView):
  month_format = '%m'

class EntryDay(ArchiveDateMixin,DayArchiveView):
  month_format = '%m'

class EntryToday(ArchiveDateMixin,TodayArchiveView):
  month_format = '%m'



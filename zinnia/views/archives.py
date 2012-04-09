"""Views for Zinnia archives

TODO: 1. Implement custom template name for the date
      2. Review context for each views
      3. Breadrumbs for week archives
"""
from datetime import timedelta

from django.views.generic.dates import ArchiveIndexView
from django.views.generic.dates import YearArchiveView
from django.views.generic.dates import MonthArchiveView
from django.views.generic.dates import WeekArchiveView
from django.views.generic.dates import DayArchiveView
from django.views.generic.dates import TodayArchiveView

from zinnia.models import Entry
from zinnia.views.mixins import ArchiveMixin
from zinnia.views.mixins import CallableQuerysetMixin
from zinnia.views.mixins import PreviousNextPublishedMixin


class ArchiveCallableQuerysetMixin(ArchiveMixin,
                                   PreviousNextPublishedMixin,
                                   CallableQuerysetMixin):
    """Mixin combinating the ArchiveMixin configuration,
    and a callable queryset to force her update + some customizations
    for retrieving next/previous day/month"""
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

    def get_dated_items(self):
        """Override get_dated_items to add a useful 'week_end_day'
        variable in the extra context of the view"""
        self.date_list, self.object_list, extra_context = super(
            EntryWeek, self).get_dated_items()
        extra_context['week_end_day'] = extra_context[
            'week'] + timedelta(days=6)
        return self.date_list, self.object_list, extra_context


class EntryDay(ArchiveCallableQuerysetMixin, DayArchiveView):
    """View returning the archive for a day"""
    # TODO link to current month


class EntryToday(ArchiveCallableQuerysetMixin, TodayArchiveView):
    """View returning the archive for the current day"""
    template_name_suffix = '_archive_today'
    # The same that EntryDay

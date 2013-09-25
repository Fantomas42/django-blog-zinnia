"""Mixins for Zinnia archive views"""
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone

from zinnia.settings import PAGINATION
from zinnia.settings import ALLOW_EMPTY
from zinnia.settings import ALLOW_FUTURE


class ArchiveMixin(object):
    """Mixin centralizing the configuration
    of the archives views"""
    paginate_by = PAGINATION
    allow_empty = ALLOW_EMPTY
    allow_future = ALLOW_FUTURE
    date_field = 'creation_date'
    month_format = '%m'
    week_format = '%W'


class PreviousNextPublishedMixin(object):
    """Mixin for correcting the previous/next
    context variable to return dates with published datas"""

    def get_previous_next_published(self, date, period, previous=True):
        """Return the next or previous published date period with Entries"""
        if settings.USE_TZ:
            date = timezone.make_aware(date, timezone.utc)

        if period == "year":
            #No thinking required here...
            next_date = date.replace(year=date.year + 1)
        elif period == "month":
            #We've got to do the date math ourselves because we don't
            #know how many days to add and timedelta doesn't have a months
            #parameter
            if date.month < 12:
                new_month = date.month + 1
                new_year = date.year
            else:
                new_month = 1
                new_year = date.year + 1
            next_date = date.replace(month=new_month, year=new_year)
        elif period == "day":
            #datetime is smart enough to do the math for us here
            next_date = date + timedelta(days=1)
        if previous:
            filters = {'creation_date__lte': next_date}
            ordering = 'DESC'
        else:
            filters = {'creation_date__gte': next_date}
            ordering = 'ASC'

        items = self.get_queryset().filter(
            **filters)
        #In 1.6, datetimes is added, which is the only way to get
        #datetimes (Which creation_date is) instead of date objects
        #We ought to handle datetimes in utc instead of the local timezone
        if hasattr(items, 'datetimes'):
            dates = items.datetimes('creation_date', period, order=ordering,
                                    tzinfo=timezone.utc)
        else:
            dates = items.dates('creation_date', period, order=ordering,
                                tzinfo=timezone.utc)
        dates = list(dates)
        if date in dates:
            dates.remove(date)

        if dates:
            return dates[0].date()

    def get_next_year(self, date):
        """Get the next year with published Entries"""
        return self.get_previous_next_published(
            datetime(date.year, 1, 1), 'year',
            previous=False)

    def get_previous_year(self, date):
        """Get the previous year with published Entries"""
        return self.get_previous_next_published(
            datetime(date.year, 1, 1), 'year',
            previous=True)

    def get_next_month(self, date):
        """Get the next month with published Entries"""
        return self.get_previous_next_published(
            datetime(date.year, date.month, 1), 'month',
            previous=False)

    def get_previous_month(self, date):
        """Get the previous month with published Entries"""
        return self.get_previous_next_published(
            datetime(date.year, date.month, 1), 'month',
            previous=True)

    def get_next_day(self, date):
        """Get the next day with published Entries"""
        return self.get_previous_next_published(
            datetime(date.year, date.month, date.day),
            'day', previous=False)

    def get_previous_day(self, date):
        """Get the previous day with published Entries"""
        return self.get_previous_next_published(
            datetime(date.year, date.month, date.day),
            'day', previous=True)

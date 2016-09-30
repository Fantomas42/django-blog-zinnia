"""Mixins for Zinnia archive views"""
from datetime import datetime
from datetime import timedelta

from zinnia.settings import ALLOW_EMPTY
from zinnia.settings import ALLOW_FUTURE
from zinnia.settings import PAGINATION


class ArchiveMixin(object):
    """
    Mixin centralizing the configuration of the archives views.
    """
    paginate_by = PAGINATION
    allow_empty = ALLOW_EMPTY
    allow_future = ALLOW_FUTURE
    date_field = 'publication_date'
    month_format = '%m'
    week_format = '%W'


class PreviousNextPublishedMixin(object):
    """
    Mixin for correcting the previous/next
    context variable to return dates with published datas.
    """

    def get_previous_next_published(self, date):
        """
        Returns a dict of the next and previous date periods
        with published entries.
        """
        previous_next = getattr(self, 'previous_next', None)

        if previous_next is None:
            date_year = datetime(date.year, 1, 1)
            date_month = datetime(date.year, date.month, 1)
            date_day = datetime(date.year, date.month, date.day)
            date_next_week = date_day + timedelta(weeks=1)
            previous_next = {'year': [None, None],
                             'week': [None, None],
                             'month': [None, None],
                             'day':  [None, None]}
            dates = self.get_queryset().datetimes(
                'publication_date', 'day', order='ASC')
            for d in dates:
                d_year = datetime(d.year, 1, 1)
                d_month = datetime(d.year, d.month, 1)
                d_day = datetime(d.year, d.month, d.day)
                if d_year < date_year:
                    previous_next['year'][0] = d_year.date()
                elif d_year > date_year and not previous_next['year'][1]:
                    previous_next['year'][1] = d_year.date()
                if d_month < date_month:
                    previous_next['month'][0] = d_month.date()
                elif d_month > date_month and not previous_next['month'][1]:
                    previous_next['month'][1] = d_month.date()
                if d_day < date_day:
                    previous_next['day'][0] = d_day.date()
                    previous_next['week'][0] = d_day.date() - timedelta(
                        days=d_day.weekday())
                elif d_day > date_day and not previous_next['day'][1]:
                    previous_next['day'][1] = d_day.date()
                if d_day > date_next_week and not previous_next['week'][1]:
                    previous_next['week'][1] = d_day.date() - timedelta(
                        days=d_day.weekday())

            setattr(self, 'previous_next', previous_next)
        return previous_next

    def get_next_year(self, date):
        """
        Get the next year with published entries.
        """
        return self.get_previous_next_published(date)['year'][1]

    def get_previous_year(self, date):
        """
        Get the previous year with published entries.
        """
        return self.get_previous_next_published(date)['year'][0]

    def get_next_week(self, date):
        """
        Get the next week with published entries.
        """
        return self.get_previous_next_published(date)['week'][1]

    def get_previous_week(self, date):
        """
        Get the previous wek with published entries.
        """
        return self.get_previous_next_published(date)['week'][0]

    def get_next_month(self, date):
        """
        Get the next month with published entries.
        """
        return self.get_previous_next_published(date)['month'][1]

    def get_previous_month(self, date):
        """
        Get the previous month with published entries.
        """
        return self.get_previous_next_published(date)['month'][0]

    def get_next_day(self, date):
        """
        Get the next day with published entries.
        """
        return self.get_previous_next_published(date)['day'][1]

    def get_previous_day(self, date):
        """
        Get the previous day with published entries.
        """
        return self.get_previous_next_published(date)['day'][0]

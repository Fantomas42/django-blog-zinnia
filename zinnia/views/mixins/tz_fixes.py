"""
Mixins for fixing the time zones support in the
class based generic views for archives.

This module must be removed in Django 1.5.

https://code.djangoproject.com/ticket/18217
"""
import datetime

from django.conf import settings
from django.utils import timezone
from django.views.generic.dates import _date_from_string
from django.views.generic.detail import BaseDetailView


def _make_date_lookup(value):
    value = datetime.datetime.combine(value, datetime.time.min)
    if settings.USE_TZ:
        value = timezone.make_aware(value, timezone.get_current_timezone())
    return value


def _date_lookup_for_field(value):
    """Here the main node of the problem"""
    since = _make_date_lookup(value)
    until = _make_date_lookup(value + datetime.timedelta(days=1))
    return {
        'creation_date__gte': since,
        'creation_date__lt': until}


class EntryMonthTZFix(object):

    def get_dated_items(self):
        """
        Return (date_list, items, extra_context) for this request.
        """
        year = self.get_year()
        month = self.get_month()
        date = _date_from_string(year, self.get_year_format(),
                                 month, self.get_month_format())

        since = _make_date_lookup(date)
        if date.month == 12:
            until = _make_date_lookup(
                datetime.date(date.year + 1, 1, 1))
        else:
            until = _make_date_lookup(
                datetime.date(date.year, date.month + 1, 1))
        lookup_kwargs = {
            'creation_date__gte': since,
            'creation_date__lt': until}

        qs = self.get_dated_queryset(**lookup_kwargs)
        date_list = self.get_date_list(qs, 'day')

        return (date_list, qs, {
            'month': date,
            'next_month': self.get_next_month(date),
            'previous_month': self.get_previous_month(date)})


class EntryWeekTZFix(object):

    def get_dated_items(self):
        """
        Return (date_list, items, extra_context) for this request.
        """
        year = self.get_year()
        week = self.get_week()
        week_format = self.get_week_format()
        week_start = {'%W': '1', '%U': '0'}[week_format]
        date = _date_from_string(year, self.get_year_format(),
                                 week_start, '%w',
                                 week, week_format)
        since = _make_date_lookup(date)
        until = _make_date_lookup(date + datetime.timedelta(days=7))
        lookup_kwargs = {
            'creation_date__gte': since,
            'creation_date__lt': until}

        qs = self.get_dated_queryset(**lookup_kwargs)

        return (None, qs, {'week': date})


class EntryDayTZFix(object):

    def _get_dated_items(self, date):
        """
        Do the actual heavy lifting of getting the dated items; this accepts a
        date object so that TodayArchiveView can be trivial.
        """
        lookup_kwargs = _date_lookup_for_field(date)
        qs = self.get_dated_queryset(**lookup_kwargs)

        return (None, qs, {
            'day': date,
            'previous_day': self.get_previous_day(date),
            'next_day': self.get_next_day(date),
            'previous_month': self.get_previous_month(date),
            'next_month': self.get_next_month(date)})


class EntryDateDetailTZFix(object):

    def get_object(self, queryset=None):
        """
        Get the object this request displays.
        """
        year = self.get_year()
        month = self.get_month()
        day = self.get_day()
        date = _date_from_string(year, self.get_year_format(),
                                 month, self.get_month_format(),
                                 day, self.get_day_format())
        qs = queryset or self.get_queryset()
        lookup = _date_lookup_for_field(date)
        qs = qs.filter(**lookup)
        return super(BaseDetailView, self).get_object(queryset=qs)

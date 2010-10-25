"""Calendar module for Zinnia templatetags"""
from datetime import date
from calendar import HTMLCalendar

from django.utils.dates import MONTHS
from django.utils.dates import WEEKDAYS_ABBR
from django.core.urlresolvers import reverse

from zinnia.models import Entry


class ZinniaCalendar(HTMLCalendar):
    """Override of HTMLCalendar"""

    def formatday(self, day, weekday):
        """Return a day as a table cell with a link
        if entries are published this day"""
        if day and day in self.day_entries:
            day_date = date(self.current_year, self.current_month, day)
            archive_day_url = reverse('zinnia_entry_archive_day',
                                      args=[day_date.strftime('%Y'),
                                            day_date.strftime('%m'),
                                            day_date.strftime('%d')])
            return '<td class="%s entry"><a href="%s" '\
                   'rel="archives">%d</a></td>' % (
                self.cssclasses[weekday], archive_day_url, day)

        return super(ZinniaCalendar, self).formatday(day, weekday)

    def formatmonth(self, theyear, themonth, withyear=True):
        """Return a formatted month as a table with
        new attributes computed for formatting a day"""
        self.current_year = theyear
        self.current_month = themonth
        self.day_entries = [entries.creation_date.day for entries in
                            Entry.published.filter(
                                creation_date__year=theyear,
                                creation_date__month=themonth)]

        return super(ZinniaCalendar, self).formatmonth(
            theyear, themonth, withyear)

    def formatweekday(self, day):
        """Return a weekday name translated
        as a table header."""
        return '<th class="%s">%s</th>' % (self.cssclasses[day],
                                           WEEKDAYS_ABBR[day].title())

    def formatmonthname(self, theyear, themonth, withyear=True):
        """Return a month name translated
        as a table row."""
        if withyear:
            monthname = '%s %s' % (MONTHS[themonth].title(), theyear)
        else:
            monthname = '%s' % MONTHS[themonth].title()
        return '<tr><th colspan="7" class="month">%s</th></tr>' % monthname

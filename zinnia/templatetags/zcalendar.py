"""Calendar module for Zinnia templatetags"""
from datetime import date
from calendar import HTMLCalendar

from django.utils.dates import MONTHS
from django.utils.dates import WEEKDAYS_ABBR
from django.utils.formats import get_format
from django.utils.formats import date_format
from django.core.urlresolvers import reverse

from zinnia.models.entry import Entry

AMERICAN_TO_EUROPEAN_WEEK_DAYS = [6, 0, 1, 2, 3, 4, 5]


class ZinniaCalendar(HTMLCalendar):
    """Override of HTMLCalendar"""

    def __init__(self):
        """Retrieve and convert the localized first week day
        at initialization"""
        HTMLCalendar.__init__(self, AMERICAN_TO_EUROPEAN_WEEK_DAYS[
            get_format('FIRST_DAY_OF_WEEK')])

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
                   'class="archives">%d</a></td>' % (
                       self.cssclasses[weekday], archive_day_url, day)

        return super(ZinniaCalendar, self).formatday(day, weekday)

    def formatweekday(self, day):
        """Return a weekday name translated
        as a table header."""
        return '<th class="%s">%s</th>' % (self.cssclasses[day],
                                           WEEKDAYS_ABBR[day].title())

    def formatweekheader(self):
        """Return a header for a week as a table row."""
        return '<thead>%s</thead>' % super(
            ZinniaCalendar, self).formatweekheader()

    def formatfooter(self, previous_month, next_month):
        """Return a footer for a previous and next month."""
        footer = '<tfoot><tr>' \
                 '<td colspan="3" class="prev">%s</td>' \
                 '<td class="pad">&nbsp;</td>' \
                 '<td colspan="3" class="next">%s</td>' \
                 '</tr></tfoot>'
        if previous_month:
            previous_content = '<a href="%s" class="previous-month">%s</a>' % (
                reverse('zinnia_entry_archive_month', args=[
                    previous_month.strftime('%Y'),
                    previous_month.strftime('%m')]),
                date_format(previous_month, 'YEAR_MONTH_FORMAT'))
        else:
            previous_content = '&nbsp;'

        if next_month:
            next_content = '<a href="%s" class="next-month">%s</a>' % (
                reverse('zinnia_entry_archive_month', args=[
                    next_month.strftime('%Y'),
                    next_month.strftime('%m')]),
                date_format(next_month, 'YEAR_MONTH_FORMAT'))
        else:
            next_content = '&nbsp;'

        return footer % (previous_content, next_content)

    def formatmonthname(self, theyear, themonth, withyear=True):
        """Return a month name translated as a table row."""
        monthname = '%s %s' % (MONTHS[themonth].title(), theyear)
        return '<caption>%s</caption>' % monthname

    def formatmonth(self, theyear, themonth, withyear=True,
                    previous_month=None, next_month=None):
        """Return a formatted month as a table with
        new attributes computed for formatting a day, and thead/tfooter"""
        self.current_year = theyear
        self.current_month = themonth
        self.day_entries = [entries.creation_date.day for entries in
                            Entry.published.filter(
                                creation_date__year=theyear,
                                creation_date__month=themonth)]

        v = []
        a = v.append
        a('<table class="calendar">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        a(self.formatfooter(previous_month, next_month))
        a('\n<tbody>\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week))
            a('\n')
        a('</tbody>\n</table>')
        a('\n')
        return ''.join(v)

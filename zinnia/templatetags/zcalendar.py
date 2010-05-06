"""Calendar module for Zinnia templatetags"""
from datetime import date
from calendar import LocaleHTMLCalendar

from django.core.urlresolvers import reverse

from zinnia.models import Entry

class ZinniaCalendar(LocaleHTMLCalendar):
    """Override of LocaleHTMLCalendar"""

    def formatday(self, day, weekday):
        if day and day in self.day_entries:
            day_date = date(self.current_year, self.current_month, day)
            archive_day_url = reverse('zinnia_entry_archive_day',
                                      args=[day_date.strftime('%Y'),
                                            day_date.strftime('%m'),
                                            day_date.strftime('%d')])
            return '<td class="%s entry"><a href="%s">%d</a></td>' % (
                self.cssclasses[weekday], archive_day_url, day)
        
        return super(ZinniaCalendar, self).formatday(day, weekday)

    def formatmonth(self, theyear, themonth, withyear=True):
        self.current_year = theyear
        self.current_month = themonth
        self.day_entries = [entries.creation_date.day for entries in
                            Entry.published.filter(creation_date__year=theyear,
                                                   creation_date__month=themonth)]

        return super(ZinniaCalendar, self).formatmonth(theyear, themonth, withyear)



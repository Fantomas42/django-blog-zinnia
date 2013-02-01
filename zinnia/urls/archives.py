"""Urls for the Zinnia archives"""
from django.conf.urls import url
from django.conf.urls import patterns

from zinnia.urls import _
from zinnia.views.archives import EntryDay
from zinnia.views.archives import EntryWeek
from zinnia.views.archives import EntryYear
from zinnia.views.archives import EntryMonth
from zinnia.views.archives import EntryToday
from zinnia.views.archives import EntryIndex


index_patterns = [
    url(r'^$',
        EntryIndex.as_view(),
        name='zinnia_entry_archive_index'),
    url(_(r'^page/(?P<page>\d+)/$'),
        EntryIndex.as_view(),
        name='zinnia_entry_archive_index_paginated')
]

year_patterns = [
    url(r'^(?P<year>\d{4})/$',
        EntryYear.as_view(),
        name='zinnia_entry_archive_year'),
    url(_(r'^(?P<year>\d{4})/page/(?P<page>\d+)/$'),
        EntryYear.as_view(),
        name='zinnia_entry_archive_year_paginated'),
]

week_patterns = [
    url(_(r'^(?P<year>\d{4})/week/(?P<week>\d{2})/$'),
        EntryWeek.as_view(),
        name='zinnia_entry_archive_week'),
    url(_(r'^(?P<year>\d{4})/week/(?P<week>\d{2})/page/(?P<page>\d+)/$'),
        EntryWeek.as_view(),
        name='zinnia_entry_archive_week_paginated'),
]

month_patterns = [
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$',
        EntryMonth.as_view(),
        name='zinnia_entry_archive_month'),
    url(_(r'^(?P<year>\d{4})/(?P<month>\d{2})/page/(?P<page>\d+)/$'),
        EntryMonth.as_view(),
        name='zinnia_entry_archive_month_paginated'),
]

day_patterns = [
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
        EntryDay.as_view(),
        name='zinnia_entry_archive_day'),
    url(_(r'^(?P<year>\d{4})/(?P<month>\d{2})/'
          '(?P<day>\d{2})/page/(?P<page>\d+)/$'),
        EntryDay.as_view(),
        name='zinnia_entry_archive_day_paginated'),
]

today_patterns = [
    url(_(r'^today/$'),
        EntryToday.as_view(),
        name='zinnia_entry_archive_today'),
    url(_(r'^today/page/(?P<page>\d+)/$'),
        EntryToday.as_view(),
        name='zinnia_entry_archive_today_paginated'),
]

archive_patterns = (index_patterns + year_patterns +
                    week_patterns + month_patterns +
                    day_patterns + today_patterns)

urlpatterns = patterns(
    '', *archive_patterns
)

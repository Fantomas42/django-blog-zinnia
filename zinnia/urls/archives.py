"""Urls for the Zinnia archives"""
from django.urls import re_path

from zinnia.urls import _
from zinnia.views.archives import EntryDay
from zinnia.views.archives import EntryIndex
from zinnia.views.archives import EntryMonth
from zinnia.views.archives import EntryToday
from zinnia.views.archives import EntryWeek
from zinnia.views.archives import EntryYear


index_patterns = [
    re_path(r'^$',
        EntryIndex.as_view(),
        name='entry_archive_index'),
    re_path(_(r'^page/(?P<page>\d+)/$'),
        EntryIndex.as_view(),
        name='entry_archive_index_paginated')
]

year_patterns = [
    re_path(r'^(?P<year>\d{4})/$',
        EntryYear.as_view(),
        name='entry_archive_year'),
    re_path(_(r'^(?P<year>\d{4})/page/(?P<page>\d+)/$'),
        EntryYear.as_view(),
        name='entry_archive_year_paginated'),
]

week_patterns = [
    re_path(_(r'^(?P<year>\d{4})/week/(?P<week>\d+)/$'),
        EntryWeek.as_view(),
        name='entry_archive_week'),
    re_path(_(r'^(?P<year>\d{4})/week/(?P<week>\d+)/page/(?P<page>\d+)/$'),
        EntryWeek.as_view(),
        name='entry_archive_week_paginated'),
]

month_patterns = [
    re_path(r'^(?P<year>\d{4})/(?P<month>\d{2})/$',
        EntryMonth.as_view(),
        name='entry_archive_month'),
    re_path(_(r'^(?P<year>\d{4})/(?P<month>\d{2})/page/(?P<page>\d+)/$'),
        EntryMonth.as_view(),
        name='entry_archive_month_paginated'),
]

day_patterns = [
    re_path(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
        EntryDay.as_view(),
        name='entry_archive_day'),
    re_path(_(r'^(?P<year>\d{4})/(?P<month>\d{2})/'
          r'(?P<day>\d{2})/page/(?P<page>\d+)/$'),
        EntryDay.as_view(),
        name='entry_archive_day_paginated'),
]

today_patterns = [
    re_path(_(r'^today/$'),
        EntryToday.as_view(),
        name='entry_archive_today'),
    re_path(_(r'^today/page/(?P<page>\d+)/$'),
        EntryToday.as_view(),
        name='entry_archive_today_paginated'),
]

archive_patterns = (index_patterns + year_patterns +
                    week_patterns + month_patterns +
                    day_patterns + today_patterns)

urlpatterns = archive_patterns

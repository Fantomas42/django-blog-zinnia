"""Urls for the Zinnia archives"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from zinnia.views.archives import EntryIndex, EntryYear, EntryWeek, EntryMonth, EntryDay, EntryToday
urlpatterns = patterns('',
    url(r'^$', EntryIndex.as_view(),name='zinnia_entry_archive_index'),
    url(r'^page/(?P<page>\d+)/$',EntryIndex.as_view(),name='zinnia_entry_archive_index_paginated'),
    url(r'^(?P<year>\d{4})/$',EntryYear.as_view(),name='zinnia_entry_archive_year'),
    url(r'^(?P<year>\d{4})/week/(?P<week>\d{2})/$',EntryWeek.as_view(),name='zinnia_entry_archive_week'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$',EntryMonth.as_view(),name='zinnia_entry_archive_month'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',EntryDay.as_view(),name='zinnia_entry_archive_day'),
    url(r'^today/$',EntryToday.as_view(),name='zinnia_entry_archive_today'),
)
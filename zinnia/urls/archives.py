"""Urls for the Zinnia archives"""
from django.conf.urls import url
from django.conf.urls import patterns

from zinnia.settings import ALLOW_EMPTY
from zinnia.settings import ALLOW_FUTURE
from zinnia.views.archives import EntryIndex

entry_conf = {'date_field': 'creation_date',
              'allow_empty': ALLOW_EMPTY,
              'allow_future': ALLOW_FUTURE,
              'month_format': '%m'}

entry_conf_year = entry_conf.copy()
del entry_conf_year['month_format']
entry_conf_week = entry_conf_year.copy()
entry_conf_year['make_object_list'] = True


urlpatterns = patterns(
    'zinnia.views.archives',
    url(r'^$',
        EntryIndex.as_view(),
        name='zinnia_entry_archive_index'),
    url(r'^page/(?P<page>\d+)/$',
        EntryIndex.as_view(),
        name='zinnia_entry_archive_index_paginated'),
    url(r'^(?P<year>\d{4})/$',
        'entry_year', entry_conf_year,
        name='zinnia_entry_archive_year'),
    url(r'^(?P<year>\d{4})/week/(?P<week>\d{2})/$',
        'entry_week', entry_conf_week,
        name='zinnia_entry_archive_week'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$',
        'entry_month', entry_conf,
        name='zinnia_entry_archive_month'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
        'entry_day', entry_conf,
        name='zinnia_entry_archive_day'),
    url(r'^today/$',
        'entry_today', entry_conf,
        name='zinnia_entry_archive_today'),
    )

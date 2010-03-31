"""Urls for the zinnia entries"""
from django.conf.urls.defaults import *

from zinnia.models import Entry
from zinnia.settings import PAGINATION
from zinnia.settings import MONTH_FORMAT

entry_conf_list = {'queryset': Entry.published.all(),
                   'paginate_by': PAGINATION,}

entry_conf = {'queryset': Entry.published.all(),
              'date_field': 'creation_date',}

entry_conf_year = entry_conf.copy()
entry_conf_year['make_object_list'] = True

entry_conf_detail = entry_conf.copy()
entry_conf_detail['queryset'] = Entry.objects.all()

urlpatterns = patterns('django.views.generic.list_detail',
                       url(r'^$', 'object_list', entry_conf_list,
                           name='zinnia_entry_archive_index'),
                       url(r'^page/(?P<page>\d+)/$', 'object_list', entry_conf_list,
                           name='zinnia_entry_archive_index_paginated'),
                       )

urlpatterns += patterns('django.views.generic.date_based',
                        url(r'^(?P<year>\d{4})/$', 'archive_year',
                            entry_conf_year, name='zinnia_entry_archive_year'),
                        url(r'^(?P<year>\d{4})/(?P<month>\w+)/$', 'archive_month',
                            entry_conf, name='zinnia_entry_archive_month'),
                        url(r'^(?P<year>\d{4})/(?P<month>\w+)/(?P<day>\d{2})/$', 'archive_day',
                            entry_conf, name='zinnia_entry_archive_day'),
                        url(r'^(?P<year>\d{4})/(?P<month>\w+)/(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
                            'object_detail', entry_conf_detail, name='zinnia_entry_detail'),
                        )

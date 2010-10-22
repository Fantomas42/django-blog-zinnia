"""Urls for the zinnia tags"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from zinnia.models import Entry
from zinnia.settings import PAGINATION
from zinnia.managers import tags_published

tag_conf = {'queryset': tags_published(),
            'template_name': 'zinnia/tag_list.html'}

tag_conf_entry = {'queryset_or_model': Entry.published.all(),
                  'paginate_by': PAGINATION}

urlpatterns = patterns('zinnia.views.tags',
                       url(r'^$', 'tag_list',
                           tag_conf, name='zinnia_tag_list'),
                       url(r'^(?P<tag>[- \w]+)/$', 'tag_detail',
                           tag_conf_entry, name='zinnia_tag_detail'),
                       url(r'^(?P<tag>[- \w]+)/page/(?P<page>\d+)/$',
                           'tag_detail', tag_conf_entry,
                           name='zinnia_tag_detail_paginated'),
                       )

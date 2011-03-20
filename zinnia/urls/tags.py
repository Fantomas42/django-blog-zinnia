"""Urls for the Zinnia tags"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from zinnia.managers import tags_published

tag_conf = {'queryset': tags_published(),
            'template_name': 'zinnia/tag_list.html'}

urlpatterns = patterns('zinnia.views.tags',
                       url(r'^$', 'tag_list',
                           tag_conf, name='zinnia_tag_list'),
                       url(r'^(?P<tag>[- \w]+)/$', 'tag_detail',
                           name='zinnia_tag_detail'),
                       url(r'^(?P<tag>[- \w]+)/page/(?P<page>\d+)/$',
                           'tag_detail', name='zinnia_tag_detail_paginated'),
                       )

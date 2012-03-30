"""Urls for the Zinnia tags"""
from django.conf.urls import url
from django.conf.urls import patterns

urlpatterns = patterns('zinnia.views.tags',
                       url(r'^$', 'tag_list',
                           name='zinnia_tag_list'),
                       url(r'^(?P<tag>[^/]+(?u))/$', 'tag_detail',
                           name='zinnia_tag_detail'),
                       url(r'^(?P<tag>[^/]+(?u))/page/(?P<page>\d+)/$',
                           'tag_detail', name='zinnia_tag_detail_paginated'),
                       )

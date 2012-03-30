"""Urls for the Zinnia authors"""
from django.conf.urls import url
from django.conf.urls import patterns


urlpatterns = patterns('zinnia.views.authors',
                       url(r'^$', 'author_list',
                           name='zinnia_author_list'),
                       url(r'^(?P<username>[.+-@\w]+)/$', 'author_detail',
                           name='zinnia_author_detail'),
                       url(r'^(?P<username>[.+-@\w]+)/page/(?P<page>\d+)/$',
                           'author_detail',
                           name='zinnia_author_detail_paginated'),
                       )

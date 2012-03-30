"""Urls for the Zinnia authors"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from zinnia.views.authors import AuthorList, AuthorDetail

urlpatterns = patterns('',
    url(r'^$', AuthorList.as_view(), name='zinnia_author_list'),
    url(r'^(?P<username>[.+-@\w]+)/$', AuthorDetail.as_view(), name='zinnia_author_detail'),
    url(r'^(?P<username>[.+-@\w]+)/page/(?P<page>\d+)/$', AuthorDetail.as_view(), name='zinnia_author_detail_paginated'),
)
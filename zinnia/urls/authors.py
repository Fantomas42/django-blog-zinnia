"""Urls for the Zinnia authors"""
from django.conf.urls import url
from django.conf.urls import patterns

from zinnia.urls import _
from zinnia.views.authors import AuthorList
from zinnia.views.authors import AuthorDetail


urlpatterns = patterns(
    '',
    url(r'^$',
        AuthorList.as_view(),
        name='zinnia_author_list'),
    url(_(r'^(?P<username>[.+-@\w]+)/page/(?P<page>\d+)/$'),
        AuthorDetail.as_view(),
        name='zinnia_author_detail_paginated'),
    url(r'^(?P<username>[.+-@\w]+)/$',
        AuthorDetail.as_view(),
        name='zinnia_author_detail'),
)

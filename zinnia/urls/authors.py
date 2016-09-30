"""Urls for the Zinnia authors"""
from django.conf.urls import url

from zinnia.urls import _
from zinnia.views.authors import AuthorDetail
from zinnia.views.authors import AuthorList


urlpatterns = [
    url(r'^$',
        AuthorList.as_view(),
        name='author_list'),
    url(_(r'^(?P<username>[.+-@\w]+)/page/(?P<page>\d+)/$'),
        AuthorDetail.as_view(),
        name='author_detail_paginated'),
    url(r'^(?P<username>[.+-@\w]+)/$',
        AuthorDetail.as_view(),
        name='author_detail'),
]

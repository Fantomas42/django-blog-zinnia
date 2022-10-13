"""Urls for the Zinnia authors"""
from django.urls import path, re_path

from zinnia.urls import _
from zinnia.views.authors import AuthorDetail
from zinnia.views.authors import AuthorList


urlpatterns = [
    path('',
        AuthorList.as_view(),
        name='author_list'),
    re_path(_(r'^(?P<username>[.+-@\w]+)/page/(?P<page>\d+)/$'),
        AuthorDetail.as_view(),
        name='author_detail_paginated'),
    re_path(r'^(?P<username>[.+-@\w]+)/$',
        AuthorDetail.as_view(),
        name='author_detail'),
]

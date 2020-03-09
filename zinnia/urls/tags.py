"""Urls for the Zinnia tags"""
from django.conf.urls import url

from zinnia.urls import _
from zinnia.views.tags import TagDetail
from zinnia.views.tags import TagList


urlpatterns = [
    url(r'^$',
        TagList.as_view(),
        name='tag_list'),
    url(r'^(?P<tag>[^/]+)/$',
        TagDetail.as_view(),
        name='tag_detail'),
    url(_(r'^(?P<tag>[^/]+)/page/(?P<page>\d+)/$'),
        TagDetail.as_view(),
        name='tag_detail_paginated'),
]

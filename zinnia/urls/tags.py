"""Urls for the Zinnia tags"""
from django.urls import re_path

from zinnia.urls import _
from zinnia.views.tags import TagDetail
from zinnia.views.tags import TagList

urlpatterns = [
    re_path(r'^$',
            TagList.as_view(),
            name='tag_list'),
    re_path(r'^(?P<tag>[^/]+)/$',
            TagDetail.as_view(),
            name='tag_detail'),
    re_path(_(r'^(?P<tag>[^/]+)/page/(?P<page>\d+)/$'),
            TagDetail.as_view(),
            name='tag_detail_paginated'),
]

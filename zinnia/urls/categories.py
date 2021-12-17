"""Urls for the Zinnia categories"""
from django.urls import re_path

from zinnia.urls import _
from zinnia.views.categories import CategoryDetail
from zinnia.views.categories import CategoryList

urlpatterns = [
    re_path(r'^$',
            CategoryList.as_view(),
            name='category_list'),
    re_path(_(r'^(?P<path>[-\/\w]+)/page/(?P<page>\d+)/$'),
            CategoryDetail.as_view(),
            name='category_detail_paginated'),
    re_path(r'^(?P<path>[-\/\w]+)/$',
            CategoryDetail.as_view(),
            name='category_detail'),
]

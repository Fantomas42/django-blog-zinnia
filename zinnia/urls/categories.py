"""Urls for the Zinnia categories"""
from django.conf.urls import url
from django.conf.urls import patterns

from zinnia.urls import _
from zinnia.views.categories import CategoryList
from zinnia.views.categories import CategoryDetail


urlpatterns = patterns(
    '',
    url(r'^$',
        CategoryList.as_view(),
        name='zinnia_category_list'),
    url(_(r'^(?P<path>[-\/\w]+)/page/(?P<page>\d+)/$'),
        CategoryDetail.as_view(),
        name='zinnia_category_detail_paginated'),
    url(r'^(?P<path>[-\/\w]+)/$',
        CategoryDetail.as_view(),
        name='zinnia_category_detail'),
)

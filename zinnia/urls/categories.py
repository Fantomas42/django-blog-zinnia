"""Urls for the Zinnia categories"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from zinnia.views.categories import CategoryListView, CategoryDetailView


urlpatterns = patterns('',
	url(r'^$', CategoryListView.as_view(), name='zinnia_category_list'),
	url(r'^(?P<path>[-\/\w]+)/page/(?P<page>\d+)/$',CategoryDetailView.as_view(), name='zinnia_category_detail_paginated'),
    url(r'^(?P<path>[-\/\w]+)/$', CategoryDetailView.as_view(), name='zinnia_category_detail'),
)
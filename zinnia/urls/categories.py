"""Urls for the zinnia categories"""
from django.conf.urls.defaults import *

from zinnia.models import Category


category_conf = {'queryset': Category.tree.all(),}

urlpatterns = patterns('',
                       url(r'^$', 'django.views.generic.list_detail.object_list',
                           category_conf, 'zinnia_category_list'),
                       )

urlpatterns += patterns('zinnia.views.categories',
                        url(r'^(?P<path>[-\/\w]+)/$', 'category_detail',
                            name='zinnia_category_detail'),
                        url(r'^(?P<path>[-\/\w]+)/page/(?P<page>\d+)/$',
                            'category_detail',
                            name='zinnia_category_detail_paginated'),
                        )

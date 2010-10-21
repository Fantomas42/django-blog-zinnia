"""Urls for the zinnia authors"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from zinnia.managers import authors_published


author_conf = {'queryset': authors_published(),
               'template_name': 'zinnia/author_list.html',}

urlpatterns = patterns('zinnia.views.authors',
                       url(r'^$', 'author_list',
                           author_conf, 'zinnia_author_list'),
                       url(r'^(?P<username>[.+-@\w]+)/$', 'author_detail',
                           name='zinnia_author_detail'),
                       url(r'^(?P<username>[.+-@\w]+)/page/(?P<page>\d+)/$',
                           'author_detail',
                           name='zinnia_author_detail_paginated'),
                       )


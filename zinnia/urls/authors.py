"""Urls for the zinnia categories"""
from django.conf.urls.defaults import *

from zinnia.managers import authors_published

author_conf = {'queryset': authors_published(),
               'template_name': 'zinnia/author_list.html',}

urlpatterns = patterns('',
                       url(r'^$', 'django.views.generic.list_detail.object_list',
                           author_conf, 'zinnia_author_list'),
                       url(r'^(?P<username>\w+)/$', 'zinnia.views.author_detail',
                           name='zinnia_author_detail'),
                       )

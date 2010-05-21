"""Urls for the zinnia tags"""
from django.conf.urls.defaults import *

from zinnia.models import Entry
from zinnia.managers import tags_published

tag_conf = {'queryset': tags_published(),
            'template_name': 'zinnia/tag_list.html'}

tag_conf_entry = {'queryset_or_model': Entry.published.all(),}

urlpatterns = patterns('',
                       url(r'^$', 'django.views.generic.list_detail.object_list',
                           tag_conf, name='zinnia_tag_list'),
                       url(r'^(?P<tag>[-\w]+)/$', 'tagging.views.tagged_object_list',
                           tag_conf_entry, name='zinnia_tag_detail'),
                       )

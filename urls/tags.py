"""Urls for the zinnia tags"""
from django.conf.urls.defaults import *

from zinnia.models import Entry
from tagging.models import Tag

tag_conf = {'queryset': Tag.objects.all()}

tag_conf_entry = {'queryset_or_model': Entry.published.all()}

urlpatterns = patterns('',
                       url(r'^$', 'django.views.generic.list_detail.object_list',
                           tag_conf, 'zinnia_tag_list'),
                       url(r'^(?P<tag>[-\w]+)/$', 'tagging.views.tagged_object_list',
                           tag_conf_entry, 'zinnia_tagged_entry_list'),
                       )

"""Urls for the Zinnia search"""
from django.conf.urls import url
from django.conf.urls import patterns

urlpatterns = patterns('zinnia.views.search',
                       url(r'^$', 'entry_search', name='zinnia_entry_search'),
                       )

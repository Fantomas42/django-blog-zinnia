"""Urls for the zinnia search"""
from django.conf.urls.defaults import *

urlpatterns = patterns('zinnia.views.search',
                       url(r'^$', 'entry_search', name='zinnia_entry_search'),
                       )

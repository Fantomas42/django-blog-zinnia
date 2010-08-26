"""Urls for the zinnia trackback"""
from django.conf.urls.defaults import *

urlpatterns = patterns('zinnia.views.trackback',
                       url(r'^(?P<slug>[-\w]+)/$', 'entry_trackback',
                           name='zinnia_entry_trackback'),
                       )

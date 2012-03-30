"""Urls for the Zinnia trackback"""
from django.conf.urls import url
from django.conf.urls import patterns

urlpatterns = patterns('zinnia.views.trackback',
                       url(r'^(?P<object_id>\d+)/$', 'entry_trackback',
                           name='zinnia_entry_trackback'),
                       )

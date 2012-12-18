"""Urls for the Zinnia trackback"""
from django.conf.urls import url
from django.conf.urls import patterns

from zinnia.views.trackback import EntryTrackback


urlpatterns = patterns(
    '',
    url(r'^(?P<pk>\d+)/$',
        EntryTrackback.as_view(),
        name='zinnia_entry_trackback'),
)

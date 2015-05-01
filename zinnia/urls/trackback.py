"""Urls for the Zinnia trackback"""
from django.conf.urls import url

from zinnia.views.trackback import EntryTrackback


urlpatterns = [
    url(r'^(?P<pk>\d+)/$',
        EntryTrackback.as_view(),
        name='entry_trackback'),
]

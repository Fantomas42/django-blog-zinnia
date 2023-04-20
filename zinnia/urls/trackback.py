"""Urls for the Zinnia trackback"""
from django.urls import re_path

from zinnia.views.trackback import EntryTrackback


urlpatterns = [
    re_path(r'^(?P<pk>\d+)/$',
        EntryTrackback.as_view(),
        name='entry_trackback'),
]

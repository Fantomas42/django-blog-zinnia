"""Urls for the Zinnia trackback"""
from django.urls import path

from zinnia.views.trackback import EntryTrackback


urlpatterns = [
    path('<int:pk>/',
        EntryTrackback.as_view(),
        name='entry_trackback'),
]

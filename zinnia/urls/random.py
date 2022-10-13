"""Urls for Zinnia random entries"""
from django.urls import path

from zinnia.views.random import EntryRandom


urlpatterns = [
    path('',
        EntryRandom.as_view(),
        name='entry_random'),
]

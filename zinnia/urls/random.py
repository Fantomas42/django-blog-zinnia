"""Urls for Zinnia random entries"""
from django.conf.urls import url
from django.conf.urls import patterns

from zinnia.views.random import EntryRandom


urlpatterns = patterns(
    '',
    url(r'^$',
        EntryRandom.as_view(),
        name='zinnia_entry_random'),
)

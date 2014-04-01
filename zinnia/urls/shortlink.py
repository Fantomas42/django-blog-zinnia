"""Urls for the Zinnia entries short link"""
from django.conf.urls import url
from django.conf.urls import patterns

from zinnia.views.shortlink import EntryShortLink


urlpatterns = patterns(
    '',
    url(r'^e(?P<token>[\da-z]+)/$',
        EntryShortLink.as_view(),
        name='entry_shortlink'),
)

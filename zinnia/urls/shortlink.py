"""Urls for the Zinnia entries short link"""
from django.conf.urls import url
from django.conf.urls import patterns

from zinnia.views.shortlink import EntryShortLink


urlpatterns = patterns(
    '',
    url(r'^(?P<pk>\d+)/$',
        EntryShortLink.as_view(),
        name='zinnia_entry_shortlink'),
)

"""Urls for the Zinnia search"""
from django.conf.urls import url
from django.conf.urls import patterns

from zinnia.views.search import EntrySearch


urlpatterns = patterns(
    '',
    url(r'^$', EntrySearch.as_view(),
        name='zinnia_entry_search'),
)

"""Urls for the Zinnia search"""
from django.conf.urls import url

from zinnia.views.search import EntrySearch


urlpatterns = [
    url(r'^$', EntrySearch.as_view(),
        name='entry_search'),
]

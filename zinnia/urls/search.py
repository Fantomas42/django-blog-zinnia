"""Urls for the Zinnia search"""
from django.urls import re_path

from zinnia.views.search import EntrySearch

urlpatterns = [
    re_path(r'^$', EntrySearch.as_view(),
            name='entry_search'),
]

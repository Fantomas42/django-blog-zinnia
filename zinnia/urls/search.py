"""Urls for the Zinnia search"""
from django.urls import path

from zinnia.views.search import EntrySearch


urlpatterns = [
    path('', EntrySearch.as_view(),
        name='entry_search'),
]

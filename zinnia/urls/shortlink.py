"""Urls for the Zinnia entries short link"""
from django.urls import re_path

from zinnia.views.shortlink import EntryShortLink

urlpatterns = [
    re_path(r'^(?P<token>[\dA-Z]+)/$',
            EntryShortLink.as_view(),
            name='entry_shortlink'),
]

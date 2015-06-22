"""Urls for the Zinnia entries"""
from django.conf.urls import url

from zinnia.views.entries import EntryDetail


urlpatterns = [
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        EntryDetail.as_view(),
        name='entry_detail'),
]

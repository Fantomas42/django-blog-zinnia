"""Url for the Zinnia quick entry view"""
from django.conf.urls import url
from django.conf.urls import patterns

from zinnia.views.quick_entry import QuickEntry


urlpatterns = patterns(
    '',
    url(r'^quick_entry/$',
        QuickEntry.as_view(),
        name='zinnia_entry_quick_post')
)

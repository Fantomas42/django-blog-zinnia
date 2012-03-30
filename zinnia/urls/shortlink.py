"""Urls for the Zinnia entries short link"""
from django.conf.urls import url
from django.conf.urls import patterns


urlpatterns = patterns(
    'zinnia.views.shortlink',
    url(r'^(?P<object_id>\d+)/$',
        'entry_shortlink',
        name='zinnia_entry_shortlink'),
    )

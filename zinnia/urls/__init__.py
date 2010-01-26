"""Defaults urls for the zinnia project"""
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^tags/', include('zinnia.urls.tags')),
    (r'^feeds/', include('zinnia.urls.feeds')),
    (r'^authors/', include('zinnia.urls.authors')),
    (r'^categories/', include('zinnia.urls.categories')),
    (r'^search/', include('zinnia.urls.search')),
    (r'^', include('zinnia.urls.entries')),
)

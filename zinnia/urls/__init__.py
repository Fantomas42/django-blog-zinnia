"""Defaults urls for the Zinnia project"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
                       url(r'^tags/', include('zinnia.urls.tags',)),
                       url(r'^feeds/', include('zinnia.urls.feeds')),
                       url(r'^authors/', include('zinnia.urls.authors')),
                       url(r'^categories/', include('zinnia.urls.categories')),
                       url(r'^search/', include('zinnia.urls.search')),
                       url(r'^sitemap/', include('zinnia.urls.sitemap')),
                       url(r'^trackback/', include('zinnia.urls.trackback')),
                       url(r'^discussions/', include('zinnia.urls.discussions')),
                       url(r'^', include('zinnia.urls.quick_entry')),
                       url(r'^', include('zinnia.urls.capabilities')),
                       url(r'^', include('zinnia.urls.entries')),
                       )

"""Defaults urls for the Zinnia project"""
from django.conf.urls import url
from django.conf.urls import include
from django.conf.urls import patterns

urlpatterns = patterns(
    '',
    url(r'^tags/', include('zinnia.urls.tags',)),
    url(r'^feeds/', include('zinnia.urls.feeds')),
    url(r'^authors/', include('zinnia.urls.authors')),
    url(r'^categories/', include('zinnia.urls.categories')),
    url(r'^search/', include('zinnia.urls.search')),
    url(r'^sitemap/', include('zinnia.urls.sitemap')),
    url(r'^trackback/', include('zinnia.urls.trackback')),
    url(r'^comments/', include('zinnia.urls.comments')),
    url(r'^', include('zinnia.urls.entries')),
    url(r'^', include('zinnia.urls.archives')),
    url(r'^', include('zinnia.urls.shortlink')),
    url(r'^', include('zinnia.urls.quick_entry')),
    url(r'^', include('zinnia.urls.capabilities')),
    )

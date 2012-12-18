"""Urls for the Zinnia sitemap"""
from django.conf.urls import url
from django.conf.urls import patterns

from zinnia.views.sitemap import Sitemap


urlpatterns = patterns(
    '',
    url(r'^$', Sitemap.as_view(),
        name='zinnia_sitemap'),
)

"""Urls for the Zinnia sitemap"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('zinnia.views.sitemap',
                       url(r'^$', 'sitemap',
                           name='zinnia_sitemap'),
                       )

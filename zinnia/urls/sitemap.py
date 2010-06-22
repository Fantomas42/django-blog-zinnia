"""Urls for the zinnia sitemap"""
from django.conf.urls.defaults import *

urlpatterns = patterns('zinnia.views.sitemap',
                       url(r'^$', 'sitemap',
                           {'template': 'zinnia/sitemap.html'},
                           name='zinnia_sitemap'),
                       )



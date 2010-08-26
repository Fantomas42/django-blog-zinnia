"""Urls for the zinnia capabilities"""
from django.conf.urls.defaults import *

from django.contrib.sites.models import Site

SITE = Site.objects.get_current()

urlpatterns = patterns('django.views.generic.simple',
                       url(r'^rsd.xml$', 'direct_to_template',
                           {'template': 'zinnia/rsd.xml',
                            'mimetype': 'text/xml',
                            'extra_context': {'site': SITE}},
                           name='zinnia_rsd'),
                       url(r'^wlwmanifest.xml$', 'direct_to_template',
                           {'template': 'zinnia/wlwmanifest.xml',
                            'mimetype': 'text/xml',
                            'extra_context': {'site': SITE}},
                           name='zinnia_wlwmanifest'),
                       )

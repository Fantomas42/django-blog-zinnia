"""Urls for the zinnia capabilities"""
from django.conf.urls import url
from django.conf.urls import patterns

from zinnia.views.capabilities import RsdXml
from zinnia.views.capabilities import HumansTxt
from zinnia.views.capabilities import OpenSearchXml
from zinnia.views.capabilities import WLWManifestXml


urlpatterns = patterns(
    '',
    url(r'^rsd.xml$', RsdXml.as_view(),
        name='zinnia_rsd'),
    url(r'^humans.txt$', HumansTxt.as_view(),
        name='zinnia_humans'),
    url(r'^opensearch.xml$', OpenSearchXml.as_view(),
        name='zinnia_opensearch'),
    url(r'^wlwmanifest.xml$', WLWManifestXml.as_view(),
        name='zinnia_wlwmanifest')
)

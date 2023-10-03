"""Urls for the zinnia capabilities"""
from django.urls import re_path

from zinnia.views.capabilities import HumansTxt
from zinnia.views.capabilities import OpenSearchXml
from zinnia.views.capabilities import RsdXml
from zinnia.views.capabilities import WLWManifestXml


urlpatterns = [
    re_path(r'^rsd.xml$', RsdXml.as_view(),
        name='rsd'),
    re_path(r'^humans.txt$', HumansTxt.as_view(),
        name='humans'),
    re_path(r'^opensearch.xml$', OpenSearchXml.as_view(),
        name='opensearch'),
    re_path(r'^wlwmanifest.xml$', WLWManifestXml.as_view(),
        name='wlwmanifest'),
]

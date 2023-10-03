"""Urls for the Zinnia sitemap"""
from django.urls import path

from zinnia.views.sitemap import Sitemap


urlpatterns = [
    path('', Sitemap.as_view(),
        name='sitemap'),
]

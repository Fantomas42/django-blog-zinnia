"""Urls for the Zinnia discussions"""
from django.conf.urls import url
from django.conf.urls import patterns

from django.views.generic import TemplateView


urlpatterns = patterns(
    '',
    url(r'^success/$', TemplateView.as_view(
        template_name='comments/zinnia/entry/posted.html'),
        name='zinnia_discussion_success')
    )

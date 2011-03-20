"""Urls for the Zinnia discussions"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('django.views.generic.simple',
                       url(r'^success/$', 'direct_to_template',
                           {'template': 'comments/zinnia/entry/posted.html'},
                           name='zinnia_discussion_success'),
                       )

"""Urls for the zinnia discussions"""
from django.conf.urls.defaults import *

urlpatterns = patterns('',
                       url(r'^success/$', 'django.views.generic.simple.direct_to_template',
                           {'template': 'comments/zinnia/entry/posted.html'},
                           name='zinnia_discussion_success'),
                       )


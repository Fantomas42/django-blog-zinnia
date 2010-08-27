"""Urls for the zinnia sitemap"""
from django.conf.urls.defaults import *

urlpatterns = patterns('',
                       url(r'^success/$', 'django.views.generic.simple.direct_to_template',
                           {'template': 'comments/zinnia/zinnia_comment_success.html'},
                           name='zinnia_discussion_success'),
                       )
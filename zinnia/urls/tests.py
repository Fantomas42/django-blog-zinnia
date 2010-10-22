"""Test urls for the zinnia project"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import handler404
from django.conf.urls.defaults import handler500

from zinnia.urls import urlpatterns

urlpatterns += patterns('',
                        url(r'^channel-test/$', 'zinnia.views.channels.entry_channel',
                            {'query': 'test'}),
                        url(r'^comments/', include('django.contrib.comments.urls')),
                        url(r'^xmlrpc/$', 'django_xmlrpc.views.handle_xmlrpc'),
                        )

"""Test urls for the zinnia project"""
from django.conf.urls.defaults import *
from zinnia.urls import urlpatterns

urlpatterns += patterns('',
                        url(r'^comments/', include('django.contrib.comments.urls')),
                        url(r'^xmlrpc/$', 'django_xmlrpc.views.handle_xmlrpc'),
                        )
                        

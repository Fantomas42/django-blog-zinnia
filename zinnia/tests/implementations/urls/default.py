"""Test urls for the zinnia project"""
from django.conf.urls import include
from django.urls import include, path, re_path
from django.contrib import admin

from django_xmlrpc.views import handle_xmlrpc

from zinnia.views.channels import EntryChannel

admin.autodiscover()

urlpatterns = [
    re_path(r'^', include('zinnia.urls')),
    path('channel-test/', EntryChannel.as_view(query='test')),
    re_path(r'^comments/', include('django_comments.urls')),
    path('xmlrpc/', handle_xmlrpc),
    re_path(r'^admin/', admin.site.urls),
]

"""Test urls for the zinnia project"""
from django.contrib import admin
from django.conf.urls import url
from django.conf.urls import include

from django_xmlrpc.views import handle_xmlrpc
from zinnia.views.channels import EntryChannel

admin.autodiscover()

urlpatterns = [
    url(r'^', include('zinnia.urls')),
    url(r'^channel-test/$', EntryChannel.as_view(query='test')),
    url(r'^comments/', include('django_comments.urls')),
    url(r'^xmlrpc/$', handle_xmlrpc),
    url(r'^admin/', admin.site.urls),
]

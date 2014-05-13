"""Test urls for the zinnia project"""
from django.contrib import admin
from django.conf.urls import url
from django.conf.urls import include
from django.conf.urls import patterns

from zinnia.urls import urlpatterns
from zinnia.views.channels import EntryChannel

admin.autodiscover()

handler500 = 'django.views.defaults.server_error'
handler404 = 'django.views.defaults.page_not_found'

comments_url_pattern = 'django.contrib.comments.urls'
try:
    import django_comments
    comments_url_pattern = 'django_comments.urls'
except ImportError:
    pass

urlpatterns += patterns(
    '',
    url(r'^channel-test/$', EntryChannel.as_view(query='test')),
    url(r'^comments/', include(comments_url_pattern)),
    url(r'^xmlrpc/$', 'django_xmlrpc.views.handle_xmlrpc'),
    url(r'^admin/', include(admin.site.urls)),
)

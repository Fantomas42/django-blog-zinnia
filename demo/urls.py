"""Urls for the demo of Zinnia"""
from functools import partial

from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import index
from django.contrib.sitemaps.views import sitemap
from django.urls import include, re_path
from django.views.defaults import bad_request, page_not_found, permission_denied, server_error
from django.views.generic.base import RedirectView
from django.views.static import serve
from django_xmlrpc.views import handle_xmlrpc

from zinnia.sitemaps import AuthorSitemap
from zinnia.sitemaps import CategorySitemap
from zinnia.sitemaps import EntrySitemap
from zinnia.sitemaps import TagSitemap

urlpatterns = [
    re_path(r'^$', RedirectView.as_view(url='/blog/', permanent=True)),
    re_path(r'^blog/', include('zinnia.urls')),
    re_path(r'^comments/', include('django_comments.urls')),
    re_path(r'^xmlrpc/$', handle_xmlrpc),
    re_path(r'^i18n/', include('django.conf.urls.i18n')),
    re_path(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    re_path(r'^admin/', admin.site.urls),
]

sitemaps = {
    'tags': TagSitemap,
    'blog': EntrySitemap,
    'authors': AuthorSitemap,
    'categories': CategorySitemap
}

urlpatterns += [
    re_path(r'^sitemap.xml$',
            index,
            {'sitemaps': sitemaps}),
    re_path(r'^sitemap-(?P<section>.+)\.xml$',
            sitemap,
            {'sitemaps': sitemaps}),
]

urlpatterns += [
    re_path(r'^400/$', partial(bad_request, exception=None)),
    re_path(r'^403/$', partial(permission_denied, exception=None)),
    re_path(r'^404/$', partial(page_not_found, exception=None)),
    re_path(r'^500/$', server_error),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve,
                {'document_root': settings.MEDIA_ROOT})
    ]

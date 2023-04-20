"""Urls for the demo of Zinnia"""
from functools import partial

from django.conf import settings
from django.conf.urls import include
from django.urls import include, path, re_path
from django.contrib import admin
from django.contrib.sitemaps.views import index
from django.contrib.sitemaps.views import sitemap
from django.views.defaults import bad_request
from django.views.defaults import page_not_found
from django.views.defaults import permission_denied
from django.views.defaults import server_error
from django.views.generic.base import RedirectView
from django.views.static import serve

from django_xmlrpc.views import handle_xmlrpc

from zinnia.sitemaps import AuthorSitemap
from zinnia.sitemaps import CategorySitemap
from zinnia.sitemaps import EntrySitemap
from zinnia.sitemaps import TagSitemap


urlpatterns = [
    path('', RedirectView.as_view(url='/blog/', permanent=True)),
    re_path(r'^blog/', include('zinnia.urls')),
    re_path(r'^comments/', include('django_comments.urls')),
    path('xmlrpc/', handle_xmlrpc),
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
    path('400/', partial(bad_request, exception=None)),
    path('403/', partial(permission_denied, exception=None)),
    path('404/', partial(page_not_found, exception=None)),
    path('500/', server_error),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT})
    ]

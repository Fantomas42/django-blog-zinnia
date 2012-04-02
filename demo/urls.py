"""Urls for the demo of Zinnia"""
from django.conf import settings
from django.contrib import admin
from django.conf.urls import url
from django.conf.urls import include
from django.conf.urls import patterns
from django.views.generic.base import RedirectView

from zinnia.sitemaps import TagSitemap
from zinnia.sitemaps import EntrySitemap
from zinnia.sitemaps import CategorySitemap
from zinnia.sitemaps import AuthorSitemap

admin.autodiscover()
handler500 = 'demo.views.server_error'
handler404 = 'django.views.defaults.page_not_found'

urlpatterns = patterns(
    '',
    url(r'^$', RedirectView.as_view(url='/blog/')),
    url(r'^blog/', include('zinnia.urls')),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^xmlrpc/$', 'django_xmlrpc.views.handle_xmlrpc'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    )

sitemaps = {'tags': TagSitemap,
            'blog': EntrySitemap,
            'authors': AuthorSitemap,
            'categories': CategorySitemap}

urlpatterns += patterns(
    'django.contrib.sitemaps.views',
    url(r'^sitemap.xml$', 'index',
        {'sitemaps': sitemaps}),
    url(r'^sitemap-(?P<section>.+)\.xml$', 'sitemap',
        {'sitemaps': sitemaps}),
    )

urlpatterns += patterns(
    '',
    url(r'^404/$', 'django.views.defaults.page_not_found'),
    url(r'^500/$', 'demo.views.server_error'),
    )

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT})
        )

"""Urls for the demo of Zinnia"""
import os

from django.contrib import admin
from django.conf.urls.defaults import url
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import handler404
from django.conf.urls.defaults import handler500

from zinnia.sitemaps import TagSitemap
from zinnia.sitemaps import EntrySitemap
from zinnia.sitemaps import CategorySitemap
from zinnia.sitemaps import AuthorSitemap

admin.autodiscover()

urlpatterns = patterns('',
                       (r'^$', 'django.views.generic.simple.redirect_to',
                        {'url': '/blog/'}),
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
            'categories': CategorySitemap,}

urlpatterns += patterns('django.contrib.sitemaps.views',
                        (r'^sitemap.xml$', 'index',
                         {'sitemaps': sitemaps}),
                        (r'^sitemap-(?P<section>.+)\.xml$', 'sitemap',
                         {'sitemaps': sitemaps}),
                        )

urlpatterns += patterns('django.views.static',
                        url(r'^zinnia/(?P<path>.*)$', 'serve',
                            {'document_root': os.path.join(os.path.dirname(__file__),
                                                           '..', 'zinnia', 'media', 'zinnia')}),
                        )

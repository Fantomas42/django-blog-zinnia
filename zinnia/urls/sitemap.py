"""Urls for the zinnia sitemap"""
from django.conf.urls.defaults import *

from zinnia.models import Entry
from zinnia.models import Category

urlpatterns = patterns('django.views.generic.simple',
                       url(r'^sitemap/$', 'direct_to_template',
                           {'template': 'zinnia/sitemap.html',
                            'extra_context': {'entries': Entry.published.all(),
                                              'categories': Category.objects.all()}},
                           name='zinnia_sitemap'),
                       )



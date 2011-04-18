"""Test urls for the zinnia project"""
from functools import wraps

from django.conf.urls.defaults import url
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns

from zinnia.urls import urlpatterns as defaultpatterns
from zinnia.views.authors import author_detail
from zinnia.views.categories import category_detail
from zinnia.views.tags import tag_detail

def call_with_template(view, template_name):
    @wraps(view)
    def dec(*args, **kwargs):
        return view(template_name=template_name, *args, **kwargs)
    return dec

author_detail = call_with_template(author_detail, 'zinnia/entry_list.html')
category_detail = call_with_template(category_detail, 'zinnia/entry_list.html')
tag_detail = call_with_template(tag_detail, 'zinnia/entry_list.html')

urlpatterns = patterns('',

                    url(r'^authors/(?P<username>[.+-@\w]+)/$',
                            author_detail,
                            name='zinnia_author_detail'),
                    url(r'^authors/(?P<username>[.+-@\w]+)/page/(?P<page>\d+)/$',
                            author_detail,
                            name='zinnia_author_detail_paginated'),

                    url(r'^categories/(?P<path>[-\/\w]+)/page/(?P<page>\d+)/$',
                            category_detail,
                            name='zinnia_category_detail_paginated'),
                    url(r'^categories/(?P<path>[-\/\w]+)/$', category_detail,
                            name='zinnia_category_detail'),

                    url(r'^tags/(?P<tag>[- \w]+)/$', tag_detail,
                            name='zinnia_tag_detail'),
                    url(r'^tags/(?P<tag>[- \w]+)/page/(?P<page>\d+)/$',
                            tag_detail, name='zinnia_tag_detail_paginated'),
) + defaultpatterns

"""Test urls for the zinnia project"""
from functools import wraps

from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from zinnia.views.tags import tag_detail
from zinnia.views.authors import author_detail
from zinnia.views.categories import category_detail


def call_with_template_and_extra_context(
    view, template_name='zinnia/entry_list.html',
    extra_context={'extra': 'context'}):

    @wraps(view)
    def wrapper(*args, **kwargs):
        return view(template_name=template_name,
                    extra_context=extra_context,
                    *args, **kwargs)

    return wrapper

custom_tag_detail = call_with_template_and_extra_context(tag_detail)
custom_author_detail = call_with_template_and_extra_context(author_detail)
custom_category_detail = call_with_template_and_extra_context(category_detail)


urlpatterns = patterns(
    '',
    url(r'^authors/(?P<username>[.+-@\w]+)/$',
        custom_author_detail, name='zinnia_author_detail'),
    url(r'^authors/(?P<username>[.+-@\w]+)/page/(?P<page>\d+)/$',
        custom_author_detail, name='zinnia_author_detail_paginated'),
    url(r'^categories/(?P<path>[-\/\w]+)/page/(?P<page>\d+)/$',
        custom_category_detail, name='zinnia_category_detail_paginated'),
    url(r'^categories/(?P<path>[-\/\w]+)/$',
        custom_category_detail, name='zinnia_category_detail'),
    url(r'^tags/(?P<tag>[- \w]+)/$',
        custom_tag_detail, name='zinnia_tag_detail'),
    url(r'^tags/(?P<tag>[- \w]+)/page/(?P<page>\d+)/$',
        custom_tag_detail, name='zinnia_tag_detail_paginated'),
    )

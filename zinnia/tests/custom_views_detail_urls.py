"""Test urls for the zinnia project"""
from functools import wraps

from django.conf.urls import url
from django.conf.urls import patterns

from zinnia.views.tags import tag_detail
from zinnia.views.authors import AuthorDetail
from zinnia.views.categories import CategoryDetail
from zinnia.tests.urls import urlpatterns as test_urlpatterns


class CustomModelDetailMixin(object):
    """Mixin for changing the template_name
    and overriding the context"""
    template_name = 'zinnia/entry_list.html'

    def get_context_data(self, **kwargs):
        context = super(CustomModelDetailMixin,
                        self).get_context_data(**kwargs)
        context.update({'extra': 'context'})
        return context


class CustomAuthorDetail(CustomModelDetailMixin, AuthorDetail):
    pass


class CustomCategoryDetail(CustomModelDetailMixin, CategoryDetail):
    pass


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


urlpatterns = patterns(
    '',
    url(r'^authors/(?P<username>[.+-@\w]+)/$',
        CustomAuthorDetail.as_view(),
        name='zinnia_author_detail'),
    url(r'^authors/(?P<username>[.+-@\w]+)/page/(?P<page>\d+)/$',
        CustomAuthorDetail.as_view(),
        name='zinnia_author_detail_paginated'),
    url(r'^categories/(?P<path>[-\/\w]+)/page/(?P<page>\d+)/$',
        CustomCategoryDetail.as_view(),
        name='zinnia_category_detail_paginated'),
    url(r'^categories/(?P<path>[-\/\w]+)/$',
        CustomCategoryDetail.as_view(),
        name='zinnia_category_detail'),
    url(r'^tags/(?P<tag>[- \w]+)/$',
        custom_tag_detail, name='zinnia_tag_detail'),
    url(r'^tags/(?P<tag>[- \w]+)/page/(?P<page>\d+)/$',
        custom_tag_detail, name='zinnia_tag_detail_paginated'),
    ) + test_urlpatterns

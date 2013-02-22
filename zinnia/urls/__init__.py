"""Defaults urls for the Zinnia project"""
from django.conf.urls import url
from django.conf.urls import include
from django.conf.urls import patterns

from django.utils.translation import ugettext_lazy

from zinnia.settings import TRANSLATED_URLS


def _(url_to_translate):
    """
    Translate or not the default Zinnia's URLs.
    """
    if TRANSLATED_URLS:
        return ugettext_lazy(url_to_translate)
    return url_to_translate


urlpatterns = patterns(
    '',
    url(_(r'^feeds/'), include('zinnia.urls.feeds')),
    url(_(r'^tags/'), include('zinnia.urls.tags',)),
    url(_(r'^authors/'), include('zinnia.urls.authors')),
    url(_(r'^categories/'), include('zinnia.urls.categories')),
    url(_(r'^search/'), include('zinnia.urls.search')),
    url(_(r'^random/'), include('zinnia.urls.random')),
    url(_(r'^sitemap/'), include('zinnia.urls.sitemap')),
    url(_(r'^trackback/'), include('zinnia.urls.trackback')),
    url(_(r'^comments/'), include('zinnia.urls.comments')),
    url(r'^', include('zinnia.urls.entries')),
    url(r'^', include('zinnia.urls.archives')),
    url(r'^', include('zinnia.urls.shortlink')),
    url(r'^', include('zinnia.urls.quick_entry')),
    url(r'^', include('zinnia.urls.capabilities')),
)

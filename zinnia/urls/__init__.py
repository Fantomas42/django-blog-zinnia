"""Defaults urls for the Zinnia project"""
from django.urls import include, re_path
from django.utils.translation import gettext_lazy

from zinnia.settings import TRANSLATED_URLS


def i18n_url(url, translate=TRANSLATED_URLS):
    """
    Translate or not an URL part.
    """
    if translate:
        return gettext_lazy(url)
    return url


_ = i18n_url

app_name = 'zinnia'

urlpatterns = [
    re_path(_(r'^feeds/'), include('zinnia.urls.feeds')),
    re_path(_(r'^tags/'), include('zinnia.urls.tags')),
    re_path(_(r'^authors/'), include('zinnia.urls.authors')),
    re_path(_(r'^categories/'), include('zinnia.urls.categories')),
    re_path(_(r'^search/'), include('zinnia.urls.search')),
    re_path(_(r'^random/'), include('zinnia.urls.random')),
    re_path(_(r'^sitemap/'), include('zinnia.urls.sitemap')),
    re_path(_(r'^trackback/'), include('zinnia.urls.trackback')),
    re_path(_(r'^comments/'), include('zinnia.urls.comments')),
    re_path(r'^', include('zinnia.urls.entries')),
    re_path(r'^', include('zinnia.urls.archives')),
    re_path(r'^', include('zinnia.urls.shortlink')),
    re_path(r'^', include('zinnia.urls.quick_entry')),
    re_path(r'^', include('zinnia.urls.capabilities')),
]

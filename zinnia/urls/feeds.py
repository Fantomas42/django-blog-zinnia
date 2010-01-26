"""Urls for the zinnia feeds"""
from django.conf.urls.defaults import *

from zinnia.feeds import LatestEntries
from zinnia.feeds import CommentEntries
from zinnia.feeds import SearchEntries
from zinnia.feeds import TagEntries
from zinnia.feeds import CategoryEntries
from zinnia.feeds import AuthorEntries

feeds = {'latest': LatestEntries,
         'comments': CommentEntries,
         'search': SearchEntries,
         'tags': TagEntries,
         'authors': AuthorEntries,
         'categories': CategoryEntries}

urlpatterns = patterns('',
    url(r'^(?P<url>.*)/$', 'django.contrib.syndication.views.feed',
    {'feed_dict': feeds, }, 'feeds'),
)

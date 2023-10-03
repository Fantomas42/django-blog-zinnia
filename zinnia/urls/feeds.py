"""Urls for the Zinnia feeds"""
from django.urls import path, re_path

from zinnia.feeds import AuthorEntries
from zinnia.feeds import CategoryEntries
from zinnia.feeds import EntryComments
from zinnia.feeds import EntryDiscussions
from zinnia.feeds import EntryPingbacks
from zinnia.feeds import EntryTrackbacks
from zinnia.feeds import LastDiscussions
from zinnia.feeds import LastEntries
from zinnia.feeds import SearchEntries
from zinnia.feeds import TagEntries
from zinnia.urls import _


urlpatterns = [
    path('',
        LastEntries(),
        name='entry_feed'),
    re_path(_(r'^discussions/$'),
        LastDiscussions(),
        name='discussion_feed'),
    re_path(_(r'^search/$'),
        SearchEntries(),
        name='entry_search_feed'),
    re_path(_(r'^tags/(?P<tag>[^/]+)/$'),
        TagEntries(),
        name='tag_feed'),
    re_path(_(r'^authors/(?P<username>[.+-@\w]+)/$'),
        AuthorEntries(),
        name='author_feed'),
    re_path(_(r'^categories/(?P<path>[-\/\w]+)/$'),
        CategoryEntries(),
        name='category_feed'),
    re_path(_(r'^discussions/(?P<year>\d{4})/(?P<month>\d{2})/'
          r'(?P<day>\d{2})/(?P<slug>[-\w]+)/$'),
        EntryDiscussions(),
        name='entry_discussion_feed'),
    re_path(_(r'^comments/(?P<year>\d{4})/(?P<month>\d{2})/'
          r'(?P<day>\d{2})/(?P<slug>[-\w]+)/$'),
        EntryComments(),
        name='entry_comment_feed'),
    re_path(_(r'^pingbacks/(?P<year>\d{4})/(?P<month>\d{2})/'
          r'(?P<day>\d{2})/(?P<slug>[-\w]+)/$'),
        EntryPingbacks(),
        name='entry_pingback_feed'),
    re_path(_(r'^trackbacks/(?P<year>\d{4})/(?P<month>\d{2})/'
          r'(?P<day>\d{2})/(?P<slug>[-\w]+)/$'),
        EntryTrackbacks(),
        name='entry_trackback_feed'),
]

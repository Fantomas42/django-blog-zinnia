"""Urls for the Zinnia feeds"""
from django.conf.urls import url

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
    url(r'^$',
        LastEntries(),
        name='entry_feed'),
    url(_(r'^discussions/$'),
        LastDiscussions(),
        name='discussion_feed'),
    url(_(r'^search/$'),
        SearchEntries(),
        name='entry_search_feed'),
    url(_(r'^tags/(?P<tag>[^/]+)/$'),
        TagEntries(),
        name='tag_feed'),
    url(_(r'^authors/(?P<username>[.+-@\w]+)/$'),
        AuthorEntries(),
        name='author_feed'),
    url(_(r'^categories/(?P<path>[-\/\w]+)/$'),
        CategoryEntries(),
        name='category_feed'),
    url(_(r'^discussions/(?P<year>\d{4})/(?P<month>\d{2})/'
          r'(?P<day>\d{2})/(?P<slug>[-\w]+)/$'),
        EntryDiscussions(),
        name='entry_discussion_feed'),
    url(_(r'^comments/(?P<year>\d{4})/(?P<month>\d{2})/'
          r'(?P<day>\d{2})/(?P<slug>[-\w]+)/$'),
        EntryComments(),
        name='entry_comment_feed'),
    url(_(r'^pingbacks/(?P<year>\d{4})/(?P<month>\d{2})/'
          r'(?P<day>\d{2})/(?P<slug>[-\w]+)/$'),
        EntryPingbacks(),
        name='entry_pingback_feed'),
    url(_(r'^trackbacks/(?P<year>\d{4})/(?P<month>\d{2})/'
          r'(?P<day>\d{2})/(?P<slug>[-\w]+)/$'),
        EntryTrackbacks(),
        name='entry_trackback_feed'),
]

"""Urls for the Zinnia feeds"""
from django.conf.urls import url
from django.conf.urls import patterns

from zinnia.urls import _
from zinnia.feeds import LatestEntries
from zinnia.feeds import TagEntries
from zinnia.feeds import AuthorEntries
from zinnia.feeds import CategoryEntries
from zinnia.feeds import SearchEntries
from zinnia.feeds import EntryComments
from zinnia.feeds import EntryPingbacks
from zinnia.feeds import EntryTrackbacks
from zinnia.feeds import EntryDiscussions
from zinnia.feeds import LatestDiscussions


urlpatterns = patterns(
    '',
    url(r'^$',
        LatestEntries(),
        name='zinnia_entry_latest_feed'),
    url(_(r'^discussions/$'),
        LatestDiscussions(),
        name='zinnia_discussion_latest_feed'),
    url(_(r'^search/$'),
        SearchEntries(),
        name='zinnia_entry_search_feed'),
    url(_(r'^tags/(?P<tag>[^/]+(?u))/$'),
        TagEntries(),
        name='zinnia_tag_feed'),
    url(_(r'^authors/(?P<username>[.+-@\w]+)/$'),
        AuthorEntries(),
        name='zinnia_author_feed'),
    url(_(r'^categories/(?P<path>[-\/\w]+)/$'),
        CategoryEntries(),
        name='zinnia_category_feed'),
    url(_(r'^discussions/(?P<year>\d{4})/(?P<month>\d{2})/'
          '(?P<day>\d{2})/(?P<slug>[-\w]+)/$'),
        EntryDiscussions(),
        name='zinnia_entry_discussion_feed'),
    url(_(r'^comments/(?P<year>\d{4})/(?P<month>\d{2})/'
          '(?P<day>\d{2})/(?P<slug>[-\w]+)/$'),
        EntryComments(),
        name='zinnia_entry_comment_feed'),
    url(_(r'^pingbacks/(?P<year>\d{4})/(?P<month>\d{2})/'
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$'),
        EntryPingbacks(),
        name='zinnia_entry_pingback_feed'),
    url(_(r'^trackbacks/(?P<year>\d{4})/(?P<month>\d{2})/'
        '(?P<day>\d{2})/(?P<slug>[-\w]+)/$'),
        EntryTrackbacks(),
        name='zinnia_entry_trackback_feed'),
)

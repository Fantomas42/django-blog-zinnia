"""Urls for the Zinnia feeds"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from zinnia.feeds import LatestEntries
from zinnia.feeds import EntryDiscussions
from zinnia.feeds import EntryComments
from zinnia.feeds import EntryTrackbacks
from zinnia.feeds import EntryPingbacks
from zinnia.feeds import SearchEntries
from zinnia.feeds import TagEntries
from zinnia.feeds import CategoryEntries
from zinnia.feeds import AuthorEntries


urlpatterns = patterns('',
                       url(r'^latest/$',
                           LatestEntries(),
                           name='zinnia_entry_latest_feed'),
                       url(r'^tags/(?P<slug>[- \w]+)/$',
                           TagEntries(),
                           name='zinnia_tag_feed'),
                       url(r'^authors/(?P<username>[.+-@\w]+)/$',
                           AuthorEntries(),
                           name='zinnia_author_feed'),
                       url(r'^categories/(?P<path>[-\/\w]+)/$',
                           CategoryEntries(),
                           name='zinnia_category_feed'),
                       url(r'^search/(?P<slug>.*)/$',
                           SearchEntries(),
                           name='zinnia_entry_search_feed'),
                       url(r'^discussions/(?P<slug>[-\w]+)/$',
                           EntryDiscussions(),
                           name='zinnia_entry_discussion_feed'),
                       url(r'^comments/(?P<slug>[-\w]+)/$',
                           EntryComments(),
                           name='zinnia_entry_comment_feed'),
                       url(r'^pingbacks/(?P<slug>[-\w]+)/$',
                           EntryPingbacks(),
                           name='zinnia_entry_pingback_feed'),
                       url(r'^trackbacks/(?P<slug>[-\w]+)/$',
                           EntryTrackbacks(),
                           name='zinnia_entry_trackback_feed'),
                       )

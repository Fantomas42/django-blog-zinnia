"""Urls for the zinnia feeds"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from zinnia.feeds import LatestEntries, AtomLatestEntries
from zinnia.feeds import EntryDiscussions, AtomEntryDiscussions
from zinnia.feeds import EntryComments, AtomEntryComments
from zinnia.feeds import EntryTrackbacks, AtomEntryTrackbacks
from zinnia.feeds import EntryPingbacks, AtomEntryPingbacks
from zinnia.feeds import SearchEntries, AtomSearchEntries
from zinnia.feeds import TagEntries, AtomTagEntries
from zinnia.feeds import CategoryEntries, AtomCategoryEntries
from zinnia.feeds import AuthorEntries, AtomAuthorEntries

from zinnia.settings import FEEDS_FORMAT


if FEEDS_FORMAT == 'atom':
    urlpatterns = patterns('',
                           url(r'^latest/$', AtomLatestEntries(),
                               name='zinnia_entry_latest_feed'),
                           url(r'^tags/(?P<slug>[- \w]+)/$', AtomTagEntries(),
                               name='zinnia_tag_feed'),
                           url(r'^authors/(?P<username>[.+-@\w]+)/$', AtomAuthorEntries(),
                               name='zinnia_author_feed'),
                           url(r'^categories/(?P<path>[-\/\w]+)/$', AtomCategoryEntries(),
                               name='zinnia_category_feed'),
                           url(r'^search/(?P<slug>.*)/$', AtomSearchEntries(),
                               name='zinnia_entry_search_feed'),
                           url(r'^discussions/(?P<slug>[-\w]+)/$', AtomEntryDiscussions(),
                               name='zinnia_entry_discussion_feed'),
                           url(r'^comments/(?P<slug>[-\w]+)/$', AtomEntryComments(),
                               name='zinnia_entry_comment_feed'),
                           url(r'^pingbacks/(?P<slug>[-\w]+)/$', AtomEntryPingbacks(),
                               name='zinnia_entry_pingback_feed'),
                           url(r'^trackbacks/(?P<slug>[-\w]+)/$', AtomEntryTrackbacks(),
                               name='zinnia_entry_trackback_feed'),
                           )
else:
    urlpatterns = patterns('',
                           url(r'^latest/$', LatestEntries(),
                               name='zinnia_entry_latest_feed'),
                           url(r'^tags/(?P<slug>[- \w]+)/$', TagEntries(),
                               name='zinnia_tag_feed'),
                           url(r'^authors/(?P<username>[.+-@\w]+)/$', AuthorEntries(),
                               name='zinnia_author_feed'),
                           url(r'^categories/(?P<path>[-\/\w]+)/$', CategoryEntries(),
                               name='zinnia_category_feed'),
                           url(r'^search/(?P<slug>.*)/$', SearchEntries(),
                               name='zinnia_entry_search_feed'),
                           url(r'^discussions/(?P<slug>[-\w]+)/$', EntryDiscussions(),
                               name='zinnia_entry_discussion_feed'),
                           url(r'^comments/(?P<slug>[-\w]+)/$', EntryComments(),
                               name='zinnia_entry_comment_feed'),
                           url(r'^pingbacks/(?P<slug>[-\w]+)/$', EntryPingbacks(),
                               name='zinnia_entry_pingback_feed'),
                           url(r'^trackbacks/(?P<slug>[-\w]+)/$', EntryTrackbacks(),
                               name='zinnia_entry_trackback_feed'),
                           )


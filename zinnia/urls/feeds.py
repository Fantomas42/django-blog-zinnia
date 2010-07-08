"""Urls for the zinnia feeds"""
from django.conf.urls.defaults import *

from zinnia.feeds import LatestEntries, AtomLatestEntries
from zinnia.feeds import CommentEntries, AtomCommentEntries
from zinnia.feeds import SearchEntries, AtomSearchEntries
from zinnia.feeds import TagEntries, AtomTagEntries
from zinnia.feeds import CategoryEntries, AtomCategoryEntries
from zinnia.feeds import AuthorEntries, AtomAuthorEntries

from zinnia.settings import FEEDS_FORMAT


if FEEDS_FORMAT == 'atom':
    urlpatterns = patterns('',
                           url(r'^latest/$', AtomLatestEntries(),
                               name='zinnia_entry_latest_feed'),
                           url(r'^tags/(?P<slug>[-\w]+)/$', AtomTagEntries(),
                               name='zinnia_tag_feed'),
                           url(r'^authors/(?P<username>[-\w]+)/$', AtomAuthorEntries(),
                               name='zinnia_author_feed'),
                           url(r'^categories/(?P<slug>[-\w]+)/$', AtomCategoryEntries(),
                               name='zinnia_category_feed'),
                           url(r'^search/(?P<slug>[-\w]+)/$', AtomSearchEntries(),
                               name='zinnia_entry_search_feed'),
                           url(r'^comments/(?P<slug>[-\w]+)/$', AtomCommentEntries(),
                               name='zinnia_entry_comment_feed'),
                           )
else:
    urlpatterns = patterns('',
                           url(r'^latest/$', LatestEntries(),
                               name='zinnia_entry_latest_feed'),
                           url(r'^tags/(?P<slug>[-\w]+)/$', TagEntries(),
                               name='zinnia_tag_feed'),
                           url(r'^authors/(?P<username>[-\w]+)/$', AuthorEntries(),
                               name='zinnia_author_feed'),
                           url(r'^categories/(?P<slug>[-\w]+)/$', CategoryEntries(),
                               name='zinnia_category_feed'),
                           url(r'^search/(?P<slug>[-\w]+)/$', SearchEntries(),
                               name='zinnia_entry_search_feed'),
                           url(r'^comments/(?P<slug>[-\w]+)/$', CommentEntries(),
                               name='zinnia_entry_comment_feed'),
                           )


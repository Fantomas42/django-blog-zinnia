"""Urls for the zinnia feeds"""
from django.conf.urls.defaults import *

from zinnia.feeds import LatestEntries
from zinnia.feeds import CommentEntries
from zinnia.feeds import SearchEntries
from zinnia.feeds import TagEntries
from zinnia.feeds import CategoryEntries
from zinnia.feeds import AuthorEntries


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
                       

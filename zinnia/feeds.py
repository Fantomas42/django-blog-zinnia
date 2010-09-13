"""Feeds for Zinnia"""
from datetime import datetime
from sgmllib import SGMLParser

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.comments.models import Comment
from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext as _
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404

from tagging.models import Tag
from tagging.models import TaggedItem

from zinnia.models import Entry
from zinnia.models import Category
from zinnia.settings import COPYRIGHT
from zinnia.settings import FEEDS_MAX_ITEMS
from zinnia.managers import entries_published
from zinnia.views.categories import get_category_or_404


current_site = Site.objects.get_current()

class ImgParser(SGMLParser):
    """Parser for getting img markups"""

    def __init__(self):
        SGMLParser.__init__(self)
        self.img_locations = []

    def start_img(self, attr):
        attr = dict(attr)
        if attr.get('src', ''):
            self.img_locations.append(attr['src'])


class EntryFeed(Feed):
    """Base Entry Feed"""
    title_template = 'feeds/entry_title.html'
    description_template= 'feeds/entry_description.html'
    feed_copyright = COPYRIGHT

    def item_pubdate(self, item):
        return item.creation_date

    def item_categories(self, item):
        return [category.title for category in item.categories.all()]

    def item_author_name(self, item):
        return item.authors.all()[0]

    def item_author_email(self, item):
        return item.authors.all()[0].email

    def item_author_link(self, item):
        return current_site.domain

    def item_enclosure_url(self, item):
        if item.image:
            return item.image.url
        parser = ImgParser()
        try:
            parser.feed(item.content)
        except UnicodeEncodeError:
            return
        if len(parser.img_locations):
            if current_site.domain in parser.img_locations[0]:
                return parser.img_locations[0]
            else:
                return 'http://%s%s' % (
                    current_site.domain, parser.img_locations[0])
        return None

    def item_enclosure_length(self, item):
        return '100000'

    def item_enclosure_mime_type(self, item):
        return 'image/jpeg'


class LatestEntries(EntryFeed):
    """Feed for the latest entries"""
    title = _('Latest entries')
    description = _('The latest entries for the site %s') % current_site.domain

    def link(self):
        return reverse('zinnia_entry_archive_index')

    def items(self):
        return Entry.published.all()[:FEEDS_MAX_ITEMS]


class CategoryEntries(EntryFeed):
    """Feed filtered by a category"""

    def get_object(self, request, path):
        return get_category_or_404(path)

    def items(self, obj):
        return obj.entries_published_set()[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        return obj.get_absolute_url()

    def title(self, obj):
        return _('Entries for the category %s') % obj.title

    def description(self, obj):
        return _('The latest entries for the category %s') % obj.title


class AuthorEntries(EntryFeed):
    """Feed filtered by an author"""

    def get_object(self, request, username):
        return get_object_or_404(User, username=username)

    def items(self, obj):
        return entries_published(obj.entry_set)[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        return reverse('zinnia_author_detail', args=[obj.username])

    def title(self, obj):
        return _('Entries for author %s') % obj.username

    def description(self, obj):
        return _('The latest entries by %s') % obj.username


class TagEntries(EntryFeed):
    """Feed filtered by a tag"""

    def get_object(self, request, slug):
        return get_object_or_404(Tag, name=slug)

    def items(self, obj):
        return TaggedItem.objects.get_by_model(
            Entry.published.all(), obj)[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        return reverse('zinnia_tag_detail', args=[obj.name])

    def title(self, obj):
        return _('Entries for the tag %s') % obj.name

    def description(self, obj):
        return _('The latest entries for the tag %s') % obj.name


class SearchEntries(EntryFeed):
    """Feed filtered by search pattern"""

    def get_object(self, request, slug):
        return slug

    def items(self, obj):
        return Entry.published.search(obj)[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        return '%s?pattern=%s' % (reverse('zinnia_entry_search'), obj)

    def title(self, obj):
        return _("Results of the search for %s") % obj

    def description(self, obj):
        return _("The entries containing the pattern %s") % obj


class EntryDiscussions(Feed):
    """Feed for discussions in an entry"""
    title_template = 'feeds/discussion_title.html'
    description_template= 'feeds/discussion_description.html'
    feed_copyright = COPYRIGHT

    def get_object(self, request, slug):
        return get_object_or_404(Entry, slug=slug)

    def items(self, obj):
        return obj.discussions[:FEEDS_MAX_ITEMS]

    def item_pubdate(self, item):
        return item.submit_date

    def item_link(self, item):
        return item.get_absolute_url()

    def link(self, obj):
        return obj.get_absolute_url()

    def item_author_name(self, item):
        return item.userinfo['name']

    def item_author_email(self, item):
        return item.userinfo['email']

    def item_author_link(self, item):
        return item.userinfo['url']

    def title(self, obj):
        return _('Discussions on %s') % obj.title

    def description(self, obj):
        return _('The latest discussions for the entry %s') % obj.title
    

class EntryComments(EntryDiscussions):
    """Feed for comments in an entry"""
    title_template = 'feeds/comment_title.html'
    description_template= 'feeds/comment_description.html'

    def items(self, obj):
        return obj.comments[:FEEDS_MAX_ITEMS]

    def item_link(self, item):
        return item.get_absolute_url('#comment_%(id)s')

    def title(self, obj):
        return _('Comments on %s') % obj.title

    def description(self, obj):
        return _('The latest comments for the entry %s') % obj.title

class EntryPingbacks(EntryDiscussions):
    """Feed for pingbacks in an entry"""
    title_template = 'feeds/pingback_title.html'
    description_template= 'feeds/pingback_description.html'

    def items(self, obj):
        return obj.pingbacks[:FEEDS_MAX_ITEMS]

    def item_link(self, item):
        return item.get_absolute_url('#pingback_%(id)s')

    def title(self, obj):
        return _('Pingbacks on %s') % obj.title

    def description(self, obj):
        return _('The latest pingbacks for the entry %s') % obj.title

class EntryTrackbacks(EntryDiscussions):
    """Feed for trackbacks in an entry"""
    title_template = 'feeds/trackback_title.html'
    description_template= 'feeds/trackback_description.html'

    def items(self, obj):
        return obj.trackbacks[:FEEDS_MAX_ITEMS]

    def item_link(self, item):
        return item.get_absolute_url('#trackback_%(id)s')

    def title(self, obj):
        return _('Trackbacks on %s') % obj.title

    def description(self, obj):
        return _('The latest trackbacks for the entry %s') % obj.title

# Atom versions of the feeds

class AtomLatestEntries(LatestEntries):
    feed_type = Atom1Feed
    subtitle = LatestEntries.description

class AtomCategoryEntries(CategoryEntries):
    feed_type = Atom1Feed
    subtitle = CategoryEntries.description

class AtomAuthorEntries(AuthorEntries):
    feed_type = Atom1Feed
    subtitle = AuthorEntries.description

class AtomTagEntries(TagEntries):
    feed_type = Atom1Feed
    subtitle = TagEntries.description

class AtomSearchEntries(SearchEntries):
    feed_type = Atom1Feed
    subtitle = SearchEntries.description

class AtomEntryDiscussions(EntryDiscussions):
    feed_type = Atom1Feed
    subtitle = EntryDiscussions.description

class AtomEntryComments(EntryComments):
    feed_type = Atom1Feed
    subtitle = EntryComments.description

class AtomEntryPingbacks(EntryPingbacks):
    feed_type = Atom1Feed
    subtitle = EntryPingbacks.description

class AtomEntryTrackbacks(EntryTrackbacks):
    feed_type = Atom1Feed
    subtitle = EntryTrackbacks.description

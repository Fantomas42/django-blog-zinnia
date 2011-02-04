"""Feeds for Zinnia"""
from sgmllib import SGMLParser

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.core.urlresolvers import NoReverseMatch
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext as _
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404

from tagging.models import Tag
from tagging.models import TaggedItem

from zinnia.models import Entry
from zinnia.settings import COPYRIGHT
from zinnia.settings import PROTOCOL
from zinnia.settings import FEEDS_MAX_ITEMS
from zinnia.managers import entries_published
from zinnia.views.categories import get_category_or_404


class ImgParser(SGMLParser):
    """Parser for getting IMG markups"""

    def __init__(self):
        SGMLParser.__init__(self)
        self.img_locations = []

    def start_img(self, attr):
        """Save each image's location"""
        attr = dict(attr)
        if attr.get('src', ''):
            self.img_locations.append(attr['src'])


class EntryFeed(Feed):
    """Base Entry Feed"""
    title_template = 'feeds/entry_title.html'
    description_template = 'feeds/entry_description.html'
    feed_copyright = COPYRIGHT

    def __init__(self):
        self.site = Site.objects.get_current()

    def item_pubdate(self, item):
        """Publication date of an entry"""
        return item.creation_date

    def item_categories(self, item):
        """Entry's categories"""
        return [category.title for category in item.categories.all()]

    def item_author_name(self, item):
        """Returns the first author of an entry"""
        return item.authors.all()[0].username

    def item_author_email(self, item):
        """Returns the first author's email"""
        return item.authors.all()[0].email

    def item_author_link(self, item):
        """Returns the author's URL"""
        url = '%s://%s' % (PROTOCOL, self.site.domain)
        try:
            author_url = reverse('zinnia_author_detail',
                                 args=[item.authors.all()[0].username])
            return url + author_url
        except NoReverseMatch:
            return url

    def item_enclosure_url(self, item):
        """Returns an image for enclosure"""
        if item.image:
            return item.image.url
        parser = ImgParser()
        try:
            parser.feed(item.content)
        except UnicodeEncodeError:
            return
        if len(parser.img_locations):
            if self.site.domain in parser.img_locations[0]:
                return parser.img_locations[0]
            else:
                return '%s://%s%s' % (PROTOCOL,
                                      self.site.domain,
                                      parser.img_locations[0])
        return None

    def item_enclosure_length(self, item):
        """Hardcoded enclosure length"""
        return '100000'

    def item_enclosure_mime_type(self, item):
        """Hardcoded enclosure mimetype"""
        return 'image/jpeg'


class LatestEntries(EntryFeed):
    """Feed for the latest entries"""
    title = _('Latest entries')

    def link(self):
        """URL of latest entries"""
        return reverse('zinnia_entry_archive_index')

    def items(self):
        """Items are published entries"""
        return Entry.published.all()[:FEEDS_MAX_ITEMS]

    def description(self, obj):
        """Description of the feed"""
        return _('The latest entries for the site %s') % self.site.domain


class CategoryEntries(EntryFeed):
    """Feed filtered by a category"""

    def get_object(self, request, path):
        """Retrieve the category by his path"""
        return get_category_or_404(path)

    def items(self, obj):
        """Items are the published entries of the category"""
        return obj.entries_published_set()[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        """URL of the category"""
        return obj.get_absolute_url()

    def title(self, obj):
        """Title of the feed"""
        return _('Entries for the category %s') % obj.title

    def description(self, obj):
        """Description of the feed"""
        return _('The latest entries for the category %s') % obj.title


class AuthorEntries(EntryFeed):
    """Feed filtered by an author"""

    def get_object(self, request, username):
        """Retrieve the author by his username"""
        return get_object_or_404(User, username=username)

    def items(self, obj):
        """Items are the published entries of the author"""
        return entries_published(obj.entry_set)[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        """URL of the author"""
        return reverse('zinnia_author_detail', args=[obj.username])

    def title(self, obj):
        """Title of the feed"""
        return _('Entries for author %s') % obj.username

    def description(self, obj):
        """Description of the feed"""
        return _('The latest entries by %s') % obj.username


class TagEntries(EntryFeed):
    """Feed filtered by a tag"""

    def get_object(self, request, slug):
        """Retrieve the tag by his name"""
        return get_object_or_404(Tag, name=slug)

    def items(self, obj):
        """Items are the published entries of the tag"""
        return TaggedItem.objects.get_by_model(
            Entry.published.all(), obj)[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        """URL of the tag"""
        return reverse('zinnia_tag_detail', args=[obj.name])

    def title(self, obj):
        """Title of the feed"""
        return _('Entries for the tag %s') % obj.name

    def description(self, obj):
        """Description of the feed"""
        return _('The latest entries for the tag %s') % obj.name


class SearchEntries(EntryFeed):
    """Feed filtered by a search pattern"""

    def get_object(self, request, slug):
        """The slug is the pattern to search"""
        return slug

    def items(self, obj):
        """Items are the published entries founds"""
        return Entry.published.search(obj)[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        """URL of the search request"""
        return '%s?pattern=%s' % (reverse('zinnia_entry_search'), obj)

    def title(self, obj):
        """Title of the feed"""
        return _('Results of the search for %s') % obj

    def description(self, obj):
        """Description of the feed"""
        return _('The entries containing the pattern %s') % obj


class EntryDiscussions(Feed):
    """Feed for discussions in an entry"""
    title_template = 'feeds/discussion_title.html'
    description_template = 'feeds/discussion_description.html'
    feed_copyright = COPYRIGHT

    def get_object(self, request, slug):
        """Retrieve the discussions by entry's slug"""
        return get_object_or_404(Entry, slug=slug)

    def items(self, obj):
        """Items are the discussions on the entry"""
        return obj.discussions[:FEEDS_MAX_ITEMS]

    def item_pubdate(self, item):
        """Publication date of a discussion"""
        return item.submit_date

    def item_link(self, item):
        """URL of the discussion"""
        return item.get_absolute_url()

    def link(self, obj):
        """URL of the entry"""
        return obj.get_absolute_url()

    def item_author_name(self, item):
        """Author of the discussion"""
        return item.userinfo['name']

    def item_author_email(self, item):
        """Author's email of the discussion"""
        return item.userinfo['email']

    def item_author_link(self, item):
        """Author's URL of the discussion"""
        return item.userinfo['url']

    def title(self, obj):
        """Title of the feed"""
        return _('Discussions on %s') % obj.title

    def description(self, obj):
        """Description of the feed"""
        return _('The latest discussions for the entry %s') % obj.title


class EntryComments(EntryDiscussions):
    """Feed for comments in an entry"""
    title_template = 'feeds/comment_title.html'
    description_template = 'feeds/comment_description.html'

    def items(self, obj):
        """Items are the comments on the entry"""
        return obj.comments[:FEEDS_MAX_ITEMS]

    def item_link(self, item):
        """URL of the comment"""
        return item.get_absolute_url('#comment_%(id)s')

    def title(self, obj):
        """Title of the feed"""
        return _('Comments on %s') % obj.title

    def description(self, obj):
        """Description of the feed"""
        return _('The latest comments for the entry %s') % obj.title


class EntryPingbacks(EntryDiscussions):
    """Feed for pingbacks in an entry"""
    title_template = 'feeds/pingback_title.html'
    description_template = 'feeds/pingback_description.html'

    def items(self, obj):
        """Items are the pingbacks on the entry"""
        return obj.pingbacks[:FEEDS_MAX_ITEMS]

    def item_link(self, item):
        """URL of the pingback"""
        return item.get_absolute_url('#pingback_%(id)s')

    def title(self, obj):
        """Title of the feed"""
        return _('Pingbacks on %s') % obj.title

    def description(self, obj):
        """Description of the feed"""
        return _('The latest pingbacks for the entry %s') % obj.title


class EntryTrackbacks(EntryDiscussions):
    """Feed for trackbacks in an entry"""
    title_template = 'feeds/trackback_title.html'
    description_template = 'feeds/trackback_description.html'

    def items(self, obj):
        """Items are the trackbacks on the entry"""
        return obj.trackbacks[:FEEDS_MAX_ITEMS]

    def item_link(self, item):
        """URL of the trackback"""
        return item.get_absolute_url('#trackback_%(id)s')

    def title(self, obj):
        """Title of the feed"""
        return _('Trackbacks on %s') % obj.title

    def description(self, obj):
        """Description of the feed"""
        return _('The latest trackbacks for the entry %s') % obj.title


# Atom versions of the feeds
class AtomLatestEntries(LatestEntries):
    """Atom feed for the latest entries"""
    feed_type = Atom1Feed
    subtitle = LatestEntries.description


class AtomCategoryEntries(CategoryEntries):
    """Atom feed filtered by a category"""
    feed_type = Atom1Feed
    subtitle = CategoryEntries.description


class AtomAuthorEntries(AuthorEntries):
    """Atom feed filtered by an author"""
    feed_type = Atom1Feed
    subtitle = AuthorEntries.description


class AtomTagEntries(TagEntries):
    """Atom feed filtered by a tag"""
    feed_type = Atom1Feed
    subtitle = TagEntries.description


class AtomSearchEntries(SearchEntries):
    """Atom feed filtered by a search pattern"""
    feed_type = Atom1Feed
    subtitle = SearchEntries.description


class AtomEntryDiscussions(EntryDiscussions):
    """Atom feed for discussions in an entry"""
    feed_type = Atom1Feed
    subtitle = EntryDiscussions.description


class AtomEntryComments(EntryComments):
    """Atom feed for comments in an entry"""
    feed_type = Atom1Feed
    subtitle = EntryComments.description


class AtomEntryPingbacks(EntryPingbacks):
    """Atom feed for pingbacks in an entry"""
    feed_type = Atom1Feed
    subtitle = EntryPingbacks.description


class AtomEntryTrackbacks(EntryTrackbacks):
    """Atom feed for trackbacks in an entry"""
    feed_type = Atom1Feed
    subtitle = EntryTrackbacks.description

"""Feeds for Zinnia"""
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup

from django.contrib import comments
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext as _
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import slugify
from django.core.urlresolvers import NoReverseMatch
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from tagging.models import Tag
from tagging.models import TaggedItem

from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.settings import COPYRIGHT
from zinnia.settings import PROTOCOL
from zinnia.settings import FEEDS_FORMAT
from zinnia.settings import FEEDS_MAX_ITEMS
from zinnia.views.categories import get_category_or_404
from zinnia.templatetags.zinnia_tags import get_gravatar


class ZinniaFeed(Feed):
    """Base Feed class for the Zinnia application,
    enriched for a more convenient usage."""
    feed_copyright = COPYRIGHT
    _site = None

    def __init__(self):
        if FEEDS_FORMAT == 'atom':
            self.feed_type = Atom1Feed
            self.subtitle = self.description

    def title(self, obj=None):
        """Title of the feed prefixed with the site name """
        return '%s - %s' % (self.site.name, self.get_title(obj))

    def get_title(self, obj):
        raise NotImplementedError

    @property
    def site(self):
        if self._site is None:
            self._site = Site.objects.get_current()
        return self._site

    @property
    def site_url(self):
        return '%s://%s' % (PROTOCOL, self.site.domain)


class EntryFeed(ZinniaFeed):
    """Base Entry Feed"""
    title_template = 'feeds/entry_title.html'
    description_template = 'feeds/entry_description.html'

    def item_pubdate(self, item):
        """Publication date of an entry"""
        return item.creation_date

    def item_categories(self, item):
        """Entry's categories"""
        return [category.title for category in item.categories.all()]

    def item_author_name(self, item):
        """Returns the first author of an entry"""
        if item.authors.count():
            self.item_author = item.authors.all()[0]
            return self.item_author.__unicode__()

    def item_author_email(self, item):
        """Returns the first author's email"""
        return self.item_author.email

    def item_author_link(self, item):
        """Returns the author's URL"""
        try:
            author_url = reverse('zinnia_author_detail',
                                 args=[self.item_author.username])
            return self.site_url + author_url
        except NoReverseMatch:
            return self.site_url

    def item_enclosure_url(self, item):
        """Returns an image for enclosure"""
        if item.image:
            url = item.image.url
        else:
            img = BeautifulSoup(item.html_content).find('img')
            url = img.get('src') if img else None
        return urljoin(self.site_url, url) if url else None

    def item_enclosure_length(self, item):
        """Hardcoded enclosure length"""
        return '100000'

    def item_enclosure_mime_type(self, item):
        """Hardcoded enclosure mimetype"""
        return 'image/jpeg'


class LatestEntries(EntryFeed):
    """Feed for the latest entries"""

    def link(self):
        """URL of latest entries"""
        return reverse('zinnia_entry_archive_index')

    def items(self):
        """Items are published entries"""
        return Entry.published.all()[:FEEDS_MAX_ITEMS]

    def get_title(self, obj):
        """Title of the feed"""
        return _('Latest entries')

    def description(self):
        """Description of the feed"""
        return _('The latest entries for the site %s') % self.site.name


class CategoryEntries(EntryFeed):
    """Feed filtered by a category"""

    def get_object(self, request, path):
        """Retrieve the category by his path"""
        return get_category_or_404(path)

    def items(self, obj):
        """Items are the published entries of the category"""
        return obj.entries_published()[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        """URL of the category"""
        return obj.get_absolute_url()

    def get_title(self, obj):
        """Title of the feed"""
        return _('Entries for the category %s') % obj.title

    def description(self, obj):
        """Description of the feed"""
        return _('The latest entries for the category %s') % obj.title


class AuthorEntries(EntryFeed):
    """Feed filtered by an author"""

    def get_object(self, request, username):
        """Retrieve the author by his username"""
        return get_object_or_404(Author, username=username)

    def items(self, obj):
        """Items are the published entries of the author"""
        return obj.entries_published()[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        """URL of the author"""
        return reverse('zinnia_author_detail', args=[obj.username])

    def get_title(self, obj):
        """Title of the feed"""
        return _('Entries for author %s') % obj.__unicode__()

    def description(self, obj):
        """Description of the feed"""
        return _('The latest entries by %s') % obj.__unicode__()


class TagEntries(EntryFeed):
    """Feed filtered by a tag"""

    def get_object(self, request, tag):
        """Retrieve the tag by his name"""
        return get_object_or_404(Tag, name=tag)

    def items(self, obj):
        """Items are the published entries of the tag"""
        return TaggedItem.objects.get_by_model(
            Entry.published.all(), obj)[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        """URL of the tag"""
        return reverse('zinnia_tag_detail', args=[obj.name])

    def get_title(self, obj):
        """Title of the feed"""
        return _('Entries for the tag %s') % obj.name

    def description(self, obj):
        """Description of the feed"""
        return _('The latest entries for the tag %s') % obj.name


class SearchEntries(EntryFeed):
    """Feed filtered by a search pattern"""

    def get_object(self, request):
        """The GET parameter 'pattern' is the object"""
        pattern = request.GET.get('pattern', '')
        if len(pattern) < 3:
            raise ObjectDoesNotExist
        return pattern

    def items(self, obj):
        """Items are the published entries founds"""
        return Entry.published.search(obj)[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        """URL of the search request"""
        return '%s?pattern=%s' % (reverse('zinnia_entry_search'), obj)

    def get_title(self, obj):
        """Title of the feed"""
        return _("Results of the search for '%s'") % obj

    def description(self, obj):
        """Description of the feed"""
        return _("The entries containing the pattern '%s'") % obj


class DiscussionFeed(ZinniaFeed):
    """Base class for Discussion Feed"""
    title_template = 'feeds/discussion_title.html'
    description_template = 'feeds/discussion_description.html'

    def item_pubdate(self, item):
        """Publication date of a discussion"""
        return item.submit_date

    def item_link(self, item):
        """URL of the discussion"""
        return item.get_absolute_url()

    def item_author_name(self, item):
        """Author of the discussion"""
        return item.name

    def item_author_email(self, item):
        """Author's email of the discussion"""
        return item.email

    def item_author_link(self, item):
        """Author's URL of the discussion"""
        return item.url


class LatestDiscussions(DiscussionFeed):
    """Feed for the latest discussions"""

    def items(self):
        """Items are the discussions on the entries"""
        content_type = ContentType.objects.get_for_model(Entry)
        return comments.get_model().objects.filter(
            content_type=content_type, is_public=True).order_by(
                '-submit_date')[:FEEDS_MAX_ITEMS]

    def link(self):
        """URL of latest discussions"""
        return reverse('zinnia_entry_archive_index')

    def get_title(self, obj):
        """Title of the feed"""
        return _('Latest discussions')

    def description(self):
        """Description of the feed"""
        return _('The latest discussions for the site %s') % self.site.name


class EntryDiscussions(DiscussionFeed):
    """Feed for discussions on an entry"""

    def get_object(self, request, year, month, day, slug):
        """Retrieve the discussions by entry's slug"""
        return get_object_or_404(Entry.published, slug=slug,
                                 creation_date__year=year,
                                 creation_date__month=month,
                                 creation_date__day=day)

    def items(self, obj):
        """Items are the discussions on the entry"""
        return obj.discussions[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        """URL of the entry"""
        return obj.get_absolute_url()

    def get_title(self, obj):
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
        return item.get_absolute_url('#comment-%(id)s-by-'
                                     ) + slugify(item.user_name)

    def get_title(self, obj):
        """Title of the feed"""
        return _('Comments on %s') % obj.title

    def description(self, obj):
        """Description of the feed"""
        return _('The latest comments for the entry %s') % obj.title

    def item_enclosure_url(self, item):
        """Returns a gravatar image for enclosure"""
        return get_gravatar(item.email)

    def item_enclosure_length(self, item):
        """Hardcoded enclosure length"""
        return '100000'

    def item_enclosure_mime_type(self, item):
        """Hardcoded enclosure mimetype"""
        return 'image/jpeg'


class EntryPingbacks(EntryDiscussions):
    """Feed for pingbacks in an entry"""
    title_template = 'feeds/pingback_title.html'
    description_template = 'feeds/pingback_description.html'

    def items(self, obj):
        """Items are the pingbacks on the entry"""
        return obj.pingbacks[:FEEDS_MAX_ITEMS]

    def item_link(self, item):
        """URL of the pingback"""
        return item.get_absolute_url('#pingback-%(id)s')

    def get_title(self, obj):
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
        return item.get_absolute_url('#trackback-%(id)s')

    def get_title(self, obj):
        """Title of the feed"""
        return _('Trackbacks on %s') % obj.title

    def description(self, obj):
        """Description of the feed"""
        return _('The latest trackbacks for the entry %s') % obj.title

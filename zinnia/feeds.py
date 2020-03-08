"""Feeds for Zinnia"""
import os
from mimetypes import guess_type
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.urls import NoReverseMatch
from django.urls import reverse
from django.utils.encoding import smart_str
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import gettext as _

import django_comments as comments

from tagging.models import Tag
from tagging.models import TaggedItem

from zinnia.models.author import Author
from zinnia.models.entry import Entry
from zinnia.settings import COPYRIGHT
from zinnia.settings import FEEDS_FORMAT
from zinnia.settings import FEEDS_MAX_ITEMS
from zinnia.settings import PROTOCOL
from zinnia.templatetags.zinnia import get_gravatar
from zinnia.views.categories import get_category_or_404


class ZinniaFeed(Feed):
    """
    Base Feed class for the Zinnia application,
    enriched for a more convenient usage.
    """
    protocol = PROTOCOL
    feed_copyright = COPYRIGHT
    feed_format = FEEDS_FORMAT
    limit = FEEDS_MAX_ITEMS

    def __init__(self):
        if self.feed_format == 'atom':
            self.feed_type = Atom1Feed
            self.subtitle = getattr(self, 'description', None)

    def title(self, obj=None):
        """
        Title of the feed prefixed with the site name.
        """
        return '%s - %s' % (self.site.name, self.get_title(obj))

    def get_title(self, obj):
        raise NotImplementedError

    @property
    def site(self):
        """
        Acquire the current site used.
        """
        return Site.objects.get_current()

    @property
    def site_url(self):
        """
        Return the URL of the current site.
        """
        return '%s://%s' % (self.protocol, self.site.domain)


class EntryFeed(ZinniaFeed):
    """
    Base Entry Feed.
    """
    title_template = 'feeds/entry_title.html'
    description_template = 'feeds/entry_description.html'

    def item_pubdate(self, item):
        """
        Publication date of an entry.
        """
        return item.publication_date

    def item_updateddate(self, item):
        """
        Update date of an entry.
        """
        return item.last_update

    def item_categories(self, item):
        """
        Entry's categories.
        """
        return [category.title for category in item.categories.all()]

    def item_author_name(self, item):
        """
        Return the first author of an entry.
        """
        if item.authors.count():
            self.item_author = item.authors.all()[0]
            return self.item_author.__str__()

    def item_author_email(self, item):
        """
        Return the first author's email.
        Should not be called if self.item_author_name has returned None.
        """
        return self.item_author.email

    def item_author_link(self, item):
        """
        Return the author's URL.
        Should not be called if self.item_author_name has returned None.
        """
        try:
            author_url = self.item_author.get_absolute_url()
            return self.site_url + author_url
        except NoReverseMatch:
            return self.site_url

    def item_enclosure_url(self, item):
        """
        Return an image for enclosure.
        """
        try:
            url = item.image.url
        except (AttributeError, ValueError):
            img = BeautifulSoup(item.html_content, 'html.parser').find('img')
            url = img.get('src') if img else None
        self.cached_enclosure_url = url
        if url:
            url = urljoin(self.site_url, url)
            if self.feed_format == 'rss':
                url = url.replace('https://', 'http://')
        return url

    def item_enclosure_length(self, item):
        """
        Try to obtain the size of the enclosure if it's present on the FS,
        otherwise returns an hardcoded value.
        Note: this method is only called if item_enclosure_url
        has returned something.
        """
        try:
            return str(item.image.size)
        except (AttributeError, ValueError, os.error):
            pass
        return '100000'

    def item_enclosure_mime_type(self, item):
        """
        Guess the enclosure's mimetype.
        Note: this method is only called if item_enclosure_url
        has returned something.
        """
        mime_type, encoding = guess_type(self.cached_enclosure_url)
        if mime_type:
            return mime_type
        return 'image/jpeg'


class LastEntries(EntryFeed):
    """
    Feed for the last entries.
    """

    def link(self):
        """
        URL of last entries.
        """
        return reverse('zinnia:entry_archive_index')

    def items(self):
        """
        Items are published entries.
        """
        return Entry.published.all()[:self.limit]

    def get_title(self, obj):
        """
        Title of the feed
        """
        return _('Last entries')

    def description(self):
        """
        Description of the feed.
        """
        return _('The last entries on the site %(object)s') % {
            'object': self.site.name}


class CategoryEntries(EntryFeed):
    """
    Feed filtered by a category.
    """

    def get_object(self, request, path):
        """
        Retrieve the category by his path.
        """
        return get_category_or_404(path)

    def items(self, obj):
        """
        Items are the published entries of the category.
        """
        return obj.entries_published()[:self.limit]

    def link(self, obj):
        """
        URL of the category.
        """
        return obj.get_absolute_url()

    def get_title(self, obj):
        """
        Title of the feed.
        """
        return _('Entries for the category %(object)s') % {'object': obj.title}

    def description(self, obj):
        """
        Description of the feed.
        """
        return (obj.description or
                _('The last entries categorized under %(object)s') % {
                    'object': obj.title})


class AuthorEntries(EntryFeed):
    """
    Feed filtered by an author.
    """

    def get_object(self, request, username):
        """
        Retrieve the author by his username.
        """
        return get_object_or_404(Author, **{Author.USERNAME_FIELD: username})

    def items(self, obj):
        """
        Items are the published entries of the author.
        """
        return obj.entries_published()[:self.limit]

    def link(self, obj):
        """
        URL of the author.
        """
        return obj.get_absolute_url()

    def get_title(self, obj):
        """
        Title of the feed.
        """
        return _('Entries for the author %(object)s') % {
            'object': smart_str(obj.__str__())}

    def description(self, obj):
        """
        Description of the feed.
        """
        return _('The last entries by %(object)s') % {
            'object': smart_str(obj.__str__())}


class TagEntries(EntryFeed):
    """
    Feed filtered by a tag.
    """

    def get_object(self, request, tag):
        """
        Retrieve the tag by his name.
        """
        return get_object_or_404(Tag, name=tag)

    def items(self, obj):
        """
        Items are the published entries of the tag.
        """
        return TaggedItem.objects.get_by_model(
            Entry.published.all(), obj)[:self.limit]

    def link(self, obj):
        """
        URL of the tag.
        """
        return reverse('zinnia:tag_detail', args=[obj.name])

    def get_title(self, obj):
        """
        Title of the feed.
        """
        return _('Entries for the tag %(object)s') % {'object': obj.name}

    def description(self, obj):
        """
        Description of the feed.
        """
        return _('The last entries tagged with %(object)s') % {
            'object': obj.name}


class SearchEntries(EntryFeed):
    """
    Feed filtered by a search pattern.
    """

    def get_object(self, request):
        """
        The GET parameter 'pattern' is the object.
        """
        pattern = request.GET.get('pattern', '')
        if len(pattern) < 3:
            raise ObjectDoesNotExist
        return pattern

    def items(self, obj):
        """
        Items are the published entries founds.
        """
        return Entry.published.search(obj)[:self.limit]

    def link(self, obj):
        """
        URL of the search request.
        """
        return '%s?pattern=%s' % (reverse('zinnia:entry_search'), obj)

    def get_title(self, obj):
        """
        Title of the feed.
        """
        return _("Search results for '%(pattern)s'") % {'pattern': obj}

    def description(self, obj):
        """
        Description of the feed.
        """
        return _("The last entries containing the pattern '%(pattern)s'") % {
            'pattern': obj}


class DiscussionFeed(ZinniaFeed):
    """
    Base class for discussion Feed.
    """
    title_template = 'feeds/discussion_title.html'
    description_template = 'feeds/discussion_description.html'

    def item_pubdate(self, item):
        """
        Publication date of a discussion.
        """
        return item.submit_date

    def item_link(self, item):
        """
        URL of the discussion item.
        """
        return item.get_absolute_url()

    def item_author_name(self, item):
        """
        Author of the discussion item.
        """
        return item.name

    def item_author_email(self, item):
        """
        Author's email of the discussion item.
        """
        return item.email

    def item_author_link(self, item):
        """
        Author's URL of the discussion.
        """
        return item.url


class LastDiscussions(DiscussionFeed):
    """
    Feed for the last discussions.
    """

    def items(self):
        """
        Items are the discussions on the entries.
        """
        content_type = ContentType.objects.get_for_model(Entry)
        return comments.get_model().objects.filter(
            content_type=content_type, is_public=True).order_by(
            '-submit_date')[:self.limit]

    def link(self):
        """
        URL of last discussions.
        """
        return reverse('zinnia:entry_archive_index')

    def get_title(self, obj):
        """
        Title of the feed.
        """
        return _('Last discussions')

    def description(self):
        """
        Description of the feed.
        """
        return _('The last discussions on the site %(object)s') % {
            'object': self.site.name}


class EntryDiscussions(DiscussionFeed):
    """
    Feed for discussions on an entry.
    """

    def get_object(self, request, year, month, day, slug):
        """
        Retrieve the discussions by entry's slug.
        """
        return get_object_or_404(Entry, slug=slug,
                                 publication_date__year=year,
                                 publication_date__month=month,
                                 publication_date__day=day)

    def items(self, obj):
        """
        Items are the discussions on the entry.
        """
        return obj.discussions[:self.limit]

    def link(self, obj):
        """
        URL of the entry.
        """
        return obj.get_absolute_url()

    def get_title(self, obj):
        """
        Title of the feed.
        """
        return _('Discussions on %(object)s') % {'object': obj.title}

    def description(self, obj):
        """
        Description of the feed.
        """
        return _('The last discussions on the entry %(object)s') % {
            'object': obj.title}


class EntryComments(EntryDiscussions):
    """
    Feed for comments on an entry.
    """
    title_template = 'feeds/comment_title.html'
    description_template = 'feeds/comment_description.html'

    def items(self, obj):
        """
        Items are the comments on the entry.
        """
        return obj.comments[:self.limit]

    def item_link(self, item):
        """
        URL of the comment.
        """
        return item.get_absolute_url('#comment-%(id)s-by-'
                                     ) + slugify(item.user_name)

    def get_title(self, obj):
        """
        Title of the feed.
        """
        return _('Comments on %(object)s') % {'object': obj.title}

    def description(self, obj):
        """
        Description of the feed.
        """
        return _('The last comments on the entry %(object)s') % {
            'object': obj.title}

    def item_enclosure_url(self, item):
        """
        Return a gravatar image for enclosure.
        """
        return get_gravatar(item.email)

    def item_enclosure_length(self, item):
        """
        Hardcoded enclosure length.
        """
        return '100000'

    def item_enclosure_mime_type(self, item):
        """
        Hardcoded enclosure mimetype.
        """
        return 'image/jpeg'


class EntryPingbacks(EntryDiscussions):
    """
    Feed for pingbacks on an entry.
    """
    title_template = 'feeds/pingback_title.html'
    description_template = 'feeds/pingback_description.html'

    def items(self, obj):
        """
        Items are the pingbacks on the entry.
        """
        return obj.pingbacks[:self.limit]

    def item_link(self, item):
        """
        URL of the pingback.
        """
        return item.get_absolute_url('#pingback-%(id)s')

    def get_title(self, obj):
        """
        Title of the feed.
        """
        return _('Pingbacks on %(object)s') % {'object': obj.title}

    def description(self, obj):
        """
        Description of the feed.
        """
        return _('The last pingbacks on the entry %(object)s') % {
            'object': obj.title}


class EntryTrackbacks(EntryDiscussions):
    """
    Feed for trackbacks on an entry.
    """
    title_template = 'feeds/trackback_title.html'
    description_template = 'feeds/trackback_description.html'

    def items(self, obj):
        """
        Items are the trackbacks on the entry.
        """
        return obj.trackbacks[:self.limit]

    def item_link(self, item):
        """
        URL of the trackback.
        """
        return item.get_absolute_url('#trackback-%(id)s')

    def get_title(self, obj):
        """
        Title of the feed.
        """
        return _('Trackbacks on %(object)s') % {'object': obj.title}

    def description(self, obj):
        """
        Description of the feed.
        """
        return _('The last trackbacks on the entry %(object)s') % {
            'object': obj.title}

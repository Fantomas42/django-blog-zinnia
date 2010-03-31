"""Feeds for Zinnia"""
from datetime import datetime
from sgmllib import SGMLParser

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.comments.models import Comment
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.syndication.feeds import Feed, FeedDoesNotExist

from tagging.models import Tag
from tagging.models import TaggedItem

from zinnia.models import Entry
from zinnia.models import Category
from zinnia.managers import entries_published


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
    copyright = 'Copyright (c) 2005-%i, Julien Fache' % datetime.now().year

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
        parser = ImgParser()
        parser.feed(item.content)
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
    title = _('%s - News') % current_site.name
    description = _('The last news for the site %s') % current_site.domain

    def link(self):
        return reverse('zinnia_entry_archive_index')

    def items(self):
        return Entry.published.all()


class CategoryEntries(EntryFeed):
    """Feed filtered by a category"""

    def get_object(self, bits):
        if len(bits) != 1:
            raise FeedDoesNotExist
        return Category.objects.get(slug__iexact=bits[0])

    def items(self, obj):
        return obj.entries_published_set()

    def link(self, obj):
        return obj.get_absolute_url()

    def title(self, obj):
        return _('Entries for the category %s') % obj.title

    def description(self, obj):
        return _('The last news for the category %s') % obj.title


class AuthorEntries(EntryFeed):
    """Feed filtered by an author"""

    def get_object(self, bits):
        if len(bits) != 1:
            raise FeedDoesNotExist
        return User.objects.get(username__iexact=bits[0])

    def items(self, obj):
        return entries_published(obj.entry_set)

    def link(self, obj):
        return reverse('zinnia_author_detail', args=[obj.username])

    def title(self, obj):
        return _('Entries for author %s') % obj.username

    def description(self, obj):
        return _('The last news by %s') % obj.username


class TagEntries(EntryFeed):
    """Feed filtered by a tag"""

    def get_object(self, bits):
        if len(bits) != 1:
            raise FeedDoesNotExist
        return Tag.objects.get(name=bits[0])

    def items(self, obj):
        return TaggedItem.objects.get_by_model(Entry.published.all(), obj)

    def link(self, obj):
        return reverse('zinnia_tag_detail', args=[obj.name])

    def title(self, obj):
        return _('Entries for the tag %s') % obj.name

    def description(self, obj):
        return _('The last news for the tag %s') % obj.name


class SearchEntries(EntryFeed):
    """Feed filtered by search pattern"""

    def get_object(self, bits):
        if len(bits) != 1:
            raise FeedDoesNotExist
        return bits[0]

    def items(self, obj):
        return Entry.published.search(obj)

    def link(self, obj):
        return '%s?pattern=%s' % (reverse('zinnia_entry_search'), obj)

    def title(self, obj):
        return _("Results of the search for %s") % obj

    def description(self, obj):
        return _("The news containing the pattern %s") % obj


class CommentEntries(Feed):
    """Feed for comments in an entry"""

    def get_object(self, bits):
        if len(bits) != 1:
            raise FeedDoesNotExist
        return Entry.objects.get(slug__iexact=bits[0])

    def items(self, obj):
        return Comment.objects.for_model(obj).order_by('-submit_date')[:10]

    def item_pubdate(self, item):
        return item.submit_date

    def link(self, obj):
        return obj.get_absolute_url()

    def title(self, obj):
        return _('Comments on %s') % obj.title

    def description(self, obj):
        return _('The last comments for the news %s') % obj.title


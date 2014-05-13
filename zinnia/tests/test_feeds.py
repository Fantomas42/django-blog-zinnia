"""Test cases for Zinnia's feeds"""
try:
    from urllib.parse import urljoin
except ImportError:  # Python 2
    from urlparse import urljoin

from django.test import TestCase
from django.utils import timezone

try:
    import django_comments as comments
except ImportError:
    from django.contrib import comments

from django.contrib.sites.models import Site
from django.utils.translation import activate
from django.utils.translation import deactivate
from django.test.utils import override_settings
from django.core.files.base import ContentFile
from django.utils.feedgenerator import Atom1Feed
from django.utils.feedgenerator import DefaultFeed
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.tests.utils import skipIfCustomUser

from tagging.models import Tag

from zinnia.managers import HIDDEN
from zinnia.managers import PUBLISHED
from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.tests.utils import datetime
from zinnia.tests.utils import urlEqual
from zinnia.models.category import Category
from zinnia.flags import PINGBACK, TRACKBACK
from zinnia import feeds
from zinnia.feeds import EntryFeed
from zinnia.feeds import ZinniaFeed
from zinnia.feeds import LatestEntries
from zinnia.feeds import CategoryEntries
from zinnia.feeds import AuthorEntries
from zinnia.feeds import TagEntries
from zinnia.feeds import SearchEntries
from zinnia.feeds import EntryDiscussions
from zinnia.feeds import EntryComments
from zinnia.feeds import EntryPingbacks
from zinnia.feeds import EntryTrackbacks
from zinnia.feeds import LatestDiscussions
from zinnia.signals import disconnect_entry_signals
from zinnia.signals import disconnect_discussion_signals


@skipIfCustomUser
class FeedsTestCase(TestCase):
    """Test cases for the Feed classes provided"""
    urls = 'zinnia.tests.implementations.urls.default'

    def setUp(self):
        disconnect_entry_signals()
        disconnect_discussion_signals()
        activate('en')
        self.site = Site.objects.get_current()
        self.author = Author.objects.create(username='admin',
                                            first_name='Root',
                                            last_name='Bloody',
                                            email='admin@example.com')
        self.category = Category.objects.create(title='Tests', slug='tests')
        self.entry_ct_id = ContentType.objects.get_for_model(Entry).pk

    def tearDown(self):
        deactivate()

    def create_published_entry(self):
        params = {'title': 'My test entry',
                  'content': 'My test content with image '
                  '<img src="/image.jpg" />',
                  'slug': 'my-test-entry',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 1, 1, 12),
                  'status': PUBLISHED}
        entry = Entry.objects.create(**params)
        entry.sites.add(self.site)
        entry.categories.add(self.category)
        entry.authors.add(self.author)
        return entry

    def create_discussions(self, entry):
        comment = comments.get_model().objects.create(
            comment='My Comment',
            user=self.author,
            user_name='admin',
            content_object=entry,
            site=self.site,
            submit_date=timezone.now())
        pingback = comments.get_model().objects.create(
            comment='My Pingback',
            user=self.author,
            content_object=entry,
            site=self.site,
            submit_date=timezone.now())
        pingback.flags.create(user=self.author, flag=PINGBACK)
        trackback = comments.get_model().objects.create(
            comment='My Trackback',
            user=self.author,
            content_object=entry,
            site=self.site,
            submit_date=timezone.now())
        trackback.flags.create(user=self.author, flag=TRACKBACK)
        return [comment, pingback, trackback]

    def test_entry_feed(self):
        entry = self.create_published_entry()
        feed = EntryFeed()
        self.assertEqual(feed.item_pubdate(entry), entry.creation_date)
        self.assertEqual(feed.item_categories(entry), [self.category.title])
        self.assertEqual(feed.item_author_name(entry),
                         self.author.__str__())
        self.assertEqual(feed.item_author_email(entry), self.author.email)
        self.assertEqual(
            feed.item_author_link(entry),
            'http://example.com/authors/%s/' % self.author.username)
        # Test a NoReverseMatch for item_author_link
        self.author.username = '[]'
        self.author.save()
        feed.item_author_name(entry)
        self.assertEqual(feed.item_author_link(entry), 'http://example.com')

    def test_entry_feed_enclosure(self):
        entry = self.create_published_entry()
        feed = EntryFeed()
        self.assertEqual(
            feed.item_enclosure_url(entry), 'http://example.com/image.jpg')
        self.assertEqual(feed.item_enclosure_length(entry), '100000')
        self.assertEqual(feed.item_enclosure_mime_type(entry), 'image/jpeg')
        entry.content = 'My test content with image <img src="image.jpg" />'
        entry.save()
        self.assertEqual(
            feed.item_enclosure_url(entry), 'http://example.com/image.jpg')
        self.assertEqual(feed.item_enclosure_length(entry), '100000')
        self.assertEqual(feed.item_enclosure_mime_type(entry), 'image/jpeg')
        entry.content = 'My test content with image ' \
                        '<img src="http://test.com/image.jpg" />'
        entry.save()
        self.assertEqual(
            feed.item_enclosure_url(entry), 'http://test.com/image.jpg')
        self.assertEqual(feed.item_enclosure_length(entry), '100000')
        self.assertEqual(feed.item_enclosure_mime_type(entry), 'image/jpeg')
        path = default_storage.save('enclosure.png', ContentFile('Content'))
        entry.image = path
        entry.save()
        self.assertEqual(feed.item_enclosure_url(entry),
                         urljoin('http://example.com', entry.image.url))
        self.assertEqual(feed.item_enclosure_length(entry), '7')
        self.assertEqual(feed.item_enclosure_mime_type(entry), 'image/png')
        default_storage.delete(path)
        entry.image = 'invalid_image_without_extension'
        entry.save()
        self.assertEqual(feed.item_enclosure_url(entry),
                         urljoin('http://example.com', entry.image.url))
        self.assertEqual(feed.item_enclosure_length(entry), '100000')
        self.assertEqual(feed.item_enclosure_mime_type(entry), 'image/jpeg')

    def test_entry_feed_enclosure_issue_134(self):
        entry = self.create_published_entry()
        feed = EntryFeed()
        entry.content = 'My test content with image <img xsrc="image.jpg" />'
        entry.save()
        self.assertEqual(
            feed.item_enclosure_url(entry), None)

    def test_latest_entries(self):
        self.create_published_entry()
        feed = LatestEntries()
        self.assertEqual(feed.link(), '/')
        self.assertEqual(len(feed.items()), 1)
        self.assertEqual(feed.get_title(None), 'Latest entries')
        self.assertEqual(
            feed.description(),
            'The latest entries for the site example.com')

    def test_category_entries(self):
        self.create_published_entry()
        feed = CategoryEntries()
        self.assertEqual(feed.get_object('request', '/tests/'), self.category)
        self.assertEqual(len(feed.items(self.category)), 1)
        self.assertEqual(feed.link(self.category), '/categories/tests/')
        self.assertEqual(
            feed.get_title(self.category),
            'Entries for the category %s' % self.category.title)
        self.assertEqual(
            feed.description(self.category),
            'The latest entries for the category %s' % self.category.title)

    def test_author_entries(self):
        self.create_published_entry()
        feed = AuthorEntries()
        self.assertEqual(feed.get_object('request', 'admin'), self.author)
        self.assertEqual(len(feed.items(self.author)), 1)
        self.assertEqual(feed.link(self.author), '/authors/admin/')
        self.assertEqual(feed.get_title(self.author),
                         'Entries for author %s' %
                         self.author.__str__())
        self.assertEqual(feed.description(self.author),
                         'The latest entries by %s' %
                         self.author.__str__())

    def test_tag_entries(self):
        self.create_published_entry()
        feed = TagEntries()
        tag = Tag(name='tests')
        self.assertEqual(feed.get_object('request', 'tests').name, 'tests')
        self.assertEqual(len(feed.items('tests')), 1)
        self.assertEqual(feed.link(tag), '/tags/tests/')
        self.assertEqual(feed.get_title(tag),
                         'Entries for the tag %s' % tag.name)
        self.assertEqual(feed.description(tag),
                         'The latest entries for the tag %s' % tag.name)

    def test_search_entries(self):
        class FakeRequest:
            def __init__(self, val):
                self.GET = {'pattern': val}
        self.create_published_entry()
        feed = SearchEntries()
        self.assertRaises(ObjectDoesNotExist,
                          feed.get_object, FakeRequest('te'))
        self.assertEqual(feed.get_object(FakeRequest('test')), 'test')
        self.assertEqual(len(feed.items('test')), 1)
        self.assertEqual(feed.link('test'), '/search/?pattern=test')
        self.assertEqual(feed.get_title('test'),
                         "Results of the search for '%s'" % 'test')
        self.assertEqual(
            feed.description('test'),
            "The entries containing the pattern '%s'" % 'test')

    def test_latest_discussions(self):
        entry = self.create_published_entry()
        self.create_discussions(entry)
        feed = LatestDiscussions()
        self.assertEqual(feed.link(), '/')
        self.assertEqual(len(feed.items()), 3)
        self.assertEqual(feed.get_title(None), 'Latest discussions')
        self.assertEqual(
            feed.description(),
            'The latest discussions for the site example.com')

    def test_entry_discussions(self):
        entry = self.create_published_entry()
        comments = self.create_discussions(entry)
        feed = EntryDiscussions()
        self.assertEqual(feed.get_object(
            'request', 2010, 1, 1, entry.slug), entry)
        self.assertEqual(feed.link(entry), '/2010/01/01/my-test-entry/')
        self.assertEqual(len(feed.items(entry)), 3)
        self.assertEqual(feed.item_pubdate(comments[0]),
                         comments[0].submit_date)
        self.assertEqual(feed.item_link(comments[0]),
                         '/comments/cr/%i/1/#c1' % self.entry_ct_id)
        self.assertEqual(feed.item_author_name(comments[0]),
                         self.author.__str__())
        self.assertEqual(feed.item_author_email(comments[0]),
                         'admin@example.com')
        self.assertEqual(feed.item_author_link(comments[0]), '')
        self.assertEqual(feed.get_title(entry),
                         'Discussions on %s' % entry.title)
        self.assertEqual(
            feed.description(entry),
            'The latest discussions for the entry %s' % entry.title)

    def test_feed_for_hidden_entry_issue_277(self):
        entry = self.create_published_entry()
        entry.status = HIDDEN
        entry.save()
        feed = EntryDiscussions()
        self.assertEqual(feed.get_object(
            'request', 2010, 1, 1, entry.slug), entry)

    @override_settings(USE_TZ=False)
    def test_feed_discussions_no_timezone_issue_277(self):
        entry = self.create_published_entry()
        entry.creation_date = datetime(2014, 1, 1, 23)
        entry.save()
        feed = EntryDiscussions()
        self.assertEqual(feed.get_object(
            'request', 2014, 1, 1, entry.slug), entry)

    @override_settings(USE_TZ=True, TIME_ZONE='Europe/Paris')
    def test_feed_discussions_with_timezone_issue_277(self):
        entry = self.create_published_entry()
        entry.creation_date = datetime(2014, 1, 1, 23)
        entry.save()
        feed = EntryDiscussions()
        self.assertEqual(feed.get_object(
            'request', 2014, 1, 2, entry.slug), entry)

    def test_entry_comments(self):
        entry = self.create_published_entry()
        comments = self.create_discussions(entry)
        feed = EntryComments()
        self.assertEqual(list(feed.items(entry)), [comments[0]])
        self.assertEqual(feed.item_link(comments[0]),
                         '/comments/cr/%i/1/#comment-1-by-admin' %
                         self.entry_ct_id)
        self.assertEqual(feed.get_title(entry),
                         'Comments on %s' % entry.title)
        self.assertEqual(
            feed.description(entry),
            'The latest comments for the entry %s' % entry.title)
        self.assertTrue(urlEqual(
            feed.item_enclosure_url(comments[0]),
            'http://www.gravatar.com/avatar/e64c7d89f26b'
            'd1972efa854d13d7dd61?s=80&amp;r=g'))
        self.assertEqual(feed.item_enclosure_length(entry), '100000')
        self.assertEqual(feed.item_enclosure_mime_type(entry), 'image/jpeg')

    def test_entry_pingbacks(self):
        entry = self.create_published_entry()
        comments = self.create_discussions(entry)
        feed = EntryPingbacks()
        self.assertEqual(list(feed.items(entry)), [comments[1]])
        self.assertEqual(feed.item_link(comments[1]),
                         '/comments/cr/%i/1/#pingback-2' % self.entry_ct_id)
        self.assertEqual(feed.get_title(entry),
                         'Pingbacks on %s' % entry.title)
        self.assertEqual(
            feed.description(entry),
            'The latest pingbacks for the entry %s' % entry.title)

    def test_entry_trackbacks(self):
        entry = self.create_published_entry()
        comments = self.create_discussions(entry)
        feed = EntryTrackbacks()
        self.assertEqual(list(feed.items(entry)), [comments[2]])
        self.assertEqual(feed.item_link(comments[2]),
                         '/comments/cr/%i/1/#trackback-3' % self.entry_ct_id)
        self.assertEqual(feed.get_title(entry),
                         'Trackbacks on %s' % entry.title)
        self.assertEqual(
            feed.description(entry),
            'The latest trackbacks for the entry %s' % entry.title)

    def test_entry_feed_no_authors(self):
        entry = self.create_published_entry()
        entry.authors.clear()
        feed = EntryFeed()
        self.assertEqual(feed.item_author_name(entry), None)

    def test_entry_feed_rss_or_atom(self):
        original_feeds_format = feeds.FEEDS_FORMAT
        feeds.FEEDS_FORMAT = ''
        feed = LatestEntries()
        self.assertEqual(feed.feed_type, DefaultFeed)
        feeds.FEEDS_FORMAT = 'atom'
        feed = LatestEntries()
        self.assertEqual(feed.feed_type, Atom1Feed)
        self.assertEqual(feed.subtitle, feed.description)
        feeds.FEEDS_FORMAT = original_feeds_format

    def test_title_with_sitename_implementation(self):
        feed = ZinniaFeed()
        self.assertRaises(NotImplementedError, feed.title)
        feed = LatestEntries()
        self.assertEqual(feed.title(), 'example.com - Latest entries')

    def test_discussion_feed_with_same_slugs(self):
        """
        https://github.com/Fantomas42/django-blog-zinnia/issues/104

        OK, Here I will reproduce the original case: getting a discussion
        type feed, with a same slug.

        The correction of this case, will need some changes in the
        get_object method.
        """
        entry = self.create_published_entry()

        feed = EntryDiscussions()
        self.assertEqual(feed.get_object(
            'request', 2010, 1, 1, entry.slug), entry)

        params = {'title': 'My test entry, part II',
                  'content': 'My content ',
                  'slug': 'my-test-entry',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 2, 1, 12),
                  'status': PUBLISHED}
        entry_same_slug = Entry.objects.create(**params)
        entry_same_slug.sites.add(self.site)
        entry_same_slug.authors.add(self.author)

        self.assertEqual(feed.get_object(
            'request', 2010, 2, 1, entry_same_slug.slug), entry_same_slug)

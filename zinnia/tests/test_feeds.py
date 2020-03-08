# coding=utf-8
"""Test cases for Zinnia's feeds"""
from urllib.parse import urljoin

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone
from django.utils.encoding import smart_str
from django.utils.feedgenerator import Atom1Feed
from django.utils.feedgenerator import DefaultFeed
from django.utils.translation import activate
from django.utils.translation import deactivate

import django_comments as comments

from tagging.models import Tag

from zinnia.feeds import AuthorEntries
from zinnia.feeds import CategoryEntries
from zinnia.feeds import EntryComments
from zinnia.feeds import EntryDiscussions
from zinnia.feeds import EntryFeed
from zinnia.feeds import EntryPingbacks
from zinnia.feeds import EntryTrackbacks
from zinnia.feeds import LastDiscussions
from zinnia.feeds import LastEntries
from zinnia.feeds import SearchEntries
from zinnia.feeds import TagEntries
from zinnia.feeds import ZinniaFeed
from zinnia.flags import PINGBACK, TRACKBACK
from zinnia.managers import HIDDEN
from zinnia.managers import PUBLISHED
from zinnia.models.author import Author
from zinnia.models.category import Category
from zinnia.models.entry import Entry
from zinnia.signals import disconnect_discussion_signals
from zinnia.signals import disconnect_entry_signals
from zinnia.tests.utils import datetime
from zinnia.tests.utils import skip_if_custom_user
from zinnia.tests.utils import url_equal


@skip_if_custom_user
@override_settings(
    ROOT_URLCONF='zinnia.tests.implementations.urls.default'
)
class FeedsTestCase(TestCase):
    """Test cases for the Feed classes provided"""

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
                  'publication_date': datetime(2010, 1, 1, 12),
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
        self.assertEqual(feed.item_pubdate(entry), entry.publication_date)
        self.assertEqual(feed.item_updateddate(entry), entry.last_update)
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

    def test_entry_feed_enclosure_replace_https_in_rss(self):
        entry = self.create_published_entry()
        feed = EntryFeed()
        entry.content = 'My test content with image in https ' \
                        '<img src="https://test.com/image.jpg" />'
        entry.save()
        self.assertEqual(
            feed.item_enclosure_url(entry), 'http://test.com/image.jpg')
        feed.protocol = 'https'
        entry.content = 'My test content with image <img src="image.jpg" />'
        entry.save()
        self.assertEqual(
            feed.item_enclosure_url(entry), 'http://example.com/image.jpg')
        path = default_storage.save('enclosure.png', ContentFile('Content'))
        entry.image = path
        entry.save()
        self.assertEqual(feed.item_enclosure_url(entry),
                         urljoin('http://example.com', entry.image.url))
        original_feed_format = LastEntries.feed_format
        LastEntries.feed_format = 'atom'
        feed = LastEntries()
        feed.protocol = 'https'
        self.assertEqual(feed.item_enclosure_url(entry),
                         urljoin('https://example.com', entry.image.url))
        LastEntries.feed_format = original_feed_format
        default_storage.delete(path)

    def test_entry_feed_enclosure_without_image(self):
        entry = self.create_published_entry()
        feed = EntryFeed()
        entry.content = 'My test content without image '
        entry.save()
        self.assertEqual(
            feed.item_enclosure_url(entry), None)

    def test_entry_feed_enclosure_issue_134(self):
        entry = self.create_published_entry()
        feed = EntryFeed()
        entry.content = 'My test content with image <img xsrc="image.jpg" />'
        entry.save()
        self.assertEqual(
            feed.item_enclosure_url(entry), None)

    def test_last_entries(self):
        self.create_published_entry()
        feed = LastEntries()
        self.assertEqual(feed.link(), '/')
        self.assertEqual(len(feed.items()), 1)
        self.assertEqual(feed.get_title(None), 'Last entries')
        self.assertEqual(
            feed.description(),
            'The last entries on the site example.com')

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
            'The last entries categorized under %s' % self.category.title)
        self.category.description = 'Category description'
        self.assertEqual(feed.description(self.category),
                         'Category description')

    def test_category_title_non_ascii(self):
        self.create_published_entry()
        self.category.title = smart_str('Catégorie')
        self.category.save()
        feed = CategoryEntries()
        self.assertEqual(feed.get_title(self.category),
                         'Entries for the category %s' % self.category.title)
        self.assertEqual(
            feed.description(self.category),
            'The last entries categorized under %s' % self.category.title)

    def test_author_entries(self):
        self.create_published_entry()
        feed = AuthorEntries()
        self.assertEqual(feed.get_object('request', 'admin'), self.author)
        self.assertEqual(len(feed.items(self.author)), 1)
        self.assertEqual(feed.link(self.author), '/authors/admin/')
        self.assertEqual(feed.get_title(self.author),
                         'Entries for the author %s' %
                         self.author.__str__())
        self.assertEqual(feed.description(self.author),
                         'The last entries by %s' %
                         self.author.__str__())

    def test_author_title_non_ascii(self):
        self.author.first_name = smart_str('Léon')
        self.author.last_name = 'Bloom'
        self.author.save()
        self.create_published_entry()
        feed = AuthorEntries()
        self.assertEqual(feed.get_title(self.author),
                         smart_str('Entries for the author %s' %
                                   self.author.__str__()))
        self.assertEqual(feed.description(self.author),
                         smart_str('The last entries by %s' %
                                   self.author.__str__()))

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
                         'The last entries tagged with %s' % tag.name)

    def test_tag_title_non_ascii(self):
        entry = self.create_published_entry()
        tag_unicode = smart_str('accentué')
        entry.tags = tag_unicode
        entry.save()
        feed = TagEntries()
        tag = Tag(name=tag_unicode)
        self.assertEqual(feed.get_title(tag),
                         'Entries for the tag %s' % tag_unicode)
        self.assertEqual(feed.description(tag),
                         'The last entries tagged with %s' % tag_unicode)

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
                         "Search results for '%s'" % 'test')
        self.assertEqual(
            feed.description('test'),
            "The last entries containing the pattern '%s'" % 'test')

    def test_last_discussions(self):
        entry = self.create_published_entry()
        self.create_discussions(entry)
        feed = LastDiscussions()
        self.assertEqual(feed.link(), '/')
        self.assertEqual(len(feed.items()), 3)
        self.assertEqual(feed.get_title(None), 'Last discussions')
        self.assertEqual(
            feed.description(),
            'The last discussions on the site example.com')

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
                         '/comments/cr/%i/%i/#c%i' %
                         (self.entry_ct_id, entry.pk, comments[0].pk))
        self.assertEqual(feed.item_author_name(comments[0]),
                         self.author.get_full_name())
        self.assertEqual(feed.item_author_email(comments[0]),
                         'admin@example.com')
        self.assertEqual(feed.item_author_link(comments[0]), '')
        self.assertEqual(feed.get_title(entry),
                         'Discussions on %s' % entry.title)
        self.assertEqual(
            feed.description(entry),
            'The last discussions on the entry %s' % entry.title)

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
        entry.publication_date = datetime(2014, 1, 1, 23)
        entry.save()
        feed = EntryDiscussions()
        self.assertEqual(feed.get_object(
            'request', 2014, 1, 1, entry.slug), entry)

    @override_settings(USE_TZ=True, TIME_ZONE='Europe/Paris')
    def test_feed_discussions_with_timezone_issue_277(self):
        entry = self.create_published_entry()
        entry.publication_date = datetime(2014, 1, 1, 23)
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
                         '/comments/cr/%i/%i/#comment-%i-by-admin' %
                         (self.entry_ct_id, entry.pk, comments[0].pk))
        self.assertEqual(feed.get_title(entry),
                         'Comments on %s' % entry.title)
        self.assertEqual(
            feed.description(entry),
            'The last comments on the entry %s' % entry.title)
        self.assertTrue(url_equal(
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
                         '/comments/cr/%i/%i/#pingback-%i' %
                         (self.entry_ct_id, entry.pk, comments[1].pk))
        self.assertEqual(feed.get_title(entry),
                         'Pingbacks on %s' % entry.title)
        self.assertEqual(
            feed.description(entry),
            'The last pingbacks on the entry %s' % entry.title)

    def test_entry_trackbacks(self):
        entry = self.create_published_entry()
        comments = self.create_discussions(entry)
        feed = EntryTrackbacks()
        self.assertEqual(list(feed.items(entry)), [comments[2]])
        self.assertEqual(feed.item_link(comments[2]),
                         '/comments/cr/%i/%i/#trackback-%i' %
                         (self.entry_ct_id, entry.pk, comments[2].pk))
        self.assertEqual(feed.get_title(entry),
                         'Trackbacks on %s' % entry.title)
        self.assertEqual(
            feed.description(entry),
            'The last trackbacks on the entry %s' % entry.title)

    def test_entry_feed_no_authors(self):
        entry = self.create_published_entry()
        entry.authors.clear()
        feed = EntryFeed()
        self.assertEqual(feed.item_author_name(entry), None)

    def test_entry_feed_rss_or_atom(self):
        original_feed_format = LastEntries.feed_format
        LastEntries.feed_format = ''
        feed = LastEntries()
        self.assertEqual(feed.feed_type, DefaultFeed)
        LastEntries.feed_format = 'atom'
        feed = LastEntries()
        self.assertEqual(feed.feed_type, Atom1Feed)
        self.assertEqual(feed.subtitle, feed.description)
        LastEntries.feed_format = original_feed_format

    def test_title_with_sitename_implementation(self):
        feed = ZinniaFeed()
        self.assertRaises(NotImplementedError, feed.title)
        feed = LastEntries()
        self.assertEqual(feed.title(), 'example.com - Last entries')

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
                  'publication_date': datetime(2010, 2, 1, 12),
                  'status': PUBLISHED}
        entry_same_slug = Entry.objects.create(**params)
        entry_same_slug.sites.add(self.site)
        entry_same_slug.authors.add(self.author)

        self.assertEqual(feed.get_object(
            'request', 2010, 2, 1, entry_same_slug.slug), entry_same_slug)

"""Test cases for Zinnia's Entry"""
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib import comments
from django.utils.unittest import skipUnless
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils.translation import activate
from django.utils.translation import deactivate
from django.test.utils import override_settings
from django.contrib.comments.models import CommentFlag
from django.contrib.auth.tests.utils import skipIfCustomUser

from zinnia.managers import PUBLISHED
from zinnia.models_bases import entry
from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.flags import PINGBACK, TRACKBACK
from zinnia.tests.utils import datetime
from zinnia.tests.utils import is_lib_available
from zinnia import url_shortener as shortener_settings


class EntryTestCase(TestCase):

    def setUp(self):
        params = {'title': 'My entry',
                  'content': 'My content',
                  'slug': 'my-entry'}
        self.entry = Entry.objects.create(**params)

    @skipIfCustomUser
    def test_discussions(self):
        site = Site.objects.get_current()
        self.assertEquals(self.entry.discussions.count(), 0)
        self.assertEquals(self.entry.comments.count(), 0)
        self.assertEquals(self.entry.pingbacks.count(), 0)
        self.assertEquals(self.entry.trackbacks.count(), 0)

        comments.get_model().objects.create(
            comment='My Comment 1',
            content_object=self.entry,
            submit_date=timezone.now(),
            site=site)
        self.assertEquals(self.entry.discussions.count(), 1)
        self.assertEquals(self.entry.comments.count(), 1)
        self.assertEquals(self.entry.pingbacks.count(), 0)
        self.assertEquals(self.entry.trackbacks.count(), 0)

        comments.get_model().objects.create(
            comment='My Comment 2',
            content_object=self.entry,
            submit_date=timezone.now(),
            site=site, is_public=False)
        self.assertEquals(self.entry.discussions.count(), 1)
        self.assertEquals(self.entry.comments.count(), 1)
        self.assertEquals(self.entry.pingbacks.count(), 0)
        self.assertEquals(self.entry.trackbacks.count(), 0)

        author = Author.objects.create_user(username='webmaster',
                                            email='webmaster@example.com')

        comment = comments.get_model().objects.create(
            comment='My Comment 3',
            content_object=self.entry,
            submit_date=timezone.now(),
            site=Site.objects.create(domain='http://toto.com',
                                     name='Toto.com'))
        comment.flags.create(user=author, flag=CommentFlag.MODERATOR_APPROVAL)
        self.assertEquals(self.entry.discussions.count(), 2)
        self.assertEquals(self.entry.comments.count(), 2)
        self.assertEquals(self.entry.pingbacks.count(), 0)
        self.assertEquals(self.entry.trackbacks.count(), 0)

        comment = comments.get_model().objects.create(
            comment='My Pingback 1',
            content_object=self.entry,
            submit_date=timezone.now(),
            site=site)
        comment.flags.create(user=author, flag=PINGBACK)
        self.assertEquals(self.entry.discussions.count(), 3)
        self.assertEquals(self.entry.comments.count(), 2)
        self.assertEquals(self.entry.pingbacks.count(), 1)
        self.assertEquals(self.entry.trackbacks.count(), 0)

        comment = comments.get_model().objects.create(
            comment='My Trackback 1',
            content_object=self.entry,
            submit_date=timezone.now(),
            site=site)
        comment.flags.create(user=author, flag=TRACKBACK)
        self.assertEquals(self.entry.discussions.count(), 4)
        self.assertEquals(self.entry.comments.count(), 2)
        self.assertEquals(self.entry.pingbacks.count(), 1)
        self.assertEquals(self.entry.trackbacks.count(), 1)

    def test_str(self):
        activate('en')
        self.assertEquals(str(self.entry), 'My entry: draft')
        deactivate()

    def test_word_count(self):
        self.assertEquals(self.entry.word_count, 2)

    def test_comments_are_open(self):
        original_auto_close = entry.AUTO_CLOSE_COMMENTS_AFTER
        entry.AUTO_CLOSE_COMMENTS_AFTER = None
        self.assertEquals(self.entry.comments_are_open, True)
        entry.AUTO_CLOSE_COMMENTS_AFTER = -1
        self.assertEquals(self.entry.comments_are_open, True)
        entry.AUTO_CLOSE_COMMENTS_AFTER = 0
        self.assertEquals(self.entry.comments_are_open, False)
        entry.AUTO_CLOSE_COMMENTS_AFTER = 5
        self.assertEquals(self.entry.comments_are_open, True)
        self.entry.start_publication = timezone.now() - timedelta(days=7)
        self.entry.save()
        self.assertEquals(self.entry.comments_are_open, False)
        entry.AUTO_CLOSE_COMMENTS_AFTER = original_auto_close

    def test_pingbacks_are_open(self):
        original_auto_close = entry.AUTO_CLOSE_PINGBACKS_AFTER
        entry.AUTO_CLOSE_PINGBACKS_AFTER = None
        self.assertEquals(self.entry.pingbacks_are_open, True)
        entry.AUTO_CLOSE_PINGBACKS_AFTER = -1
        self.assertEquals(self.entry.pingbacks_are_open, True)
        entry.AUTO_CLOSE_PINGBACKS_AFTER = 0
        self.assertEquals(self.entry.pingbacks_are_open, False)
        entry.AUTO_CLOSE_PINGBACKS_AFTER = 5
        self.assertEquals(self.entry.pingbacks_are_open, True)
        self.entry.start_publication = timezone.now() - timedelta(days=7)
        self.entry.save()
        self.assertEquals(self.entry.pingbacks_are_open, False)
        entry.AUTO_CLOSE_PINGBACKS_AFTER = original_auto_close

    def test_trackbacks_are_open(self):
        original_auto_close = entry.AUTO_CLOSE_TRACKBACKS_AFTER
        entry.AUTO_CLOSE_TRACKBACKS_AFTER = None
        self.assertEquals(self.entry.trackbacks_are_open, True)
        entry.AUTO_CLOSE_TRACKBACKS_AFTER = -1
        self.assertEquals(self.entry.trackbacks_are_open, True)
        entry.AUTO_CLOSE_TRACKBACKS_AFTER = 0
        self.assertEquals(self.entry.trackbacks_are_open, False)
        entry.AUTO_CLOSE_TRACKBACKS_AFTER = 5
        self.assertEquals(self.entry.trackbacks_are_open, True)
        self.entry.start_publication = timezone.now() - timedelta(days=7)
        self.entry.save()
        self.assertEquals(self.entry.trackbacks_are_open, False)
        entry.AUTO_CLOSE_TRACKBACKS_AFTER = original_auto_close

    def test_is_actual(self):
        self.assertTrue(self.entry.is_actual)
        self.entry.start_publication = datetime(2020, 3, 15)
        self.assertFalse(self.entry.is_actual)
        self.entry.start_publication = timezone.now()
        self.assertTrue(self.entry.is_actual)
        self.entry.end_publication = datetime(2000, 3, 15)
        self.assertFalse(self.entry.is_actual)

    def test_is_visible(self):
        self.assertFalse(self.entry.is_visible)
        self.entry.status = PUBLISHED
        self.assertTrue(self.entry.is_visible)
        self.entry.start_publication = datetime(2020, 3, 15)
        self.assertFalse(self.entry.is_visible)

    def test_short_url(self):
        original_shortener = shortener_settings.URL_SHORTENER_BACKEND
        shortener_settings.URL_SHORTENER_BACKEND = 'zinnia.url_shortener.'\
                                                   'backends.default'
        self.assertEquals(self.entry.short_url,
                          'http://example.com' +
                          reverse('zinnia_entry_shortlink',
                                  args=[self.entry.pk]))
        shortener_settings.URL_SHORTENER_BACKEND = original_shortener

    def test_previous_entry(self):
        site = Site.objects.get_current()
        with self.assertNumQueries(0):
            # entry.previous_entry does not works until entry
            # is published, so no query should be performed
            self.assertFalse(self.entry.previous_entry)
        self.entry.status = PUBLISHED
        self.entry.save()
        self.entry.sites.add(site)
        del self.entry.previous_next  # Invalidate the cached property
        with self.assertNumQueries(1):
            self.assertFalse(self.entry.previous_entry)
            # Reload to check the cache
            self.assertFalse(self.entry.previous_entry)
        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'slug': 'my-second-entry',
                  'creation_date': datetime(2000, 1, 1),
                  'status': PUBLISHED}
        self.second_entry = Entry.objects.create(**params)
        self.second_entry.sites.add(site)
        del self.entry.previous_next  # Invalidate the cached property
        with self.assertNumQueries(1):
            self.assertEquals(self.entry.previous_entry, self.second_entry)
            # Reload to check the cache
            self.assertEquals(self.entry.previous_entry, self.second_entry)
        params = {'title': 'My third entry',
                  'content': 'My third content',
                  'slug': 'my-third-entry',
                  'creation_date': datetime(2001, 1, 1),
                  'status': PUBLISHED}
        self.third_entry = Entry.objects.create(**params)
        self.third_entry.sites.add(site)
        del self.entry.previous_next  # Invalidate the cached property
        self.assertEquals(self.entry.previous_entry, self.third_entry)
        self.assertEquals(self.third_entry.previous_entry, self.second_entry)
        self.assertFalse(self.second_entry.previous_entry)

    def test_next_entry(self):
        site = Site.objects.get_current()
        with self.assertNumQueries(0):
            # entry.next_entry does not works until entry
            # is published, so no query should be performed
            self.assertFalse(self.entry.previous_entry)
        self.entry.status = PUBLISHED
        self.entry.save()
        self.entry.sites.add(site)
        del self.entry.previous_next  # Invalidate the cached property
        with self.assertNumQueries(1):
            self.assertFalse(self.entry.next_entry)
            # Reload to check the cache
            self.assertFalse(self.entry.next_entry)
        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'slug': 'my-second-entry',
                  'creation_date': datetime(2100, 1, 1),
                  'status': PUBLISHED}
        self.second_entry = Entry.objects.create(**params)
        self.second_entry.sites.add(site)
        del self.entry.previous_next  # Invalidate the cached property
        with self.assertNumQueries(1):
            self.assertEquals(self.entry.next_entry, self.second_entry)
            # Reload to check the cache
            self.assertEquals(self.entry.next_entry, self.second_entry)
        params = {'title': 'My third entry',
                  'content': 'My third content',
                  'slug': 'my-third-entry',
                  'creation_date': datetime(2050, 1, 1),
                  'status': PUBLISHED}
        self.third_entry = Entry.objects.create(**params)
        self.third_entry.sites.add(site)
        del self.entry.previous_next  # Invalidate the cached property
        self.assertEquals(self.entry.next_entry, self.third_entry)
        self.assertEquals(self.third_entry.next_entry, self.second_entry)
        self.assertFalse(self.second_entry.next_entry)

    def test_previous_next_entry_in_one_query(self):
        site = Site.objects.get_current()
        self.entry.status = PUBLISHED
        self.entry.save()
        self.entry.sites.add(site)
        with self.assertNumQueries(1):
            self.assertFalse(self.entry.previous_entry)
            self.assertFalse(self.entry.next_entry)
            # Reload to check the cache
            self.assertFalse(self.entry.previous_entry)
            self.assertFalse(self.entry.next_entry)
        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'slug': 'my-second-entry',
                  'creation_date': datetime(2001, 1, 1),
                  'status': PUBLISHED}
        self.second_entry = Entry.objects.create(**params)
        self.second_entry.sites.add(site)
        params = {'title': 'My third entry',
                  'content': 'My third content',
                  'slug': 'my-third-entry',
                  'creation_date': datetime(2050, 1, 1),
                  'status': PUBLISHED}
        self.third_entry = Entry.objects.create(**params)
        self.third_entry.sites.add(site)
        del self.entry.previous_next  # Invalidate the cached property
        with self.assertNumQueries(1):
            self.assertEquals(self.entry.previous_entry, self.second_entry)
            self.assertEquals(self.entry.next_entry, self.third_entry)
            # Reload to check the cache
            self.assertEquals(self.entry.previous_entry, self.second_entry)
            self.assertEquals(self.entry.next_entry, self.third_entry)

    def test_related_published(self):
        site = Site.objects.get_current()
        self.assertFalse(self.entry.related_published)
        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'slug': 'my-second-entry',
                  'status': PUBLISHED}
        self.second_entry = Entry.objects.create(**params)
        self.second_entry.related.add(self.entry)
        self.assertEquals(len(self.entry.related_published), 0)

        self.second_entry.sites.add(site)
        self.assertEquals(len(self.entry.related_published), 1)
        self.assertEquals(len(self.second_entry.related_published), 0)

        self.entry.status = PUBLISHED
        self.entry.save()
        self.entry.sites.add(site)
        self.assertEquals(len(self.entry.related_published), 1)
        self.assertEquals(len(self.second_entry.related_published), 1)

    def test_tags_list(self):
        self.assertEquals(self.entry.tags_list, [])
        self.entry.tags = 'tag-1, tag-2'
        self.assertEquals(self.entry.tags_list, ['tag-1', 'tag-2'])


class EntryHtmlContentTestCase(TestCase):

    def setUp(self):
        params = {'title': 'My entry',
                  'content': 'My content',
                  'slug': 'my-entry'}
        self.entry = Entry(**params)
        self.original_rendering = entry.MARKUP_LANGUAGE

    def tearDown(self):
        entry.MARKUP_LANGUAGE = self.original_rendering

    def test_html_content_default(self):
        entry.MARKUP_LANGUAGE = None
        self.assertEquals(self.entry.html_content, '<p>My content</p>')

        self.entry.content = 'Hello world !\n' \
                             ' this is my content'
        self.assertEquals(self.entry.html_content,
                          '<p>Hello world !<br /> this is my content</p>')

    @skipUnless(is_lib_available('textile'), 'Textile is not available')
    def test_html_content_textitle(self):
        entry.MARKUP_LANGUAGE = 'textile'
        self.entry.content = 'Hello world !\n\n' \
                             'this is my content :\n\n' \
                             '* Item 1\n* Item 2'
        html_content = self.entry.html_content
        self.assertEquals(html_content,
                          '\t<p>Hello world !</p>\n\n\t'
                          '<p>this is my content :</p>\n\n\t'
                          '<ul>\n\t\t<li>Item 1</li>\n\t\t'
                          '<li>Item 2</li>\n\t</ul>')

    @skipUnless(is_lib_available('markdown'), 'Markdown is not available')
    def test_html_content_markdown(self):
        entry.MARKUP_LANGUAGE = 'markdown'
        self.entry.content = 'Hello world !\n\n' \
                             'this is my content :\n\n' \
                             '* Item 1\n* Item 2'
        html_content = self.entry.html_content
        self.assertEquals(html_content,
                          '<p>Hello world !</p>\n'
                          '<p>this is my content :</p>'
                          '\n<ul>\n<li>Item 1</li>\n'
                          '<li>Item 2</li>\n</ul>')

    @skipUnless(is_lib_available('docutils'), 'Docutils is not available')
    def test_html_content_restructuredtext(self):
        entry.MARKUP_LANGUAGE = 'restructuredtext'
        self.entry.content = 'Hello world !\n\n' \
                             'this is my content :\n\n' \
                             '* Item 1\n* Item 2'
        html_content = self.entry.html_content
        self.assertEquals(html_content,
                          '<p>Hello world !</p>\n'
                          '<p>this is my content :</p>'
                          '\n<ul class="simple">\n<li>Item 1</li>\n'
                          '<li>Item 2</li>\n</ul>\n')

    def test_html_preview(self):
        entry.MARKUP_LANGUAGE = None
        preview = self.entry.html_preview
        self.assertEquals(str(preview), '<p>My content</p>')
        self.assertEquals(preview.has_more, False)


class EntryAbsoluteUrlTestCase(TestCase):

    def check_get_absolute_url(self, creation_date, url_expected):
        params = {'title': 'My entry',
                  'content': 'My content',
                  'slug': 'my-entry',
                  'creation_date': creation_date}
        entry = Entry.objects.create(**params)
        self.assertTrue(url_expected in entry.get_absolute_url())

    @override_settings(USE_TZ=False)
    def test_get_absolute_url_no_timezone(self):
        self.check_get_absolute_url(datetime(2013, 1, 1, 12, 0),
                                    '/2013/01/01/my-entry/')

    @override_settings(USE_TZ=True, TIME_ZONE='Europe/Paris')
    def test_get_absolute_url_with_timezone(self):
        self.check_get_absolute_url(datetime(2013, 1, 1, 12, 0),
                                    '/2013/01/01/my-entry/')
        self.check_get_absolute_url(datetime(2013, 1, 1, 23, 0),
                                    '/2013/01/02/my-entry/')

"""Unit tests for zinnia"""
import cStringIO
from datetime import datetime
from urlparse import urlsplit
from urllib2 import HTTPError
from xmlrpclib import Fault
from xmlrpclib import Transport
from xmlrpclib import ServerProxy

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.template import TemplateDoesNotExist

from tagging.models import Tag
from zinnia.models import Entry
from zinnia.models import Category
from zinnia.managers import DRAFT, HIDDEN, PUBLISHED
from zinnia.managers import tags_published
from zinnia.managers import entries_published
from zinnia.managers import authors_published
from zinnia.xmlrpc.metaweblog import authenticate
from zinnia.xmlrpc.metaweblog import post_structure
from zinnia.xmlrpc.pingback import generate_pingback_content
from BeautifulSoup import BeautifulSoup

class ManagersTestCase(TestCase):

    def setUp(self):
        self.sites = [Site.objects.get_current(),
                      Site.objects.create(domain='http://domain.com',
                                          name='Domain.com')]
        self.authors = [User.objects.create_user(username='webmaster',
                                                 email='webmaster@example.com'),
                        User.objects.create_user(username='contributor',
                                                 email='contributor@example.com')]
        self.categories = [Category.objects.create(title='Category 1',
                                                   slug='category-1'),
                           Category.objects.create(title='Category 2',
                                                   slug='category-2')]

        params = {'title': 'My entry 1', 'content': 'My content 1',
                  'tags': 'zinnia, test', 'slug': 'my-entry-1',
                  'status': PUBLISHED}
        self.entry_1 = Entry.objects.create(**params)
        self.entry_1.authors.add(self.authors[0])
        self.entry_1.categories.add(*self.categories)
        self.entry_1.sites.add(*self.sites)

        params = {'title': 'My entry 2', 'content': 'My content 2',
                  'tags': 'zinnia, test', 'slug': 'my-entry-2'}
        self.entry_2 = Entry.objects.create(**params)
        self.entry_2.authors.add(*self.authors)
        self.entry_2.categories.add(self.categories[0])
        self.entry_2.sites.add(self.sites[0])

    def test_tags_published(self):
        self.assertEquals(tags_published().count(), Tag.objects.count())
        Tag.objects.create(name='out')
        self.assertNotEquals(tags_published().count(), Tag.objects.count())

    def test_authors_published(self):
        self.assertEquals(authors_published().count(), 1)
        self.entry_2.status = PUBLISHED
        self.entry_2.save()
        self.assertEquals(authors_published().count(), 2)

    def test_entries_published(self):
        self.assertEquals(entries_published(Entry.objects.all()).count(), 1)
        self.entry_2.status = PUBLISHED
        self.entry_2.save()
        self.assertEquals(entries_published(Entry.objects.all()).count(), 2)
        self.entry_1.sites.clear()
        self.assertEquals(entries_published(Entry.objects.all()).count(), 1)
        self.entry_1.sites.add(*self.sites)
        self.entry_1.start_publication = datetime(2020, 1, 1)
        self.entry_1.save()
        self.assertEquals(entries_published(Entry.objects.all()).count(), 1)
        self.entry_1.start_publication = datetime(2000, 1, 1)
        self.entry_1.save()
        self.assertEquals(entries_published(Entry.objects.all()).count(), 2)
        self.entry_1.end_publication = datetime(2000, 1, 1)
        self.entry_1.save()
        self.assertEquals(entries_published(Entry.objects.all()).count(), 1)
        self.entry_1.end_publication = datetime(2020, 1, 1)
        self.entry_1.save()
        self.assertEquals(entries_published(Entry.objects.all()).count(), 2)

    def test_entry_published_manager_get_query_set(self):
        self.assertEquals(Entry.published.count(), 1)
        self.entry_2.status = PUBLISHED
        self.entry_2.save()
        self.assertEquals(Entry.published.count(), 2)
        self.entry_1.sites.clear()
        self.assertEquals(Entry.published.count(), 1)
        self.entry_1.sites.add(*self.sites)
        self.entry_1.start_publication = datetime(2020, 1, 1)
        self.entry_1.save()
        self.assertEquals(Entry.published.count(), 1)
        self.entry_1.start_publication = datetime(2000, 1, 1)
        self.entry_1.save()
        self.assertEquals(Entry.published.count(), 2)
        self.entry_1.end_publication = datetime(2000, 1, 1)
        self.entry_1.save()
        self.assertEquals(Entry.published.count(), 1)
        self.entry_1.end_publication = datetime(2020, 1, 1)
        self.entry_1.save()
        self.assertEquals(Entry.published.count(), 2)

    def test_entry_published_manager_on_site(self):
        self.assertEquals(Entry.published.on_site().count(), 2)
        self.entry_2.sites.clear()
        self.entry_2.sites.add(self.sites[1])
        self.assertEquals(Entry.published.on_site().count(), 1)
        self.entry_1.sites.clear()
        self.assertEquals(Entry.published.on_site().count(), 0)

    def test_entry_published_manager_basic_search(self):
        self.assertEquals(Entry.published.basic_search('My ').count(), 1)
        self.entry_2.status = PUBLISHED
        self.entry_2.save()
        self.assertEquals(Entry.published.basic_search('My ').count(), 2)
        self.assertEquals(Entry.published.basic_search('1').count(), 1)
        self.assertEquals(Entry.published.basic_search('content 1').count(), 2)

    def test_entry_published_manager_advanced_search(self):
        category = Category.objects.create(title='SimpleCategory', slug='simple')
        self.entry_2.categories.add(category)
        self.entry_2.tags = self.entry_2.tags + ', custom'
        self.entry_2.status = PUBLISHED
        self.entry_2.save()
        self.assertEquals(Entry.published.advanced_search('content').count(), 2)
        search = Entry.published.advanced_search('content 1')
        self.assertEquals(search.count(), 1)
        self.assertEquals(search.all()[0].pk, 1)
        self.assertEquals(Entry.published.advanced_search('content 1 or 2').count(), 2)
        self.assertEquals(Entry.published.advanced_search('content 1 and 2').count(), 0)
        self.assertEquals(Entry.published.advanced_search('content 1 2').count(), 0)
        self.assertEquals(Entry.published.advanced_search('"My content" 1 or 2').count(), 2)
        search = Entry.published.advanced_search('content -1')
        self.assertEquals(search.count(), 1)
        self.assertEquals(search.all()[0].pk, 2)
        self.assertEquals(Entry.published.advanced_search('content category:SimpleCategory').count(), 1)
        self.assertEquals(Entry.published.advanced_search('content category:simple').count(), 1)
        self.assertEquals(Entry.published.advanced_search('content category:"Category 1"').count(), 2)
        self.assertEquals(Entry.published.advanced_search('content category:"category-1"').count(), 2)
        self.assertEquals(Entry.published.advanced_search('content category:"category-2"').count(), 1)
        self.assertEquals(Entry.published.advanced_search('content tag:zinnia').count(), 2)
        self.assertEquals(Entry.published.advanced_search('content tag:custom').count(), 1)
        self.assertEquals(Entry.published.advanced_search('content author:webmaster').count(), 2)
        self.assertEquals(Entry.published.advanced_search('content author:contributor').count(), 1)
        self.assertEquals(Entry.published.advanced_search('content author:webmaster tag:zinnia').count(), 2)
        self.assertEquals(Entry.published.advanced_search('content author:webmaster tag:custom').count(), 1)
        self.assertEquals(Entry.published.advanced_search('content 1 or 2 author:webmaster').count(), 2)
        self.assertEquals(Entry.published.advanced_search('content 1 or 2 author:webmaster').count(), 2)
        self.assertEquals(Entry.published.advanced_search('(author:webmaster content) my').count(), 2)
        self.assertEquals(Entry.published.advanced_search('(author:webmaster) or (author:contributor)').count(), 2)
        self.assertEquals(Entry.published.advanced_search('(author:webmaster) (author:contributor)').count(), 0)
        self.assertEquals(Entry.published.advanced_search('(author:webmaster content) 1').count(), 1)
        self.assertEquals(Entry.published.advanced_search('(author:webmaster content) or 2').count(), 2)
        self.assertEquals(Entry.published.advanced_search('(author:contributor content) or 1').count(), 2)
        self.assertEquals(Entry.published.advanced_search('(author:contributor content) or 2').count(), 1)
        self.assertEquals(Entry.published.advanced_search('(author:webmaster or ("hello world")) and 2').count(), 1)


class EntryTestCase(TestCase):

    def setUp(self):
        params = {'title': 'My entry',
                  'content': 'My content',
                  'tags': 'zinnia, test',
                  'slug': 'my-entry'}
        self.entry = Entry.objects.create(**params)
        self.author = User.objects.create_user(username='webmaster',
                                               email='webmaster@example.com')

    def test_html_content(self):
        self.assertEquals(self.entry.html_content, '<p>My content</p>')

        self.entry.content = """Hello world !
        this is my content"""
        self.assertEquals(self.entry.html_content,
                          '<p>Hello world !<br />        this is my content</p>')

    def test_discussions(self):
        site = Site.objects.get_current()

        self.assertEquals(self.entry.discussions.count(), 0)
        self.assertEquals(self.entry.comments.count(), 0)
        self.assertEquals(self.entry.pingbacks.count(), 0)
        self.assertEquals(self.entry.trackbacks.count(), 0)

        Comment.objects.create(comment='My Comment 1',
                               content_object=self.entry,
                               site=site)
        self.assertEquals(self.entry.discussions.count(), 1)
        self.assertEquals(self.entry.comments.count(), 1)
        self.assertEquals(self.entry.pingbacks.count(), 0)
        self.assertEquals(self.entry.trackbacks.count(), 0)

        Comment.objects.create(comment='My Comment 2',
                               content_object=self.entry,
                               site=site, is_public=False)
        self.assertEquals(self.entry.discussions.count(), 1)
        self.assertEquals(self.entry.comments.count(), 1)
        self.assertEquals(self.entry.pingbacks.count(), 0)
        self.assertEquals(self.entry.trackbacks.count(), 0)

        Comment.objects.create(comment='My Comment 3',
                               content_object=self.entry,
                               site=Site.objects.create(domain='http://toto.com',
                                                        name='Toto.com'))
        self.assertEquals(self.entry.discussions.count(), 2)
        self.assertEquals(self.entry.comments.count(), 2)
        self.assertEquals(self.entry.pingbacks.count(), 0)
        self.assertEquals(self.entry.trackbacks.count(), 0)

        comment = Comment.objects.create(comment='My Pingback 1',
                                         content_object=self.entry,
                                         site=site)
        comment.flags.create(user=self.author, flag='pingback')
        self.assertEquals(self.entry.discussions.count(), 3)
        self.assertEquals(self.entry.comments.count(), 2)
        self.assertEquals(self.entry.pingbacks.count(), 1)
        self.assertEquals(self.entry.trackbacks.count(), 0)

        comment = Comment.objects.create(comment='My Trackback 1',
                                         content_object=self.entry,
                                         site=site)
        comment.flags.create(user=self.author, flag='trackback')
        self.assertEquals(self.entry.discussions.count(), 4)
        self.assertEquals(self.entry.comments.count(), 2)
        self.assertEquals(self.entry.pingbacks.count(), 1)
        self.assertEquals(self.entry.trackbacks.count(), 1)

    def test_word_count(self):
        self.assertEquals(self.entry.word_count, 2)

    def test_is_actual(self):
        self.assertTrue(self.entry.is_actual)
        self.entry.start_publication = datetime(2020, 3, 15)
        self.assertFalse(self.entry.is_actual)
        self.entry.start_publication = datetime.now()
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
        pass

    def test_previous_entry(self):
        self.assertFalse(self.entry.previous_entry)
        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'tags': 'zinnia, test',
                  'slug': 'my-second-entry',
                  'creation_date': datetime(2000, 1, 1),
                  'status': PUBLISHED}
        self.second_entry = Entry.objects.create(**params)
        self.second_entry.sites.add(Site.objects.get_current())
        self.assertEquals(self.entry.previous_entry, self.second_entry)
        params = {'title': 'My third entry',
                  'content': 'My third content',
                  'tags': 'zinnia, test',
                  'slug': 'my-third-entry',
                  'creation_date': datetime(2001, 1, 1),
                  'status': PUBLISHED}
        self.third_entry = Entry.objects.create(**params)
        self.third_entry.sites.add(Site.objects.get_current())
        self.assertEquals(self.entry.previous_entry, self.third_entry)
        self.assertEquals(self.third_entry.previous_entry, self.second_entry)

    def test_next_entry(self):
        self.assertFalse(self.entry.next_entry)
        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'tags': 'zinnia, test',
                  'slug': 'my-second-entry',
                  'creation_date': datetime(2100, 1, 1),
                  'status': PUBLISHED}
        self.second_entry = Entry.objects.create(**params)
        self.second_entry.sites.add(Site.objects.get_current())
        self.assertEquals(self.entry.next_entry, self.second_entry)
        params = {'title': 'My third entry',
                  'content': 'My third content',
                  'tags': 'zinnia, test',
                  'slug': 'my-third-entry',
                  'creation_date': datetime(2050, 1, 1),
                  'status': PUBLISHED}
        self.third_entry = Entry.objects.create(**params)
        self.third_entry.sites.add(Site.objects.get_current())
        self.assertEquals(self.entry.next_entry, self.third_entry)
        self.assertEquals(self.third_entry.next_entry, self.second_entry)

    def test_related_published_set(self):
        self.assertFalse(self.entry.related_published_set)
        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'tags': 'zinnia, test',
                  'slug': 'my-second-entry',
                  'status': PUBLISHED}
        self.second_entry = Entry.objects.create(**params)
        self.second_entry.related.add(self.entry)
        self.assertEquals(len(self.entry.related_published_set), 0)

        self.second_entry.sites.add(Site.objects.get_current())
        self.assertEquals(len(self.entry.related_published_set), 1)
        self.assertEquals(len(self.second_entry.related_published_set), 0)

        self.entry.status = PUBLISHED
        self.entry.save()
        self.entry.sites.add(Site.objects.get_current())
        self.assertEquals(len(self.entry.related_published_set), 1)
        self.assertEquals(len(self.second_entry.related_published_set), 1)


class CategoryTestCase(TestCase):

    def setUp(self):
        self.site = Site.objects.get_current()
        self.categories = [Category.objects.create(title='Category 1',
                                                   slug='category-1'),
                           Category.objects.create(title='Category 2',
                                                   slug='category-2')]
        params = {'title': 'My entry',
                  'content': 'My content',
                  'tags': 'zinnia, test',
                  'slug': 'my-entry'}

        self.entry = Entry.objects.create(**params)
        self.entry.categories.add(*self.categories)
        self.entry.sites.add(self.site)

    def test_entries_published_set(self):
        category = self.categories[0]
        self.assertEqual(category.entries_published_set().count(), 0)
        self.entry.status = PUBLISHED
        self.entry.save()
        self.assertEqual(category.entries_published_set().count(), 1)

        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'tags': 'zinnia, test',
                  'status': PUBLISHED,
                  'slug': 'my-second-entry'}

        new_entry = Entry.objects.create(**params)
        new_entry.sites.add(self.site)
        new_entry.categories.add(self.categories[0])

        self.assertEqual(self.categories[0].entries_published_set().count(), 2)
        self.assertEqual(self.categories[1].entries_published_set().count(), 1)

class ZinniaViewsTestCase(TestCase):
    """Test cases for generic views used in the application,
    for reproducing and correcting issue :
    http://github.com/Fantomas42/django-blog-zinnia/issues#issue/3
    """
    urls = 'zinnia.urls.tests'
    fixtures = ['zinnia_test_data.json',]

    def create_published_entry(self):
        params = {'title': 'My test entry',
                  'content': 'My test content',
                  'slug': 'my-test-entry',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 1, 1),
                  'status': PUBLISHED}
        entry = Entry.objects.create(**params)
        entry.sites.add(Site.objects.get_current())
        entry.categories.add(Category.objects.get(slug='tests'))
        entry.authors.add(User.objects.get(username='admin'))
        return entry

    def check_publishing_context(self, url, first_expected,
                                 second_expected=None):
        """Test the numbers of entries in context of an url,"""
        response = self.client.get(url)
        self.assertEquals(len(response.context['object_list']), first_expected)
        if second_expected:
            self.create_published_entry()
            response = self.client.get(url)
            self.assertEquals(len(response.context['object_list']), second_expected)

    def test_zinnia_entry_archive_index(self):
        self.check_publishing_context('/', 2, 3)

    def test_zinnia_entry_archive_year(self):
        self.check_publishing_context('/2010/', 2, 3)

    def test_zinnia_entry_archive_month(self):
        self.check_publishing_context('/2010/01/', 1, 2)

    def test_zinnia_entry_archive_day(self):
        self.check_publishing_context('/2010/01/01/', 1, 2)

    def test_zinnia_entry_detail(self):
        entry = self.create_published_entry()
        entry.sites.clear()
        # Check a 404 error, but the 404.html may no exist
        try:
            self.assertRaises(TemplateDoesNotExist, self.client.get,
                              '/2010/01/01/my-test-entry/')
        except AssertionError:
            response = self.client.get('/2010/01/01/my-test-entry/')
            self.assertEquals(response.status_code, 404)

        entry.sites.add(Site.objects.get_current())
        response = self.client.get('/2010/01/01/my-test-entry/')
        self.assertEquals(response.status_code, 200)

    def test_zinnia_category_list(self):
        self.check_publishing_context('/categories/', 1)
        entry = Entry.objects.all()[0]
        entry.categories.add(Category.objects.create(title='New category',
                                                     slug='new-category'))
        self.check_publishing_context('/categories/', 2)

    def test_zinnia_category_detail(self):
        self.check_publishing_context('/categories/tests/', 2, 3)

    def test_zinnia_author_list(self):
        self.check_publishing_context('/authors/', 1)
        entry = Entry.objects.all()[0]
        entry.authors.add(User.objects.create(username='new-user',
                                              email='new_user@example.com'))
        self.check_publishing_context('/authors/', 2)

    def test_zinnia_author_detail(self):
        self.check_publishing_context('/authors/admin/', 2, 3)

    def test_zinnia_tag_list(self):
        self.check_publishing_context('/tags/', 1)
        entry = Entry.objects.all()[0]
        entry.tags = 'tests, tag'
        entry.save()
        self.check_publishing_context('/tags/', 2)

    def test_zinnia_tag_detail(self):
        self.check_publishing_context('/tags/tests/', 2, 3)

    def test_zinnia_entry_search(self):
        self.check_publishing_context('/search/?pattern=test', 2, 3)

    def test_zinnia_sitemap(self):
        response = self.client.get('/sitemap/')
        self.assertEquals(len(response.context['entries']), 2)
        self.assertEquals(len(response.context['categories']), 1)
        entry = self.create_published_entry()
        entry.categories.add(Category.objects.create(title='New category',
                                                     slug='new-category'))
        response = self.client.get('/sitemap/')
        self.assertEquals(len(response.context['entries']), 3)
        self.assertEquals(len(response.context['categories']), 2)

    def test_zinnia_trackback(self):
        # Check a 404 error, but the 404.html may no exist
        try:
            self.assertRaises(TemplateDoesNotExist, self.client.post,
                              '/trackback/404/')
        except AssertionError:
            response = self.client.post('/trackback/404/')
            self.assertEquals(response.status_code, 404)
        self.assertEquals(self.client.post('/trackback/test-1/').status_code, 302)
        self.assertEquals(self.client.get('/trackback/test-1/').status_code, 302)
        entry = Entry.objects.get(slug='test-1')
        entry.pingback_enabled = False
        entry.save()
        self.assertEquals(self.client.post('/trackback/test-1/', {'url': 'http://example.com'}).content,
                          '<?xml version="1.0" encoding="utf-8"?>\n<response>\n  \n  <error>1</error>\n  '
                          '<message>Trackback is not enabled for Test 1</message>\n  \n</response>\n')
        entry.pingback_enabled = True
        entry.save()
        self.assertEquals(self.client.post('/trackback/test-1/', {'url': 'http://example.com'}).content,
                          '<?xml version="1.0" encoding="utf-8"?>\n<response>\n  \n  <error>0</error>\n  \n</response>\n')
        self.assertEquals(self.client.post('/trackback/test-1/', {'url': 'http://example.com'}).content,
                          '<?xml version="1.0" encoding="utf-8"?>\n<response>\n  \n  <error>1</error>\n  '
                          '<message>Trackback is already registered</message>\n  \n</response>\n')

class TestTransport(Transport):
    """Handles connections to XML-RPC server
    through Django test client."""

    def __init__(self, *args, **kwargs):
        Transport.__init__(self, *args, **kwargs)
        self.client = Client()

    def request(self, host, handler, request_body, verbose=0):
        self.verbose = verbose
        response = self.client.post(handler,
                                    request_body,
                                    content_type="text/xml")
        res = cStringIO.StringIO(response.content)
        res.seek(0)
        return self.parse_response(res)


class PingBackTestCase(TestCase):
    """TestCases for pingbacks"""
    urls = 'zinnia.urls.tests'

    def fake_urlopen(self, url):
        """Fake urlopen using client if domain
        correspond to current_site else HTTPError"""
        scheme, netloc, path, query, fragment = urlsplit(url)
        if not netloc:
            raise
        if self.site.domain == netloc:
            response = cStringIO.StringIO(self.client.get(url).content)
            return response
        raise HTTPError(url, 404, 'unavailable url', {}, None)

    def setUp(self):
        # Set up a stub around urlopen
        import zinnia.xmlrpc.pingback
        self.original_urlopen = zinnia.xmlrpc.pingback.urlopen
        zinnia.xmlrpc.pingback.urlopen = self.fake_urlopen
        # Preparing site
        self.site = Site.objects.get_current()
        self.site.domain = 'localhost:8000'
        self.site.save()
        # Creating tests entries
        self.author = User.objects.create_user(username='webmaster',
                                               email='webmaster@example.com')
        self.category = Category.objects.create(title='test', slug='test')
        params = {'title': 'My first entry',
                  'content': 'My first content',
                  'slug': 'my-first-entry',
                  'creation_date': datetime(2010, 1, 1),
                  'status': PUBLISHED}
        self.first_entry = Entry.objects.create(**params)
        self.first_entry.sites.add(self.site)
        self.first_entry.categories.add(self.category)
        self.first_entry.authors.add(self.author)

        params = {'title': 'My second entry',
                  'content': 'My second content with link ' \
                  'to <a href="http://%s%s">first entry</a> and other links : %s %s.' % (
                      self.site.domain,
                      self.first_entry.get_absolute_url(),
                      'http://localhost:8000/404/',
                      'http://example.com/'),
                  'slug': 'my-second-entry',
                  'creation_date': datetime(2010, 1, 1),
                  'status': PUBLISHED}
        self.second_entry = Entry.objects.create(**params)
        self.second_entry.sites.add(self.site)
        self.second_entry.categories.add(self.category)
        self.second_entry.authors.add(self.author)
        # Instanciating the server proxy
        self.server = ServerProxy('http://localhost:8000/xmlrpc/',
                                  transport=TestTransport())

    def tearDown(self):
        import zinnia.xmlrpc.pingback
        zinnia.xmlrpc.pingback.urlopen = self.original_urlopen

    def test_generate_pingback_content(self):
        soup = BeautifulSoup(self.second_entry.content)
        target = 'http://%s%s' % (self.site.domain, self.first_entry.get_absolute_url())

        self.assertEquals(generate_pingback_content(soup, target, 1000),
                          'My second content with link to first entry and '\
                          'other links : http://localhost:8000/404/ http://example.com/.')

        self.assertEquals(generate_pingback_content(soup, target, 50),
                          '...ond content with link to first entry and other link...')

    def test_pingback_ping(self):
        target = 'http://%s%s' % (self.site.domain, self.first_entry.get_absolute_url())
        source = 'http://%s%s' % (self.site.domain, self.second_entry.get_absolute_url())

        # Error code 0 : A generic fault code
        response = self.server.pingback.ping('toto', 'titi')
        self.assertEquals(response, 0)
        response = self.server.pingback.ping('http://%s/' % self.site.domain,
                                             'http://%s/' % self.site.domain)
        self.assertEquals(response, 0)

        # Error code 16 : The source URI does not exist.
        response = self.server.pingback.ping('http://example.com/', target)
        self.assertEquals(response, 16)

        # Error code 17 : The source URI does not contain a link to the target URI,
        # and so cannot be used as a source.
        response = self.server.pingback.ping(source, 'toto')
        self.assertEquals(response, 17)

        # Error code 32 : The target URI does not exist.
        response = self.server.pingback.ping(source, 'http://localhost:8000/404/')
        self.assertEquals(response, 32)
        response = self.server.pingback.ping(source, 'http://example.com/')
        self.assertEquals(response, 32)

        # Error code 33 : The target URI cannot be used as a target.
        response = self.server.pingback.ping(source, 'http://localhost:8000/')
        self.assertEquals(response, 33)
        self.first_entry.pingback_enabled = False
        self.first_entry.save()
        response = self.server.pingback.ping(source, target)
        self.assertEquals(response, 33)

        # Validate pingback
        self.assertEquals(self.first_entry.comments.count(), 0)
        self.first_entry.pingback_enabled = True
        self.first_entry.save()
        response = self.server.pingback.ping(source, target)
        self.assertEquals(response, 'Pingback from %s to %s registered.' % (source, target))
        self.assertEquals(self.first_entry.pingbacks.count(), 1)
        self.assertEquals(self.first_entry.pingbacks[0].user_name,
                          'Zinnia\'s Blog - %s' % self.second_entry.title)

        # Error code 48 : The pingback has already been registered.
        response = self.server.pingback.ping(source, target)
        self.assertEquals(response, 48)

    def test_pingback_extensions_get_pingbacks(self):
        target = 'http://%s%s' % (self.site.domain, self.first_entry.get_absolute_url())
        source = 'http://%s%s' % (self.site.domain, self.second_entry.get_absolute_url())

        response = self.server.pingback.ping(source, target)
        self.assertEquals(response, 'Pingback from %s to %s registered.' % (source, target))

        response = self.server.pingback.extensions.getPingbacks('http://example.com/')
        self.assertEquals(response, 32)

        response = self.server.pingback.extensions.getPingbacks('http://localhost:8000/404/')
        self.assertEquals(response, 32)

        response = self.server.pingback.extensions.getPingbacks('http://localhost:8000/2010/')
        self.assertEquals(response, 33)

        response = self.server.pingback.extensions.getPingbacks(source)
        self.assertEquals(response, [])

        response = self.server.pingback.extensions.getPingbacks(target)
        self.assertEquals(response, ['http://localhost:8000/2010/01/01/my-second-entry/'])

        comment = Comment.objects.create(
            content_type=ContentType.objects.get_for_model(Entry),
            object_pk=self.first_entry.pk, site=self.site, comment='Test pingback',
            user_url='http://example.com/blog/1/', user_name='Test pingback')
        comment.flags.create(user=self.author, flag='pingback')

        response = self.server.pingback.extensions.getPingbacks(target)
        self.assertEquals(response, ['http://localhost:8000/2010/01/01/my-second-entry/',
                                     'http://example.com/blog/1/'])

class MetaWeblogTestCase(TestCase):
    """TestCases for MetaWeblog"""
    urls = 'zinnia.urls.tests'

    def setUp(self):
        # Create data
        self.webmaster = User.objects.create_superuser(username='webmaster',
                                                       email='webmaster@example.com',
                                                       password='password')
        self.contributor = User.objects.create_user(username='contributor',
                                                    email='contributor@example.com',
                                                    password='password')
        self.site = Site.objects.get_current()
        self.categories = [Category.objects.create(title='Category 1',
                                                   slug='category-1'),
                           Category.objects.create(title='Category 2',
                                                   slug='category-2')]
        params = {'title': 'My entry 1', 'content': 'My content 1',
                  'tags': 'zinnia, test', 'slug': 'my-entry-1',
                  'creation_date': datetime(2010, 1, 1),
                  'status': PUBLISHED}
        self.entry_1 = Entry.objects.create(**params)
        self.entry_1.authors.add(self.webmaster)
        self.entry_1.categories.add(*self.categories)
        self.entry_1.sites.add(self.site)

        params = {'title': 'My entry 2', 'content': 'My content 2',
                  'creation_date': datetime(2010, 3, 15),
                  'tags': 'zinnia, test', 'slug': 'my-entry-2'}
        self.entry_2 = Entry.objects.create(**params)
        self.entry_2.authors.add(self.webmaster)
        self.entry_2.categories.add(self.categories[0])
        self.entry_2.sites.add(self.site)
        # Instanciating the server proxy
        self.server = ServerProxy('http://localhost:8000/xmlrpc/',
                                  transport=TestTransport())

    def test_authenticate(self):
        self.assertRaises(Fault, authenticate, 'badcontributor', 'badpassword')
        self.assertRaises(Fault, authenticate, 'contributor', 'badpassword')
        self.assertRaises(Fault, authenticate, 'contributor', 'password')
        self.contributor.is_staff = True
        self.contributor.save()
        self.assertEquals(authenticate('contributor', 'password'), self.contributor)
        self.assertRaises(Fault, authenticate, 'contributor', 'password', 'zinnia.change_entry')
        self.assertEquals(authenticate('webmaster', 'password'), self.webmaster)
        self.assertEquals(authenticate('webmaster', 'password', 'zinnia.change_entry'),
                          self.webmaster)

    def test_get_users_blogs(self):
        self.assertRaises(Fault, self.server.blogger.getUsersBlogs,
                          'apikey', 'contributor', 'password')
        self.assertEquals(self.server.blogger.getUsersBlogs(
            'apikey', 'webmaster', 'password'),
                          [{'url': 'http://example.com/',
                            'blogid': 1,
                            'blogName': 'example.com'}])

    def test_get_user_info(self):
        self.assertRaises(Fault, self.server.blogger.getUserInfo,
                          'apikey', 'contributor', 'password')
        self.webmaster.first_name = 'John'
        self.webmaster.last_name = 'Doe'
        self.webmaster.save()
        self.assertEquals(self.server.blogger.getUserInfo(
            'apikey', 'webmaster', 'password'),
                          {'firstname': 'John', 'lastname': 'Doe',
                           'url': 'http://example.com/authors/webmaster/',
                           'userid': 1, 'nickname': 'webmaster',
                           'email': 'webmaster@example.com'})

    def test_get_authors(self):
        self.assertRaises(Fault, self.server.wp.getAuthors,
                          'apikey', 'contributor', 'password')
        self.assertEquals(self.server.wp.getAuthors(
            'apikey', 'webmaster', 'password'), [
                              {'user_login': 'webmaster', 'user_id': 1,
                               'user_email': 'webmaster@example.com',
                               'display_name': 'webmaster'}])

    def test_get_categories(self):
        self.assertRaises(Fault, self.server.metaWeblog.getCategories,
                          1, 'contributor', 'password')
        self.assertEquals(self.server.metaWeblog.getCategories(
            'apikey', 'webmaster', 'password'),
                          [{'rssUrl': 'http://example.com/feeds/categories/category-1/',
                            'description': 'Category 1',
                            'htmlUrl': 'http://example.com/categories/category-1/'},
                           {'rssUrl': 'http://example.com/feeds/categories/category-2/',
                            'description': 'Category 2',
                            'htmlUrl': 'http://example.com/categories/category-2/'}])

    def test_get_recent_posts(self):
        self.assertRaises(Fault, self.server.metaWeblog.getRecentPosts,
                          1, 'contributor', 'password', 10)
        self.assertEquals(len(self.server.metaWeblog.getRecentPosts(
            1, 'webmaster', 'password', 10)), 2)

    def test_delete_post(self):
        self.assertRaises(Fault, self.server.blogger.deletePost,
                          'apikey', 1, 'contributor', 'password', 'publish')
        self.assertEquals(Entry.objects.count(), 2)
        self.assertEquals(self.server.blogger.deletePost(
            'apikey', 1, 'webmaster', 'password', 'publish'), True)
        self.assertEquals(Entry.objects.count(), 1)

    def test_get_post(self):
        self.assertRaises(Fault, self.server.metaWeblog.getPost,
                          1, 'contributor', 'password')
        post = self.server.metaWeblog.getPost(
            1, 'webmaster', 'password')
        self.assertEquals(post['title'], self.entry_1.title)
        self.assertEquals(post['description'], '<p>My content 1</p>')
        self.assertEquals(post['categories'], ['Category 1', 'Category 2'])
        self.assertEquals(post['dateCreated'].value, '2010-01-01T00:00:00')
        self.assertEquals(post['link'], 'http://example.com/2010/01/01/my-entry-1/')
        self.assertEquals(post['permaLink'], 'http://example.com/2010/01/01/my-entry-1/')
        self.assertEquals(post['postid'], 1)
        self.assertEquals(post['userid'], 'webmaster')
        self.assertEquals(post['mt_excerpt'], '')
        self.assertEquals(post['mt_allow_comments'], 1)
        self.assertEquals(post['mt_allow_pings'], 1)
        self.assertEquals(post['mt_keywords'], self.entry_1.tags)
        self.assertEquals(post['wp_author'], 'webmaster')
        self.assertEquals(post['wp_author_id'], 1)
        self.assertEquals(post['wp_author_display_name'], 'webmaster')
        self.assertEquals(post['wp_slug'], self.entry_1.slug)

    def test_new_post(self):
        post = post_structure(self.entry_2, self.site)
        self.assertRaises(Fault, self.server.metaWeblog.newPost,
                          1, 'contributor', 'password', post, 1)
        self.assertEquals(Entry.objects.count(), 2)
        self.assertEquals(Entry.published.count(), 1)
        new_post_id = self.server.metaWeblog.newPost(
            1, 'webmaster', 'password', post, 1)
        self.assertEquals(Entry.objects.count(), 3)
        self.assertEquals(Entry.published.count(), 2)
        new_post_id = self.server.metaWeblog.newPost(
            1, 'webmaster', 'password', post, 0)
        self.assertEquals(Entry.objects.count(), 4)
        self.assertEquals(Entry.published.count(), 2)

    def test_edit_post(self):
        post = post_structure(self.entry_2, self.site)
        self.assertRaises(Fault, self.server.metaWeblog.editPost,
                          1, 'contributor', 'password', post, 1)
        new_post_id = self.server.metaWeblog.newPost(
            1, 'webmaster', 'password', post, 0)

        entry = Entry.objects.get(pk=new_post_id)
        self.assertEquals(entry.title, self.entry_2.title)
        self.assertEquals(entry.content, self.entry_2.html_content)
        self.assertEquals(entry.excerpt, self.entry_2.excerpt)
        self.assertEquals(entry.slug, self.entry_2.slug)
        self.assertEquals(entry.status, DRAFT)
        self.assertEquals(entry.comment_enabled, True)
        self.assertEquals(entry.pingback_enabled, True)
        self.assertEquals(entry.categories.count(), 1)
        self.assertEquals(entry.authors.count(), 1)
        self.assertEquals(entry.authors.all()[0].pk, 1)
        self.assertEquals(entry.creation_date, self.entry_2.creation_date)

        entry.title = 'Title edited'
        entry.creation_date = datetime(2000, 1, 1)
        post = post_structure(entry, self.site)
        post['categories'] =  ''
        post['description'] = 'Content edited'
        post['mt_excerpt'] = 'Content edited'
        post['wp_slug'] = 'slug-edited'
        post['wp_author_id'] = 2
        post['mt_allow_comments'] = 2
        post['mt_allow_pings'] = 0

        response = self.server.metaWeblog.editPost(
            new_post_id, 'webmaster', 'password', post, 1)
        self.assertEquals(response, True)
        entry = Entry.objects.get(pk=new_post_id)
        self.assertEquals(entry.title, post['title'])
        self.assertEquals(entry.content, post['description'])
        self.assertEquals(entry.excerpt, post['mt_excerpt'])
        self.assertEquals(entry.slug, 'slug-edited')
        self.assertEquals(entry.status, PUBLISHED)
        self.assertEquals(entry.comment_enabled, False)
        self.assertEquals(entry.pingback_enabled, False)
        self.assertEquals(entry.categories.count(), 0)
        self.assertEquals(entry.authors.count(), 1)
        self.assertEquals(entry.authors.all()[0].pk, 2)
        self.assertEquals(entry.creation_date, datetime(2000, 1, 1))



"""Test cases for Zinnia's PingBack API"""
try:
    from urllib.error import HTTPError
    from urllib.parse import urlsplit
    from xmlrpc.client import ServerProxy
except ImportError:  # Python 2
    from urllib2 import HTTPError
    from urlparse import urlsplit
    from xmlrpclib import ServerProxy

from django.utils import six
from django.utils import timezone
from django.test import TestCase

try:
    import django_comments as comments
except ImportError:
    from django.contrib import comments

from django.contrib.sites.models import Site
from django.test.utils import restore_template_loaders
from django.test.utils import setup_test_template_loader
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.tests.utils import skipIfCustomUser

from bs4 import BeautifulSoup

from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.models.category import Category
from zinnia.flags import PINGBACK
from zinnia.managers import PUBLISHED
from zinnia.tests.utils import datetime
from zinnia.tests.utils import TestTransport
from zinnia.xmlrpc.pingback import generate_pingback_content
from zinnia import url_shortener as shortener_settings
from zinnia.signals import connect_discussion_signals
from zinnia.signals import disconnect_entry_signals
from zinnia.signals import disconnect_discussion_signals


@skipIfCustomUser
class PingBackTestCase(TestCase):
    """Test cases for pingbacks"""
    urls = 'zinnia.tests.implementations.urls.default'

    def fake_urlopen(self, url):
        """Fake urlopen using client if domain
        correspond to current_site else HTTPError"""
        scheme, netloc, path, query, fragment = urlsplit(url)
        if not netloc:
            raise
        if self.site.domain == netloc:
            response = six.BytesIO(self.client.get(url).content)
            return response
        raise HTTPError(url, 404, 'unavailable url', {}, None)

    def setUp(self):
        disconnect_entry_signals()
        disconnect_discussion_signals()
        # Use default URL shortener backend, to avoid networks errors
        self.original_shortener = shortener_settings.URL_SHORTENER_BACKEND
        shortener_settings.URL_SHORTENER_BACKEND = 'zinnia.url_shortener.'\
                                                   'backends.default'
        # Set up a stub around urlopen
        import zinnia.xmlrpc.pingback
        self.original_urlopen = zinnia.xmlrpc.pingback.urlopen
        zinnia.xmlrpc.pingback.urlopen = self.fake_urlopen
        # Set a short template for entry_detail to avoid rendering errors
        setup_test_template_loader(
            {'zinnia/entry_detail.html':
             '<html><head><title>{{ object.title }}</title></head>'
             '<body>{{ object.html_content|safe }}</body></html>',
             '404.html': '404'})
        # Preparing site
        self.site = Site.objects.get_current()
        # Creating tests entries
        self.author = Author.objects.create_user(username='webmaster',
                                                 email='webmaster@example.com')
        self.category = Category.objects.create(title='test', slug='test')
        params = {'title': 'My first entry',
                  'content': 'My first content',
                  'slug': 'my-first-entry',
                  'creation_date': datetime(2010, 1, 1, 12),
                  'status': PUBLISHED}
        self.first_entry = Entry.objects.create(**params)
        self.first_entry.sites.add(self.site)
        self.first_entry.categories.add(self.category)
        self.first_entry.authors.add(self.author)

        params = {'title': 'My second entry',
                  'content': 'My second content with link '
                  'to <a href="http://%s%s">first entry</a>'
                  ' and other links : %s %s.' % (
                      self.site.domain,
                      self.first_entry.get_absolute_url(),
                      'http://example.com/error-404/',
                      'http://external/'),
                  'slug': 'my-second-entry',
                  'creation_date': datetime(2010, 1, 1, 12),
                  'status': PUBLISHED}
        self.second_entry = Entry.objects.create(**params)
        self.second_entry.sites.add(self.site)
        self.second_entry.categories.add(self.category)
        self.second_entry.authors.add(self.author)
        # Instanciating the server proxy
        self.server = ServerProxy('http://example.com/xmlrpc/',
                                  transport=TestTransport())

    def tearDown(self):
        import zinnia.xmlrpc.pingback
        zinnia.xmlrpc.pingback.urlopen = self.original_urlopen
        shortener_settings.URL_SHORTENER_BACKEND = self.original_shortener
        restore_template_loaders()

    def test_generate_pingback_content(self):
        soup = BeautifulSoup(self.second_entry.content)
        target = 'http://%s%s' % (self.site.domain,
                                  self.first_entry.get_absolute_url())

        self.assertEqual(
            generate_pingback_content(soup, target, 1000),
            'My second content with link to first entry and other links : '
            'http://example.com/error-404/ http://external/.')
        self.assertEqual(
            generate_pingback_content(soup, target, 50),
            '...ond content with link to first entry and other lin...')

        soup = BeautifulSoup('<a href="%s">test link</a>' % target)
        self.assertEqual(
            generate_pingback_content(soup, target, 6), 'test l...')

        soup = BeautifulSoup('test <a href="%s">link</a>' % target)
        self.assertEqual(
            generate_pingback_content(soup, target, 8), '...est link')
        self.assertEqual(
            generate_pingback_content(soup, target, 9), 'test link')

    def test_pingback_ping(self):
        target = 'http://%s%s' % (
            self.site.domain, self.first_entry.get_absolute_url())
        source = 'http://%s%s' % (
            self.site.domain, self.second_entry.get_absolute_url())

        # Error code 0 : A generic fault code
        response = self.server.pingback.ping('toto', 'titi')
        self.assertEqual(response, 0)
        response = self.server.pingback.ping('http://%s/' % self.site.domain,
                                             'http://%s/' % self.site.domain)
        self.assertEqual(response, 0)

        # Error code 16 : The source URI does not exist.
        response = self.server.pingback.ping('http://external/', target)
        self.assertEqual(response, 16)

        # Error code 17 : The source URI does not contain a link to
        # the target URI and so cannot be used as a source.
        response = self.server.pingback.ping(source, 'toto')
        self.assertEqual(response, 17)

        # Error code 32 : The target URI does not exist.
        response = self.server.pingback.ping(
            source, 'http://example.com/error-404/')
        self.assertEqual(response, 32)
        response = self.server.pingback.ping(source, 'http://external/')
        self.assertEqual(response, 32)

        # Error code 33 : The target URI cannot be used as a target.
        response = self.server.pingback.ping(source, 'http://example.com/')
        self.assertEqual(response, 33)
        self.first_entry.pingback_enabled = False
        self.first_entry.save()
        response = self.server.pingback.ping(source, target)
        self.assertEqual(response, 33)

        # Validate pingback
        self.assertEqual(self.first_entry.pingback_count, 0)
        self.first_entry.pingback_enabled = True
        self.first_entry.save()
        connect_discussion_signals()
        response = self.server.pingback.ping(source, target)
        disconnect_discussion_signals()
        self.assertEqual(
            response,
            'Pingback from %s to %s registered.' % (source, target))
        first_entry_reloaded = Entry.objects.get(pk=self.first_entry.pk)
        self.assertEqual(first_entry_reloaded.pingback_count, 1)
        self.assertTrue(self.second_entry.title in
                        self.first_entry.pingbacks[0].user_name)

        # Error code 48 : The pingback has already been registered.
        response = self.server.pingback.ping(source, target)
        self.assertEqual(response, 48)

    def test_pingback_ping_on_entry_without_author(self):
        target = 'http://%s%s' % (
            self.site.domain, self.first_entry.get_absolute_url())
        source = 'http://%s%s' % (
            self.site.domain, self.second_entry.get_absolute_url())
        self.first_entry.pingback_enabled = True
        self.first_entry.save()
        self.first_entry.authors.clear()
        connect_discussion_signals()
        response = self.server.pingback.ping(source, target)
        disconnect_discussion_signals()
        self.assertEqual(
            response,
            'Pingback from %s to %s registered.' % (source, target))
        first_entry_reloaded = Entry.objects.get(pk=self.first_entry.pk)
        self.assertEqual(first_entry_reloaded.pingback_count, 1)
        self.assertTrue(self.second_entry.title in
                        self.first_entry.pingbacks[0].user_name)

    def test_pingback_extensions_get_pingbacks(self):
        target = 'http://%s%s' % (
            self.site.domain, self.first_entry.get_absolute_url())
        source = 'http://%s%s' % (
            self.site.domain, self.second_entry.get_absolute_url())

        response = self.server.pingback.ping(source, target)
        self.assertEqual(
            response, 'Pingback from %s to %s registered.' % (source, target))

        response = self.server.pingback.extensions.getPingbacks(
            'http://external/')
        self.assertEqual(response, 32)

        response = self.server.pingback.extensions.getPingbacks(
            'http://example.com/error-404/')
        self.assertEqual(response, 32)

        response = self.server.pingback.extensions.getPingbacks(
            'http://example.com/2010/')
        self.assertEqual(response, 33)

        response = self.server.pingback.extensions.getPingbacks(source)
        self.assertEqual(response, [])

        response = self.server.pingback.extensions.getPingbacks(target)
        self.assertEqual(response, [
            'http://example.com/2010/01/01/my-second-entry/'])

        comment = comments.get_model().objects.create(
            content_type=ContentType.objects.get_for_model(Entry),
            object_pk=self.first_entry.pk,
            site=self.site, submit_date=timezone.now(),
            comment='Test pingback',
            user_url='http://external/blog/1/',
            user_name='Test pingback')
        comment.flags.create(user=self.author, flag=PINGBACK)

        response = self.server.pingback.extensions.getPingbacks(target)
        self.assertEqual(response, [
            'http://example.com/2010/01/01/my-second-entry/',
            'http://external/blog/1/'])

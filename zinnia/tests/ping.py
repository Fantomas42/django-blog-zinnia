"""Test cases for Zinnia's ping"""
import cStringIO
from urllib2 import URLError
from urllib import addinfourl
from django.test import TestCase

from zinnia.models.entry import Entry
from zinnia.ping import URLRessources
from zinnia.ping import DirectoryPinger
from zinnia.ping import ExternalUrlsPinger


class DirectoryPingerTestCase(TestCase):
    """Test cases for DirectoryPinger"""
    def setUp(self):
        params = {'title': 'My entry',
                  'content': 'My content',
                  'tags': 'zinnia, test',
                  'slug': 'my-entry'}
        self.entry = Entry.objects.create(**params)
        self.pinger = DirectoryPinger('http://localhost', [self.entry],
                                      start_now=False)

    def test_ping_entry(self):
        self.assertEquals(
            self.pinger.ping_entry(self.entry),
            {'message': 'http://localhost is an invalid directory.',
             'flerror': True})


class ExternalUrlsPingerTestCase(TestCase):
    """Test cases for ExternalUrlsPinger"""

    def setUp(self):
        params = {'title': 'My entry',
                  'content': 'My content',
                  'tags': 'zinnia, test',
                  'slug': 'my-entry'}
        self.entry = Entry.objects.create(**params)
        self.pinger = ExternalUrlsPinger(self.entry, start_now=False)

    def test_is_external_url(self):
        r = URLRessources()
        self.assertEquals(self.pinger.is_external_url(
            'http://example.com/', 'http://google.com/'), True)
        self.assertEquals(self.pinger.is_external_url(
            'http://example.com/toto/', 'http://google.com/titi/'), True)
        self.assertEquals(self.pinger.is_external_url(
            'http://example.com/blog/', 'http://example.com/page/'), False)
        self.assertEquals(self.pinger.is_external_url(
            '%s/blog/' % r.site_url, r.site_url), False)
        self.assertEquals(self.pinger.is_external_url(
            'http://google.com/', r.site_url), True)
        self.assertEquals(self.pinger.is_external_url(
            '/blog/', r.site_url), False)

    def test_find_external_urls(self):
        r = URLRessources()
        external_urls = self.pinger.find_external_urls(self.entry)
        self.assertEquals(external_urls, [])
        self.entry.content = """
        <p>This is a <a href="http://fantomas.willbreak.it/">link</a>
        to a site.</p>
        <p>This is a <a href="%s/blog/">link</a> within my site.</p>
        <p>This is a <a href="/blog/">relative link</a> within my site.</p>
        """ % r.site_url
        self.entry.save()
        external_urls = self.pinger.find_external_urls(self.entry)
        self.assertEquals(external_urls, ['http://fantomas.willbreak.it/'])

    def test_find_pingback_href(self):
        result = self.pinger.find_pingback_href('')
        self.assertEquals(result, None)
        result = self.pinger.find_pingback_href("""
        <html><head><link rel="pingback" href="/xmlrpc/" /></head>
        <body></body></html>
        """)
        self.assertEquals(result, '/xmlrpc/')
        result = self.pinger.find_pingback_href("""
        <html><head><LINK hrEF="/xmlrpc/" REL="PingBack" /></head>
        <body></body></html>
        """)
        self.assertEquals(result, '/xmlrpc/')
        result = self.pinger.find_pingback_href("""
        <html><head><LINK REL="PingBack" /></head><body></body></html>
        """)
        self.assertEquals(result, None)

    def fake_urlopen(self, url):
        """Fake urlopen using test client"""
        if 'example' in url:
            response = cStringIO.StringIO('')
            return addinfourl(response, {'X-Pingback': '/xmlrpc.php',
                                         'Content-Type': 'text/html'}, url)
        elif 'localhost' in url:
            response = cStringIO.StringIO(
                '<link rel="pingback" href="/xmlrpc/">')
            return addinfourl(response, {'Content-Type': 'text/xhtml'}, url)
        elif 'google' in url:
            response = cStringIO.StringIO('PNG CONTENT')
            return addinfourl(response, {'content-type': 'image/png'}, url)
        elif 'error' in url:
            raise URLError('Invalid ressource')

    def test_find_pingback_urls(self):
        # Set up a stub around urlopen
        import zinnia.ping
        self.original_urlopen = zinnia.ping.urlopen
        zinnia.ping.urlopen = self.fake_urlopen

        urls = ['http://localhost/', 'http://example.com/', 'http://error',
                'http://www.google.co.uk/images/nav_logo72.png']
        self.assertEquals(
            self.pinger.find_pingback_urls(urls),
            {'http://localhost/': 'http://localhost/xmlrpc/',
             'http://example.com/': 'http://example.com/xmlrpc.php'})
        # Remove stub
        zinnia.ping.urlopen = self.original_urlopen

    def test_pingback_url(self):
        self.assertEquals(self.pinger.pingback_url('http://localhost',
                                                   'http://error.com'),
                          'http://error.com cannot be pinged.')

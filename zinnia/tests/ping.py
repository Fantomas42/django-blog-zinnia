"""Test cases for Zinnia's ping"""
try:
    from urllib import addinfourl
except ImportError:
    from urllib.response import addinfourl

try:
    from io import StringIO
    from urllib.error import URLError
except ImportError:  # Python 2
    from cStringIO import StringIO
    from urllib2 import URLError

from django.test import TestCase

from zinnia.models.entry import Entry
from zinnia.ping import URLRessources
from zinnia.ping import DirectoryPinger
from zinnia.ping import ExternalUrlsPinger


class NoThreadMixin(object):
    def start(self):
        self.run()


class NoThreadDirectoryPinger(NoThreadMixin, DirectoryPinger):
    pass


class NoThreadExternalUrlsPinger(NoThreadMixin, ExternalUrlsPinger):
    pass


class DirectoryPingerTestCase(TestCase):
    """Test cases for DirectoryPinger"""
    def setUp(self):
        params = {'title': 'My entry',
                  'content': 'My content',
                  'tags': 'zinnia, test',
                  'slug': 'my-entry'}
        self.entry = Entry.objects.create(**params)

    def test_ping_entry(self):
        pinger = NoThreadDirectoryPinger('http://localhost', [self.entry],
                                         start_now=False)
        self.assertEqual(
            pinger.ping_entry(self.entry),
            {'message': 'http://localhost is an invalid directory.',
             'flerror': True})
        self.assertEqual(pinger.results, [])

    def test_run(self):
        pinger = NoThreadDirectoryPinger('http://localhost', [self.entry])
        self.assertEqual(
            pinger.results,
            [{'flerror': True,
              'message': 'http://localhost is an invalid directory.'}])


class ExternalUrlsPingerTestCase(TestCase):
    """Test cases for ExternalUrlsPinger"""

    def setUp(self):
        params = {'title': 'My entry',
                  'content': 'My content',
                  'tags': 'zinnia, test',
                  'slug': 'my-entry'}
        self.entry = Entry.objects.create(**params)

    def test_is_external_url(self):
        r = URLRessources()
        pinger = ExternalUrlsPinger(self.entry, start_now=False)
        self.assertEqual(pinger.is_external_url(
            'http://example.com/', 'http://google.com/'), True)
        self.assertEqual(pinger.is_external_url(
            'http://example.com/toto/', 'http://google.com/titi/'), True)
        self.assertEqual(pinger.is_external_url(
            'http://example.com/blog/', 'http://example.com/page/'), False)
        self.assertEqual(pinger.is_external_url(
            '%s/blog/' % r.site_url, r.site_url), False)
        self.assertEqual(pinger.is_external_url(
            'http://google.com/', r.site_url), True)
        self.assertEqual(pinger.is_external_url(
            '/blog/', r.site_url), False)

    def test_find_external_urls(self):
        r = URLRessources()
        pinger = ExternalUrlsPinger(self.entry, start_now=False)
        external_urls = pinger.find_external_urls(self.entry)
        self.assertEqual(external_urls, [])
        self.entry.content = """
        <p>This is a <a href="http://fantomas.willbreak.it/">link</a>
        to a site.</p>
        <p>This is a <a href="%s/blog/">link</a> within my site.</p>
        <p>This is a <a href="/blog/">relative link</a> within my site.</p>
        """ % r.site_url
        self.entry.save()
        external_urls = pinger.find_external_urls(self.entry)
        self.assertEqual(external_urls, ['http://fantomas.willbreak.it/'])

    def test_find_pingback_href(self):
        pinger = ExternalUrlsPinger(self.entry, start_now=False)
        result = pinger.find_pingback_href('')
        self.assertEqual(result, None)
        result = pinger.find_pingback_href("""
        <html><head><link rel="pingback" href="/xmlrpc/" /></head>
        <body></body></html>
        """)
        self.assertEqual(result, '/xmlrpc/')
        result = pinger.find_pingback_href("""
        <html><head><LINK hrEF="/xmlrpc/" REL="PingBack" /></head>
        <body></body></html>
        """)
        self.assertEqual(result, '/xmlrpc/')
        result = pinger.find_pingback_href("""
        <html><head><LINK REL="PingBack" /></head><body></body></html>
        """)
        self.assertEqual(result, None)

    def fake_urlopen(self, url):
        """Fake urlopen using test client"""
        if 'example' in url:
            response = StringIO('')
            return addinfourl(response, {'X-Pingback': '/xmlrpc.php',
                                         'Content-Type': 'text/html'}, url)
        elif 'localhost' in url:
            response = StringIO(
                '<link rel="pingback" href="/xmlrpc/">')
            return addinfourl(response, {'Content-Type': 'text/xhtml'}, url)
        elif 'google' in url:
            response = StringIO('PNG CONTENT')
            return addinfourl(response, {'content-type': 'image/png'}, url)
        elif 'error' in url:
            raise URLError('Invalid ressource')

    def test_pingback_url(self):
        pinger = ExternalUrlsPinger(self.entry, start_now=False)
        self.assertEqual(
            pinger.pingback_url('http://localhost',
                                'http://error.com'),
            'http://error.com cannot be pinged.')

    def test_find_pingback_urls(self):
        # Set up a stub around urlopen
        import zinnia.ping
        self.original_urlopen = zinnia.ping.urlopen
        zinnia.ping.urlopen = self.fake_urlopen
        pinger = ExternalUrlsPinger(self.entry, start_now=False)

        urls = ['http://localhost/', 'http://example.com/', 'http://error',
                'http://www.google.co.uk/images/nav_logo72.png']
        self.assertEqual(
            pinger.find_pingback_urls(urls),
            {'http://localhost/': 'http://localhost/xmlrpc/',
             'http://example.com/': 'http://example.com/xmlrpc.php'})
        # Remove stub
        zinnia.ping.urlopen = self.original_urlopen

    def test_run(self):
        import zinnia.ping
        self.original_urlopen = zinnia.ping.urlopen
        zinnia.ping.urlopen = self.fake_urlopen
        self.entry.content = """
        <a href="http://localhost/">Localhost</a>
        <a href="http://example.com/">Example</a>
        <a href="http://error">Error</a>
        <a href="http://www.google.co.uk/images/nav_logo72.png">Img</a>
        """
        pinger = NoThreadExternalUrlsPinger(self.entry)
        self.assertEqual(pinger.results, [
            'http://localhost/ cannot be pinged.'])
        zinnia.ping.urlopen = self.original_urlopen

"""Pings utilities for Zinnia"""
import socket
import xmlrpclib
import threading
from urllib2 import urlopen
from urlparse import urlsplit

from BeautifulSoup import BeautifulSoup

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from zinnia.settings import PROTOCOL

CURRENT_SITE = Site.objects.get_current()
SITE = '%s://%s' % (PROTOCOL, CURRENT_SITE.domain)
BLOG_URL = ''
BLOG_FEED = ''


class DirectoryPinger(threading.Thread):
    """Threaded Directory Pinger"""

    def __init__(self, server_name, entries, timeout=10, start_now=True):
        global BLOG_URL, BLOG_FEED

        self.results = []
        self.timeout = timeout
        self.entries = entries
        self.server_name = server_name
        self.server = xmlrpclib.ServerProxy(self.server_name)

        if not BLOG_URL or not BLOG_FEED:
            BLOG_URL = '%s%s' % (SITE, reverse('zinnia_entry_archive_index'))
            BLOG_FEED = '%s%s' % (SITE, reverse('zinnia_entry_latest_feed'))

        threading.Thread.__init__(self)
        if start_now:
            self.start()

    def run(self):
        """Ping entries to a Directory in a Thread"""
        socket.setdefaulttimeout(self.timeout)
        for entry in self.entries:
            reply = self.ping_entry(entry)
            self.results.append(reply)
        socket.setdefaulttimeout(None)

    def ping_entry(self, entry):
        """Ping an entry to a Directory"""
        entry_url = '%s%s' % (SITE, entry.get_absolute_url())
        categories = '|'.join([c.title for c in entry.categories.all()])

        try:
            reply = self.server.weblogUpdates.extendedPing(CURRENT_SITE.name,
                                                           BLOG_URL, entry_url,
                                                           BLOG_FEED,
                                                           categories)
        except Exception:
            try:
                reply = self.server.weblogUpdates.ping(CURRENT_SITE.name,
                                                       BLOG_URL, entry_url,
                                                       categories)
            except Exception:
                reply = {'message': '%s is an invalid directory.' % \
                         self.server_name,
                         'flerror': True}
        return reply


class ExternalUrlsPinger(threading.Thread):
    """Threaded ExternalUrls Pinger"""

    def __init__(self, entry, timeout=10, start_now=True):
        self.results = []
        self.entry = entry
        self.timeout = timeout
        self.entry_url = '%s%s' % (SITE, self.entry.get_absolute_url())

        threading.Thread.__init__(self)
        if start_now:
            self.start()

    def run(self):
        """Ping external URLS in a Thread"""
        socket.setdefaulttimeout(self.timeout)

        external_urls = self.find_external_urls(self.entry)
        external_urls_pingable = self.find_pingback_urls(external_urls)

        for url, server_name in external_urls_pingable.items():
            reply = self.pingback_url(server_name, url)
            self.results.append(reply)

        socket.setdefaulttimeout(None)

    def is_external_url(self, url, site_url=SITE):
        """Check of the url in an external url"""
        url_splitted = urlsplit(url)
        if not url_splitted.netloc:
            return False
        return url_splitted.netloc != urlsplit(site_url).netloc

    def find_external_urls(self, entry):
        """Find external urls in an entry"""
        soup = BeautifulSoup(entry.html_content)
        external_urls = [a['href'] for a in soup.findAll('a')
                         if self.is_external_url(a['href'])]
        return external_urls

    def find_pingback_href(self, content):
        """Try to find Link markup to pingback url"""
        soup = BeautifulSoup(content)
        for link in soup.findAll('link'):
            dict_attr = dict(link.attrs)
            if 'rel' in dict_attr and 'href' in dict_attr:
                if dict_attr['rel'].lower() == 'pingback':
                    return dict_attr.get('href')

    def find_pingback_urls(self, urls):
        """Find the pingback urls of each urls"""
        pingback_urls = {}

        for url in urls:
            try:
                page = urlopen(url)
                server_url = page.info().get('X-Pingback') or \
                             self.find_pingback_href(page.read())
                if server_url:
                    server_url_splitted = urlsplit(server_url)
                    if not server_url_splitted.netloc:
                        url_splitted = urlsplit(url)
                        server_url = '%s://%s%s' % (url_splitted.scheme,
                                                    url_splitted.netloc,
                                                    server_url)
                    pingback_urls[url] = server_url
            except IOError:
                pass
        return pingback_urls

    def pingback_url(self, server_name, target_url):
        """Do a pingback call for the target url"""
        try:
            server = xmlrpclib.ServerProxy(server_name)
            reply = server.pingback.ping(self.entry_url, target_url)
        except xmlrpclib.Error:
            reply = '%s cannot be pinged.' % target_url
        return reply

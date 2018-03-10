"""Pings utilities for Zinnia"""
import socket
from logging import getLogger
from threading import Thread
from urllib.parse import urlsplit
from urllib.request import urlopen
from xmlrpc.client import Error
from xmlrpc.client import ServerProxy

from bs4 import BeautifulSoup

from django.contrib.sites.models import Site
from django.urls import reverse

from zinnia.flags import PINGBACK
from zinnia.settings import PROTOCOL


class URLRessources(object):
    """
    Object defining the ressources of the Website.
    """

    def __init__(self):
        self.current_site = Site.objects.get_current()
        self.site_url = '%s://%s' % (PROTOCOL, self.current_site.domain)
        self.blog_url = '%s%s' % (self.site_url,
                                  reverse('zinnia:entry_archive_index'))
        self.blog_feed = '%s%s' % (self.site_url,
                                   reverse('zinnia:entry_feed'))


class DirectoryPinger(Thread):
    """
    Threaded web directory pinger.
    """

    def __init__(self, server_name, entries, timeout=10):
        self.results = []
        self.timeout = timeout
        self.entries = entries
        self.server_name = server_name
        self.server = ServerProxy(self.server_name)
        self.ressources = URLRessources()

        super(DirectoryPinger, self).__init__()
        self.start()

    def run(self):
        """
        Ping entries to a directory in a thread.
        """
        logger = getLogger('zinnia.ping.directory')
        socket.setdefaulttimeout(self.timeout)
        for entry in self.entries:
            reply = self.ping_entry(entry)
            self.results.append(reply)
            logger.info('%s : %s', self.server_name, reply['message'])
        socket.setdefaulttimeout(None)

    def ping_entry(self, entry):
        """
        Ping an entry to a directory.
        """
        entry_url = '%s%s' % (self.ressources.site_url,
                              entry.get_absolute_url())
        categories = '|'.join([c.title for c in entry.categories.all()])

        try:
            reply = self.server.weblogUpdates.extendedPing(
                self.ressources.current_site.name,
                self.ressources.blog_url, entry_url,
                self.ressources.blog_feed, categories)
        except Exception:
            try:
                reply = self.server.weblogUpdates.ping(
                    self.ressources.current_site.name,
                    self.ressources.blog_url, entry_url,
                    categories)
            except Exception:
                reply = {'message': '%s is an invalid directory.' %
                         self.server_name,
                         'flerror': True}
        return reply


class ExternalUrlsPinger(Thread):
    """
    Threaded external URLs pinger.
    """

    def __init__(self, entry, timeout=10):
        self.results = []
        self.entry = entry
        self.timeout = timeout
        self.ressources = URLRessources()
        self.entry_url = '%s%s' % (self.ressources.site_url,
                                   self.entry.get_absolute_url())

        super(ExternalUrlsPinger, self).__init__()
        self.start()

    def run(self):
        """
        Ping external URLs in a Thread.
        """
        logger = getLogger('zinnia.ping.external_urls')
        socket.setdefaulttimeout(self.timeout)

        external_urls = self.find_external_urls(self.entry)
        external_urls_pingable = self.find_pingback_urls(external_urls)

        for url, server_name in external_urls_pingable.items():
            reply = self.pingback_url(server_name, url)
            self.results.append(reply)
            logger.info('%s : %s', url, reply)

        socket.setdefaulttimeout(None)

    def is_external_url(self, url, site_url):
        """
        Check if the URL is an external URL.
        """
        url_splitted = urlsplit(url)
        if not url_splitted.netloc:
            return False
        return url_splitted.netloc != urlsplit(site_url).netloc

    def find_external_urls(self, entry):
        """
        Find external URLs in an entry.
        """
        soup = BeautifulSoup(entry.html_content, 'html.parser')
        external_urls = [a['href'] for a in soup.find_all('a')
                         if self.is_external_url(
                             a['href'], self.ressources.site_url)]
        return external_urls

    def find_pingback_href(self, content):
        """
        Try to find LINK markups to pingback URL.
        """
        soup = BeautifulSoup(content, 'html.parser')
        for link in soup.find_all('link'):
            dict_attr = dict(link.attrs)
            if 'rel' in dict_attr and 'href' in dict_attr:
                for rel_type in dict_attr['rel']:
                    if rel_type.lower() == PINGBACK:
                        return dict_attr.get('href')

    def find_pingback_urls(self, urls):
        """
        Find the pingback URL for each URLs.
        """
        pingback_urls = {}

        for url in urls:
            try:
                page = urlopen(url)
                headers = page.info()

                server_url = headers.get('X-Pingback')

                if not server_url:
                    content_type = headers.get('Content-Type', '').split(
                        ';')[0].strip().lower()
                    if content_type in ['text/html', 'application/xhtml+xml']:
                        server_url = self.find_pingback_href(
                            page.read(5 * 1024))

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
        """
        Do a pingback call for the target URL.
        """
        try:
            server = ServerProxy(server_name)
            reply = server.pingback.ping(self.entry_url, target_url)
        except (Error, socket.error):
            reply = '%s cannot be pinged.' % target_url
        return reply

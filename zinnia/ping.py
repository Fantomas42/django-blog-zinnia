"""Pings utilities for Zinnia"""
import socket
import xmlrpclib
import threading

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse


current_site = Site.objects.get_current()
site = 'http://%s' % current_site.domain
blog_url = ''
blog_feed = ''

class DirectoryPinger(threading.Thread):
    """Threaded Directory Pinger"""

    def __init__(self, server_name, entries, timeout=10):
        global blog_url, blog_feed

        self.results = []
        self.timeout = timeout
        self.entries = entries
        self.server_name = server_name
        self.server = xmlrpclib.ServerProxy(self.server_name)

        if not blog_url or not blog_feed:
            blog_url = '%s%s' % (site, reverse('zinnia_entry_archive_index'))
            blog_feed = '%s%s' % (site, reverse('zinnia_entry_latest_feed'))

        threading.Thread.__init__(self)
        self.start()

    def run(self):
        socket.setdefaulttimeout(self.timeout)
        for entry in self.entries:
            reply = self.ping_entry(entry)
            self.results.append(reply)
        socket.setdefaulttimeout(None)

    def ping_entry(self, entry):
        entry_url = '%s%s' % (site, entry.get_absolute_url())
        categories = '|'.join([c.title for c in entry.categories.all()])

        try:
            reply = self.server.weblogUpdates.extendedPing(current_site.name,
                                                           blog_url, entry_url,
                                                           blog_feed, categories)
        except Exception, ex:
            try:
                reply = self.server.weblogUpdates.ping(current_site.name,
                                                       blog_url, entry_url,
                                                       categories)
            except xmlrpclib.ProtocolError, ex:
                reply = {'message': '%s is an invalid directory.' % self.server_name,
                         'flerror': True}
        return reply

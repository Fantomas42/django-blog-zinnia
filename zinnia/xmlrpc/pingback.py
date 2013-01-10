"""XML-RPC methods of Zinnia Pingback"""
from urllib2 import urlopen
from urllib2 import URLError
from urllib2 import HTTPError
from urlparse import urlsplit

from django.contrib import comments
from django.utils.html import strip_tags
from django.contrib.sites.models import Site
from django.core.urlresolvers import resolve
from django.core.urlresolvers import Resolver404
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType

from zinnia.models.entry import Entry
from zinnia.flags import PINGBACK
from zinnia.flags import get_user_flagger
from zinnia.signals import pingback_was_posted
from zinnia.settings import PINGBACK_CONTENT_LENGTH

from BeautifulSoup import BeautifulSoup
from django_xmlrpc.decorators import xmlrpc_func

UNDEFINED_ERROR = 0
SOURCE_DOES_NOT_EXIST = 16
SOURCE_DOES_NOT_LINK = 17
TARGET_DOES_NOT_EXIST = 32
TARGET_IS_NOT_PINGABLE = 33
PINGBACK_ALREADY_REGISTERED = 48


def generate_pingback_content(soup, target, max_length, trunc_char='...'):
    """Generate a description text for the pingback"""
    link = soup.find('a', href=target)

    content = strip_tags(unicode(link.findParent()))
    index = content.index(link.string)

    if len(content) > max_length:
        middle = max_length / 2
        start = index - middle
        end = index + middle

        if start <= 0:
            end -= start
            extract = content[0:end]
        else:
            extract = '%s%s' % (trunc_char, content[start:end])

        if end < len(content):
            extract += trunc_char
        return extract

    return content


@xmlrpc_func(returns='string', args=['string', 'string'])
def pingback_ping(source, target):
    """pingback.ping(sourceURI, targetURI) => 'Pingback message'

    Notifies the server that a link has been added to sourceURI,
    pointing to targetURI.

    See: http://hixie.ch/specs/pingback/pingback-1.0"""
    try:
        if source == target:
            return UNDEFINED_ERROR

        site = Site.objects.get_current()
        try:
            document = ''.join(urlopen(source).readlines())
        except (HTTPError, URLError):
            return SOURCE_DOES_NOT_EXIST

        if not target in document:
            return SOURCE_DOES_NOT_LINK

        scheme, netloc, path, query, fragment = urlsplit(target)
        if netloc != site.domain:
            return TARGET_DOES_NOT_EXIST

        try:
            view, args, kwargs = resolve(path)
        except Resolver404:
            return TARGET_DOES_NOT_EXIST

        try:
            entry = Entry.published.get(
                slug=kwargs['slug'],
                creation_date__year=kwargs['year'],
                creation_date__month=kwargs['month'],
                creation_date__day=kwargs['day'])
            if not entry.pingbacks_are_open:
                return TARGET_IS_NOT_PINGABLE
        except (KeyError, Entry.DoesNotExist):
            return TARGET_IS_NOT_PINGABLE

        soup = BeautifulSoup(document)
        title = soup.find('title')
        title = title and strip_tags(title) or _('No title')
        description = generate_pingback_content(soup, target,
                                                PINGBACK_CONTENT_LENGTH)

        pingback, created = comments.get_model().objects.get_or_create(
            content_type=ContentType.objects.get_for_model(Entry),
            object_pk=entry.pk, user_url=source, site=site,
            defaults={'comment': description, 'user_name': title})
        if created:
            pingback.flags.create(user=get_user_flagger(), flag=PINGBACK)
            pingback_was_posted.send(pingback.__class__,
                                     pingback=pingback,
                                     entry=entry)
            return 'Pingback from %s to %s registered.' % (source, target)
        return PINGBACK_ALREADY_REGISTERED
    except:
        return UNDEFINED_ERROR


@xmlrpc_func(returns='string[]', args=['string'])
def pingback_extensions_get_pingbacks(target):
    """pingback.extensions.getPingbacks(url) => '[url, url, ...]'

    Returns an array of URLs that link to the specified url.

    See: http://www.aquarionics.com/misc/archives/blogite/0198.html"""
    site = Site.objects.get_current()

    scheme, netloc, path, query, fragment = urlsplit(target)
    if netloc != site.domain:
        return TARGET_DOES_NOT_EXIST

    try:
        view, args, kwargs = resolve(path)
    except Resolver404:
        return TARGET_DOES_NOT_EXIST

    try:
        entry = Entry.published.get(
            slug=kwargs['slug'],
            creation_date__year=kwargs['year'],
            creation_date__month=kwargs['month'],
            creation_date__day=kwargs['day'])
    except (KeyError, Entry.DoesNotExist):
        return TARGET_IS_NOT_PINGABLE

    return [pingback.user_url for pingback in entry.pingbacks]

"""XML-RPC methods of Zinnia Pingback"""
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import urlopen

from bs4 import BeautifulSoup

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.urls import Resolver404
from django.urls import resolve
from django.utils.html import strip_tags
from django.utils.translation import gettext as _

import django_comments as comments

from django_xmlrpc.decorators import xmlrpc_func

from zinnia.flags import PINGBACK
from zinnia.flags import get_user_flagger
from zinnia.models.entry import Entry
from zinnia.settings import PINGBACK_CONTENT_LENGTH
from zinnia.signals import pingback_was_posted
from zinnia.spam_checker import check_is_spam

UNDEFINED_ERROR = 0
SOURCE_DOES_NOT_EXIST = 16
SOURCE_DOES_NOT_LINK = 17
TARGET_DOES_NOT_EXIST = 32
TARGET_IS_NOT_PINGABLE = 33
PINGBACK_ALREADY_REGISTERED = 48
PINGBACK_IS_SPAM = 51


class FakeRequest(object):
    META = {}


def generate_pingback_content(soup, target, max_length, trunc_char='...'):
    """
    Generate a description text for the pingback.
    """
    link = soup.find('a', href=target)

    content = strip_tags(str(link.findParent()))
    index = content.index(link.string)

    if len(content) > max_length:
        middle = max_length // 2
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
    """
    pingback.ping(sourceURI, targetURI) => 'Pingback message'

    Notifies the server that a link has been added to sourceURI,
    pointing to targetURI.

    See: http://hixie.ch/specs/pingback/pingback-1.0
    """
    try:
        if source == target:
            return UNDEFINED_ERROR

        site = Site.objects.get_current()
        try:
            document = ''.join(map(
                lambda byte_line: byte_line.decode('utf-8'),
                urlopen(source).readlines()))
        except (HTTPError, URLError):
            return SOURCE_DOES_NOT_EXIST

        if target not in document:
            return SOURCE_DOES_NOT_LINK

        target_splitted = urlsplit(target)
        if target_splitted.netloc != site.domain:
            return TARGET_DOES_NOT_EXIST

        try:
            view, args, kwargs = resolve(target_splitted.path)
        except Resolver404:
            return TARGET_DOES_NOT_EXIST

        try:
            entry = Entry.published.get(
                slug=kwargs['slug'],
                publication_date__year=kwargs['year'],
                publication_date__month=kwargs['month'],
                publication_date__day=kwargs['day'])
            if not entry.pingbacks_are_open:
                return TARGET_IS_NOT_PINGABLE
        except (KeyError, Entry.DoesNotExist):
            return TARGET_IS_NOT_PINGABLE

        soup = BeautifulSoup(document, 'html.parser')
        title = str(soup.find('title'))
        title = title and strip_tags(title) or _('No title')
        description = generate_pingback_content(soup, target,
                                                PINGBACK_CONTENT_LENGTH)

        pingback_klass = comments.get_model()
        pingback_datas = {
            'content_type': ContentType.objects.get_for_model(Entry),
            'object_pk': entry.pk,
            'site': site,
            'user_url': source,
            'user_name': title,
            'comment': description
        }
        pingback = pingback_klass(**pingback_datas)
        if check_is_spam(pingback, entry, FakeRequest()):
            return PINGBACK_IS_SPAM

        pingback_defaults = {'comment': pingback_datas.pop('comment'),
                             'user_name': pingback_datas.pop('user_name')}
        pingback, created = pingback_klass.objects.get_or_create(
            defaults=pingback_defaults,
            **pingback_datas)
        if created:
            pingback.flags.create(user=get_user_flagger(), flag=PINGBACK)
            pingback_was_posted.send(pingback.__class__,
                                     pingback=pingback,
                                     entry=entry)
            return 'Pingback from %s to %s registered.' % (source, target)
        return PINGBACK_ALREADY_REGISTERED
    except Exception:
        return UNDEFINED_ERROR


@xmlrpc_func(returns='string[]', args=['string'])
def pingback_extensions_get_pingbacks(target):
    """
    pingback.extensions.getPingbacks(url) => '[url, url, ...]'

    Returns an array of URLs that link to the specified url.

    See: http://www.aquarionics.com/misc/archives/blogite/0198.html
    """
    site = Site.objects.get_current()

    target_splitted = urlsplit(target)
    if target_splitted.netloc != site.domain:
        return TARGET_DOES_NOT_EXIST

    try:
        view, args, kwargs = resolve(target_splitted.path)
    except Resolver404:
        return TARGET_DOES_NOT_EXIST

    try:
        entry = Entry.published.get(
            slug=kwargs['slug'],
            publication_date__year=kwargs['year'],
            publication_date__month=kwargs['month'],
            publication_date__day=kwargs['day'])
    except (KeyError, Entry.DoesNotExist):
        return TARGET_IS_NOT_PINGABLE

    return [pingback.user_url for pingback in entry.pingbacks]

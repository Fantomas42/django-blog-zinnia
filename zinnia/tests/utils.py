"""Utils for Zinnia's tests"""
import functools
from datetime import datetime as original_datetime
from io import BytesIO
from unittest import SkipTest
from unittest import skipIf
from urllib.parse import parse_qs
from urllib.parse import urlparse
from xmlrpc.client import Transport

from django.conf import settings
from django.template import Origin
from django.template.loaders.base import Loader
from django.test.client import Client
from django.utils import timezone


class TestTransport(Transport):
    """
    Handles connections to XML-RPC server through Django test client.
    """

    def __init__(self, *args, **kwargs):
        Transport.__init__(self, *args, **kwargs)
        self.client = Client()

    def request(self, host, handler, request_body, verbose=0):
        self.verbose = verbose
        response = self.client.post(handler,
                                    request_body,
                                    content_type="text/xml")
        res = BytesIO(response.content)
        setattr(res, 'getheader', lambda *args: '')  # For Python >= 2.7
        res.seek(0)
        return self.parse_response(res)


def omniscient_datetime(*args):
    """
    Generating a datetime aware or naive depending of USE_TZ.
    """
    d = original_datetime(*args)
    if settings.USE_TZ:
        d = timezone.make_aware(d, timezone.utc)
    return d


datetime = omniscient_datetime


def is_lib_available(library):
    """
    Check if a Python library is available.
    """
    try:
        __import__(library)
        return True
    except ImportError:
        return False


def skip_if_lib_not_available(lib):
    """
    Skip a test if a lib is not available
    """
    def decorator(test_func):
        @functools.wraps(test_func)
        def f(*args, **kwargs):
            if not is_lib_available(lib):
                raise SkipTest('%s is not available' % lib.title())
            return test_func(*args, **kwargs)
        return f
    return decorator


def skip_if_custom_user(test_func):
    """
    Skip a test if a custom user model is in use.
    """
    return skipIf(settings.AUTH_USER_MODEL != 'auth.User',
                  'Custom user model in use')(test_func)


def url_equal(url_1, url_2):
    """
    Compare two URLs with query string where
    ordering does not matter.
    """
    parse_result_1 = urlparse(url_1)
    parse_result_2 = urlparse(url_2)

    return (parse_result_1[:4] == parse_result_2[:4] and
            parse_qs(parse_result_1[5]) == parse_qs(parse_result_2[5]))


class VoidLoader(Loader):
    """
    Template loader which is always returning
    an empty template.
    """
    is_usable = True
    _accepts_engine_in_init = True

    def get_template_sources(self, template_name):
        yield Origin(
            name='voidloader',
            template_name=template_name,
            loader=self)

    def get_contents(self, origin):
        return ''


class EntryDetailLoader(Loader):
    """
    Template loader which only return the content
    of an entry detail template.
    """
    is_usable = True
    _accepts_engine_in_init = True

    def get_template_sources(self, template_name):
        yield Origin(
            name='entrydetailloader',
            template_name=template_name,
            loader=self)

    def get_contents(self, origin):
        return ('<html><head><title>{{ object.title }}</title></head>'
                '<body>{{ object.html_content|safe }}</body></html>')

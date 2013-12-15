"""Utils for Zinnia's tests"""
try:
    from urllib.parse import parse_qs
    from urllib.parse import urlparse
    from xmlrpc.client import Transport
except ImportError:  # Python 2
    from urlparse import parse_qs
    from urlparse import urlparse
    from xmlrpclib import Transport
from datetime import datetime as original_datetime

from django.utils import six
from django.conf import settings
from django.utils import timezone
from django.test.client import Client


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
        res = six.BytesIO(response.content)
        setattr(res, 'getheader', lambda *args: '')  # For Python >= 2.7
        res.seek(0)
        return self.parse_response(res)


def test_datetime(*args):
    """
    Generating a datetime aware or naive depending of USE_TZ.
    """
    d = original_datetime(*args)
    if settings.USE_TZ:
        d = timezone.make_aware(d, timezone.utc)
    return d

datetime = test_datetime


def is_lib_available(library):
    """
    Check if a Python library is available.
    """
    try:
        __import__(library)
        return True
    except ImportError:
        return False


def urlEqual(url_1, url_2):
    """
    Compare two URLs with query string where
    ordering does not matter.
    """
    parse_result_1 = urlparse(url_1)
    parse_result_2 = urlparse(url_2)

    return (parse_result_1[:4] == parse_result_2[:4] and
            parse_qs(parse_result_1[5]) == parse_qs(parse_result_2[5]))

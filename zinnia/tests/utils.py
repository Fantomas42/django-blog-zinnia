"""Utils for Zinnia's tests"""
try:
    from xmlrpc.client import Transport
except ImportError:  # Python 2
    from xmlrpclib import Transport
from datetime import datetime as original_datetime

from django.utils import six
from django.conf import settings
from django.utils import timezone
from django.test.client import Client

from zinnia import is_before_1_6


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
        #I think(?) this is supposed to be bytes
        res = six.BytesIO(response.content)
        setattr(res, 'getheader', lambda *args: '')  # For Python >= 2.7
        res.seek(0)
        #What's with the redundancy?
        if not hasattr(res, 'getheader'):
            setattr(res, 'getheader', lambda *args: "")
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
    uri_1, uri_2 = url_1.split("?")[0], url_2.split("?")[0]
    if uri_1 == uri_2:
        try:
            querystring_1 = url_1.split("?")[1]
        except IndexError:
            querystring_1 = ""
        try:
            querystring_2 = url_2.split("?")[1]
        except IndexError:
            querystring_2 = ""
        query_1 = {}
        #This is ugly, I know. Will fix when less braindead
        for item in map(lambda item: item.split("="), querystring_1.replace(";", "&").split("&")):
            if len(item) == 2:
                key, value = item
            else:
                key = item[0]
                value = None
            query_1[key] = value
        query_2 = {}
        for item in map(lambda item: item.split("="), querystring_2.replace(";", "&").split("&")):
            if len(item) == 2:
                key, value = item
            else:
                key = item[0]
                value = None
            query_2[key] = value
            
        return query_1 == query_2
    return False

is_using_sqlite = settings.DATABASES["default"]["ENGINE"].endswith("sqlite3")

#This is a rough rule
#I don't know if it's necessarily true across all inputs
#Will ask on the mailing list eventually
supports_savepoints = not (is_before_1_6 and is_using_sqlite)

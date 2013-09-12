"""Utils for Zinnia's tests"""
try:
    from io import StringIO
    from xmlrpc.client import Transport
except ImportError:  # Python 2
    from StringIO import StringIO
    from xmlrpclib import Transport
from datetime import datetime as original_datetime

from django.conf import settings
from django.utils import timezone
from django.test.client import Client
import django


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
        #I'm not sure if it's allowed to assume utf-8 is the proper
        #encoding. Feedback would be appreciated.
        res = StringIO(response.content.decode("utf-8"))
        setattr(res, 'getheader', lambda *args: '')  # For Python >= 2.7
        res.seek(0)
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

is_before_1_6 = (django.VERSION[0] < 1) or (django.VERSION[0]
                                            == 1 and django.VERSION[1] < 6)

is_using_sqlite = settings.DATABASES["default"]["ENGINE"].endswith("sqlite3")

#This is a rough rule
#I don't know if it's necessarily true across all inputs
#Will ask on the mailing list eventually
supports_savepoints = not (is_before_1_6 and is_using_sqlite)

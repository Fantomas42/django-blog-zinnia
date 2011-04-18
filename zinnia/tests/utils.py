"""Utils for Zinnia's tests"""
import StringIO
from xmlrpclib import Transport

from django.test.client import Client


class TestTransport(Transport):
    """Handles connections to XML-RPC server
    through Django test client."""

    def __init__(self, *args, **kwargs):
        Transport.__init__(self, *args, **kwargs)
        self.client = Client()

    def request(self, host, handler, request_body, verbose=0):
        self.verbose = verbose
        response = self.client.post(handler,
                                    request_body,
                                    content_type="text/xml")
        res = StringIO.StringIO(response.content)
        res.seek(0)
        if not hasattr(res, 'getheader'):
            setattr(res, 'getheader', lambda *args: "")
        return self.parse_response(res)

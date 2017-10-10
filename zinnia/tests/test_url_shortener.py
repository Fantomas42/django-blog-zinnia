"""Test cases for Zinnia's url_shortener"""
import warnings

from django.test import TestCase
from django.test.utils import override_settings

from zinnia import url_shortener as us_settings
from zinnia.url_shortener import get_url_shortener
from zinnia.url_shortener.backends import default


class URLShortenerTestCase(TestCase):
    """Test cases for zinnia.url_shortener"""

    def setUp(self):
        self.original_backend = us_settings.URL_SHORTENER_BACKEND

    def tearDown(self):
        us_settings.URL_SHORTENER_BACKEND = self.original_backend

    def test_get_url_shortener(self):
        us_settings.URL_SHORTENER_BACKEND = 'mymodule.myclass'
        with warnings.catch_warnings(record=True) as w:
            self.assertEqual(get_url_shortener(), default.backend)
            self.assertTrue(issubclass(w[-1].category, RuntimeWarning))
            self.assertEqual(
                str(w[-1].message),
                'mymodule.myclass backend cannot be imported')

        us_settings.URL_SHORTENER_BACKEND = ('zinnia.tests.implementations.'
                                             'custom_url_shortener')
        with warnings.catch_warnings(record=True) as w:
            self.assertEqual(get_url_shortener(), default.backend)
            self.assertTrue(issubclass(w[-1].category, RuntimeWarning))
            self.assertEqual(
                str(w[-1].message),
                'This backend only exists for testing')

        us_settings.URL_SHORTENER_BACKEND = 'zinnia.url_shortener'\
                                            '.backends.default'
        self.assertEqual(get_url_shortener(), default.backend)


class FakeEntry(object):
    """Fake entry with only 'pk' as attribute"""
    def __init__(self, pk):
        self.pk = pk


@override_settings(
    ROOT_URLCONF='zinnia.tests.implementations.urls.default'
)
class UrlShortenerDefaultBackendTestCase(TestCase):
    """Tests cases for the default url shortener backend"""

    def test_backend(self):
        original_protocol = default.PROTOCOL
        default.PROTOCOL = 'http'
        entry = FakeEntry(1)
        self.assertEqual(default.backend(entry),
                         'http://example.com/1/')
        default.PROTOCOL = 'https'
        entry = FakeEntry(100)
        self.assertEqual(default.backend(entry),
                         'https://example.com/2S/')
        default.PROTOCOL = original_protocol

    def test_base36(self):
        self.assertEqual(default.base36(1), '1')
        self.assertEqual(default.base36(100), '2S')
        self.assertEqual(default.base36(46656), '1000')

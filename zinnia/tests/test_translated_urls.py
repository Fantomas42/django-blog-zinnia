"""Test cases for Zinnia's translated URLs"""
from django.test import TestCase
from django.utils.translation import activate
from django.utils.translation import deactivate

from zinnia.urls import i18n_url


class TranslatedURLsTestCase(TestCase):
    """Test cases for translated URLs"""

    def test_translated_urls(self):
        deactivate()
        self.assertEqual(
            i18n_url(r'^authors/'), r'^authors/')
        activate('fr')
        self.assertEqual(
            i18n_url(r'^authors/', True), r'^auteurs/')
        self.assertEqual(
            i18n_url(r'^authors/', False), r'^authors/')

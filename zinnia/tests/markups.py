"""Test cases for Zinnia's markups"""
import __builtin__
import warnings

from django.test import TestCase

from zinnia.markups import textile
from zinnia.markups import markdown
from zinnia.markups import restructuredtext


class FailImportMarkupTestCase(TestCase):
    exclude_list = ['textile', 'markdown', 'docutils']

    def setUp(self):
        self.original_import = __builtin__.__import__
        __builtin__.__import__ = self.import_hook

    def tearDown(self):
        __builtin__.__import__ = self.original_import

    def import_hook(self, name, *args, **kwargs):
        if name in self.exclude_list:
            raise ImportError('%s module has been disabled' % name)
        else:
            self.original_import(name, *args, **kwargs)

    def test_textile(self):
        with warnings.catch_warnings(record=True) as w:
            result = textile('My *text*')
        self.tearDown()
        self.assertEquals(result, 'My *text*')
        self.assertTrue(issubclass(w[-1].category, RuntimeWarning))
        self.assertEquals(
            str(w[-1].message),
            "The Python textile library isn't installed.")

    def test_markdown(self):
        with warnings.catch_warnings(record=True) as w:
            result = markdown('My *text*')
        self.tearDown()
        self.assertEquals(result, 'My *text*')
        self.assertTrue(issubclass(w[-1].category, RuntimeWarning))
        self.assertEquals(
            str(w[-1].message),
            "The Python markdown library isn't installed.")

    def test_restructuredtext(self):
        with warnings.catch_warnings(record=True) as w:
            result = restructuredtext('My *text*')
        self.tearDown()
        self.assertEquals(result, 'My *text*')
        self.assertTrue(issubclass(w[-1].category, RuntimeWarning))
        self.assertEquals(
            str(w[-1].message),
            "The Python docutils library isn't installed.")

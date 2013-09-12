"""Test cases for Zinnia's markups"""
import sys
try:
    import __builtin__
except ImportError:
    import builtins as __builtin__
import warnings

from django.test import TestCase
from django.utils.unittest import skipUnless

from zinnia.markups import textile
from zinnia.markups import markdown
from zinnia.markups import restructuredtext
from zinnia.tests.utils import is_lib_available


class MarkupsTestCase(TestCase):
    text = 'Hello *World* !'

    @skipUnless(is_lib_available('textile'), 'Textile is not available')
    def test_textile(self):
        self.assertEqual(textile(self.text).strip(),
                          '<p>Hello <strong>World</strong> !</p>')

    @skipUnless(is_lib_available('markdown'), 'Markdown is not available')
    def test_markdown(self):
        self.assertEqual(markdown(self.text).strip(),
                          '<p>Hello <em>World</em> !</p>')

    @skipUnless(is_lib_available('markdown'), 'Markdown is not available')
    def test_markdown_extensions(self):
        text = '[TOC]\n\n# Header 1\n\n## Header 2'
        self.assertEqual(markdown(text).strip(),
                          '<p>[TOC]</p>\n<h1>Header 1</h1>'
                          '\n<h2>Header 2</h2>')
        self.assertEqual(markdown(text, extensions='toc').strip(),
                          '<div class="toc">\n<ul>\n<li><a href="#header-1">'
                          'Header 1</a><ul>\n<li><a href="#header-2">'
                          'Header 2</a></li>\n</ul>\n</li>\n</ul>\n</div>'
                          '\n<h1 id="header-1">Header 1</h1>\n'
                          '<h2 id="header-2">Header 2</h2>')

    @skipUnless(is_lib_available('docutils'), 'Docutils is not available')
    def test_restructuredtext(self):
        self.assertEqual(restructuredtext(self.text).strip(),
                          '<p>Hello <em>World</em> !</p>')

    @skipUnless(is_lib_available('docutils'), 'Docutils is not available')
    def test_restructuredtext_settings_override(self):
        text = 'My email is toto@example.com'
        self.assertEqual(restructuredtext(text).strip(),
                          '<p>My email is <a class="reference external" '
                          'href="mailto:toto&#64;example.com">'
                          'toto&#64;example.com</a></p>')
        self.assertEqual(
            restructuredtext(text, {'cloak_email_addresses': True}).strip(),
            '<p>My email is <a class="reference external" '
            'href="mailto:toto&#37;&#52;&#48;example&#46;com">'
            'toto<span>&#64;</span>example<span>&#46;</span>com</a></p>')


@skipUnless(sys.version_info >= (2, 7, 0),
            'Cannot run these tests under Python 2.7')
class MarkupFailImportTestCase(TestCase):
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
            warnings.simplefilter("always")
            result = textile('My *text*')
            self.tearDown()
            self.assertEqual(result, 'My *text*')
            self.assertTrue(issubclass(w[-1].category, RuntimeWarning))
            self.assertEqual(
                str(w[-1].message),
                "The Python textile library isn't installed.")

    def test_markdown(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = markdown('My *text*')
            self.tearDown()
            self.assertEqual(result, 'My *text*')
            self.assertTrue(issubclass(w[-1].category, RuntimeWarning))
            self.assertEqual(
                str(w[-1].message),
                "The Python markdown library isn't installed.")

    def test_restructuredtext(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = restructuredtext('My *text*')
            self.tearDown()
            self.assertEqual(result, 'My *text*')
            self.assertTrue(issubclass(w[-1].category, RuntimeWarning))
            self.assertEqual(
                str(w[-1].message),
                "The Python docutils library isn't installed.")

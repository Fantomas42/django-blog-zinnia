"""Test cases for Zinnia's preview"""
from django.test import TestCase

from zinnia.preview import HTMLPreview


class HTMLPreviewTestCase(TestCase):

    def test_splitters(self):
        text = '<p>Hello World</p><!-- more --><p>Hello dude</p>'
        preview = HTMLPreview(text, splitters=['<!--more-->'],
                              max_words=1000, more_string=' ...')
        self.assertEquals(str(preview), text)
        preview = HTMLPreview(text, splitters=['<!--more-->',
                                               '<!-- more -->'],
                              max_words=1000, more_string=' ...')
        self.assertEquals(str(preview), '<p>Hello World ...</p>')

    def test_truncate(self):
        text = '<p>Hello World</p><p>Hello dude</p>'
        preview = HTMLPreview(text, splitters=[],
                              max_words=2, more_string=' ...')
        self.assertEquals(str(preview), '<p>Hello World ...</p>')

    def test_has_more(self):
        text = '<p>Hello World</p><p>Hello dude</p>'
        preview = HTMLPreview(text, splitters=[],
                              max_words=2, more_string=' ...')
        self.assertEquals(preview.has_more, True)
        preview = HTMLPreview(text, splitters=[],
                              max_words=4, more_string=' ...')
        self.assertEquals(preview.has_more, False)

    def test_has_more_with_long_more_text(self):
        text = '<p>Hello the World</p>'
        preview = HTMLPreview(text, splitters=[],
                              max_words=2, more_string=' .........')
        self.assertEquals(str(preview), '<p>Hello the .........</p>')
        self.assertEquals(preview.has_more, True)

# coding=utf-8
"""Test cases for Zinnia's preview"""
from django.test import TestCase

from zinnia.preview import HTMLPreview


class HTMLPreviewTestCase(TestCase):

    def test_splitters(self):
        text = '<p>Hello World</p><!-- more --><p>Hello dude</p>'
        preview = HTMLPreview(text, splitters=['<!--more-->'],
                              max_words=1000, more_string=' ...')
        self.assertEqual(str(preview), text)
        preview = HTMLPreview(text, splitters=['<!--more-->',
                                               '<!-- more -->'],
                              max_words=1000, more_string=' ...')
        self.assertEqual(str(preview), '<p>Hello World ...</p>')

    def test_truncate(self):
        text = '<p>Hello World</p><p>Hello dude</p>'
        preview = HTMLPreview(text, splitters=[],
                              max_words=2, more_string=' ...')
        self.assertEqual(str(preview), '<p>Hello World ...</p>')

    def test_has_more(self):
        text = '<p>Hello World</p><p>Hello dude</p>'
        preview = HTMLPreview(text, splitters=[],
                              max_words=2, more_string=' ...')
        self.assertEqual(preview.has_more, True)
        preview = HTMLPreview(text, splitters=[],
                              max_words=4, more_string=' ...')
        self.assertEqual(preview.has_more, False)

    def test_has_more_with_long_more_text(self):
        text = '<p>Hello the World</p>'
        preview = HTMLPreview(text, splitters=[],
                              max_words=2, more_string=' .........')
        self.assertEqual(str(preview), '<p>Hello the .........</p>')
        self.assertEqual(preview.has_more, True)

    def test_has_more_with_lead(self):
        text = '<p>Hello the World</p>'
        lead = '<p>Lead paragraph</p>'
        preview = HTMLPreview(text, lead)
        self.assertEqual(str(preview), '<p>Lead paragraph</p>')
        self.assertEqual(preview.has_more, True)
        preview = HTMLPreview('', lead)
        self.assertEqual(str(preview), '<p>Lead paragraph</p>')
        self.assertEqual(preview.has_more, False)

    def test_str_non_ascii_issue_314(self):
        text = '<p>тест non ascii</p>'
        preview = HTMLPreview(text, splitters=[],
                              max_words=2, more_string=' ...')
        self.assertEqual(str(preview), '<p>тест non ...</p>')

    def test_metrics(self):
        text = '<p>Hello World</p> <p>Hello dude</p>'
        preview = HTMLPreview(text, splitters=[],
                              max_words=2, more_string=' ...')
        self.assertEqual(preview.total_words, 4)
        self.assertEqual(preview.displayed_words, 2)
        self.assertEqual(preview.remaining_words, 2)
        self.assertEqual(preview.displayed_percent, 50.0)
        self.assertEqual(preview.remaining_percent, 50.0)

    def test_metrics_with_lead(self):
        text = '<p>Hello World</p> <p>Hello dude</p>'
        lead = '<p>Lead paragraph</p>'
        preview = HTMLPreview(text, lead, splitters=[],
                              max_words=2, more_string=' ...')
        self.assertEqual(preview.total_words, 6)
        self.assertEqual(preview.displayed_words, 2)
        self.assertEqual(preview.remaining_words, 4)
        self.assertEqual('%.2f' % preview.displayed_percent, '33.33')
        self.assertEqual('%.2f' % preview.remaining_percent, '66.67')

    def test_empty_text(self):
        preview = HTMLPreview('')
        self.assertEqual(str(preview), '')
        self.assertEqual(preview.has_more, False)
        preview = HTMLPreview('', '')
        self.assertEqual(str(preview), '')
        self.assertEqual(preview.has_more, False)

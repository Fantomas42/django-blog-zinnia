"""Test cases for Zinnia's admin widgets"""
from __future__ import unicode_literals

from django.test import TestCase

from zinnia.admin.widgets import MPTTFilteredSelectMultiple


class MPTTFilteredSelectMultipleTestCase(TestCase):

    def test_render_options(self):
        widget = MPTTFilteredSelectMultiple('test', False)
        self.assertEquals(widget.render_options([], []), '')

        self.assertEquals(
            widget.render_options(
                [(1, 'Category 1', (1, 1)),
                 (2, '|-- Category 2', (1, 2))], []),
            '<option value="1" data-tree-id="1" data-left-value="1">'
            'Category 1</option>\n<option value="2" data-tree-id="1" '
            'data-left-value="2">|-- Category 2</option>')

        self.assertEquals(
            widget.render_options(
                [(1, 'Category 1', (1, 1)),
                 (2, '|-- Category 2', (1, 2))], [2]),
            '<option value="1" data-tree-id="1" data-left-value="1">'
            'Category 1</option>\n<option value="2" data-tree-id="1" '
            'data-left-value="2" selected="selected">|-- Category 2</option>')

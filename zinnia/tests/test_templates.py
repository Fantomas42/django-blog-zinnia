"""Test cases for Zinnia Template"""
from django.test import TestCase

from zinnia.templates import loop_template_list


class TemplateTestCase(TestCase):
    """Tests cases for template"""

    def test_loop_template_list(self):
        template = 'zinnia/template.html'
        self.assertEqual(
            loop_template_list(
                1, None, template),
            ['zinnia/template.html_1',
             template])
        self.assertEqual(
            loop_template_list(
                1, None, template,
                {'default': {1: 'default_template.html'}}),
            ['default_template.html',
             'zinnia/template.html_1',
             template])
        self.assertEqual(
            loop_template_list(
                1, 'object', template,
                {'default': {1: 'default_template.html'},
                 'str': {1: 'str_template.html'},
                 'object': {1: 'object_template.html'},
                 'str-object': {1: 'str_object_template.html'}}),
            ['str_object_template.html',
             'object_template.html',
             'str_template.html',
             'default_template.html',
             'zinnia/template.html_1',
             template])

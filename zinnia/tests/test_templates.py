"""Test cases for Zinnia Template"""
from django.test import TestCase

from zinnia.templates import append_position
from zinnia.templates import loop_template_list


class TemplateTestCase(TestCase):
    """Tests cases for template"""

    def test_loop_template_list(self):
        template = 'zinnia/template.html'
        self.assertEqual(
            loop_template_list(
                (1, 1), None, None, template, {}),
            ['zinnia/template-1.html',
             'zinnia/template_1.html',
             template])
        self.assertEqual(
            loop_template_list(
                (10, 1), None, None, template,
                {'default': {10: 'default_template.html'}}),
            ['default_template.html',
             'zinnia/template-10.html',
             'zinnia/template_1.html',
             template])
        self.assertEqual(
            loop_template_list(
                (10, 1), 'object', 'str', template,
                {'default': {10: 'default_template.html'},
                 'str': {10: 'str_template.html'},
                 'object': {10: 'object_template.html'},
                 'str-object': {10: 'str_object_template.html'}}),
            ['str_object_template.html',
             'object_template.html',
             'str_template.html',
             'default_template.html',
             'zinnia/template-10.html',
             'zinnia/template_1.html',
             template])

    def test_append_position(self):
        self.assertEqual(
            append_position('template.html', 1),
            'template1.html')
        self.assertEqual(
            append_position('template', 1),
            'template1')
        self.assertEqual(
            append_position('/path/template.html', 1),
            '/path/template1.html')
        self.assertEqual(
            append_position('/path/template.html', 1, '-'),
            '/path/template-1.html')

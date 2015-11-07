"""Test cases for Zinnia Template"""
from django.test import TestCase

from zinnia.templates import loop_template_list


class TemplateTestCase(TestCase):
    """Tests cases for template"""

    def test_loop_template_list(self):
        template = 'zinnia/template.html'
        self.assertEqual(
            loop_template_list(0, None, template),
            [template])
        self.assertEqual(
            loop_template_list(1, None, template),
            ['zinnia/template.html_1',
             'zinnia/1_entry_detail.html',
             template])

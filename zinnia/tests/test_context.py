"""Test cases for Zinnia Context"""
from django.core.paginator import Paginator
from django.template import Context
from django.test import TestCase

from zinnia.context import get_context_first_matching_object
from zinnia.context import get_context_first_object
from zinnia.context import get_context_loop_positions


class ContextTestCase(TestCase):
    """Tests cases for context"""

    def test_get_context_first_matching_object(self):
        context = Context({'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(
            get_context_first_matching_object(context, ['key']),
            (None, None))
        self.assertEqual(
            get_context_first_matching_object(context, ['a']),
            ('a', 1))
        self.assertEqual(
            get_context_first_matching_object(context, ['b', 'a']),
            ('b', 2))

    def test_get_context_first_object(self):
        context = Context({'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(
            get_context_first_object(context, ['key']),
            None)
        self.assertEqual(
            get_context_first_object(context, ['a']),
            1)
        self.assertEqual(
            get_context_first_object(context, ['b', 'a']),
            2)

    def test_get_context_loop_positions(self):
        paginator = Paginator(range(50), 10)
        context = Context({})
        self.assertEqual(
            get_context_loop_positions(context),
            (0, 0))
        context = Context({'forloop': {'counter': 5}})
        self.assertEqual(
            get_context_loop_positions(context),
            (5, 5))
        context = Context({'forloop': {'counter': 5},
                           'page_obj': paginator.page(3)})
        self.assertEqual(
            get_context_loop_positions(context),
            (25, 5))

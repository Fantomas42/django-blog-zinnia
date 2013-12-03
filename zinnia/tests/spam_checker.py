"""Test cases for Zinnia's spam_checker"""
import warnings

from django.test import TestCase

from zinnia.spam_checker import get_spam_checker
from zinnia.spam_checker.backends.all_is_spam import backend


class SpamCheckerTestCase(TestCase):
    """Test cases for zinnia.spam_checker"""

    def test_get_spam_checker(self):
        with warnings.catch_warnings(record=True) as w:
            #Without this, in python 3, depending on the flags passed in
            #on the command line, you might not get the warnings
            warnings.simplefilter("always")
            self.assertEqual(get_spam_checker('mymodule.myclass'), None)
            self.assertTrue(issubclass(w[-1].category, RuntimeWarning))
            self.assertEqual(
                str(w[-1].message),
                'mymodule.myclass backend cannot be imported')

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.assertEqual(
                get_spam_checker('zinnia.tests.custom_spam_checker'), None)
            self.assertTrue(issubclass(w[-1].category, RuntimeWarning))
            self.assertEqual(
                str(w[-1].message),
                'This backend only exists for testing')

        self.assertEqual(
            get_spam_checker('zinnia.spam_checker.backends.all_is_spam'),
            backend)

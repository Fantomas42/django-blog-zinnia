"""Unit tests for Zinnia"""
from unittest import TestSuite
from unittest import TestLoader
from django.conf import settings

from zinnia.tests.entry import EntryTestCase
from zinnia.tests.category import CategoryTestCase
from zinnia.tests.managers import ManagersTestCase
from zinnia.tests.feeds import ZinniaFeedsTestCase
from zinnia.tests.views import ZinniaViewsTestCase  # ~6s ouch...
from zinnia.tests.pingback import PingBackTestCase  # ~1.5s
from zinnia.tests.metaweblog import MetaWeblogTestCase  # ~0.8s
from zinnia.tests.comparison import ComparisonTestCase
from zinnia.tests.quick_entry import QuickEntryTestCase
from zinnia.tests.sitemaps import ZinniaSitemapsTestCase
from zinnia.tests.ping import ExternalUrlsPingerTestCase
from zinnia.tests.templatetags import TemplateTagsTestCase
from zinnia.tests.moderator import EntryCommentModeratorTestCase


def suite():
    """Suite of TestCases for Django"""
    suite = TestSuite()
    loader = TestLoader()

    test_cases = (ManagersTestCase, EntryTestCase, CategoryTestCase,
                  ZinniaViewsTestCase, ZinniaFeedsTestCase,
                  ZinniaSitemapsTestCase, ComparisonTestCase,
                  ExternalUrlsPingerTestCase, TemplateTagsTestCase,
                  QuickEntryTestCase, EntryCommentModeratorTestCase)

    if 'django_xmlrpc' in settings.INSTALLED_APPS:
        test_cases += (PingBackTestCase, MetaWeblogTestCase)

    for test_class in test_cases:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    return suite

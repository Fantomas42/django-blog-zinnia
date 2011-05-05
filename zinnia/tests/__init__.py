"""Unit tests for Zinnia"""
from unittest import TestSuite
from unittest import TestLoader
from django.conf import settings

from zinnia.tests.entry import EntryTestCase  # ~0.2s
from zinnia.tests.entry import EntryHtmlContentTestCase  # ~0.5s
from zinnia.tests.entry import EntryGetBaseModelTestCase
from zinnia.tests.signals import SignalsTestCase
from zinnia.tests.category import CategoryTestCase
from zinnia.tests.managers import ManagersTestCase  # ~1.2s
from zinnia.tests.feeds import ZinniaFeedsTestCase  # ~0.4s
from zinnia.tests.views import ZinniaViewsTestCase  # ~1.5s ouch...
from zinnia.tests.views import ZinniaCustomDetailViews  # ~0.3s
from zinnia.tests.pingback import PingBackTestCase  # ~0.3s
from zinnia.tests.metaweblog import MetaWeblogTestCase  # ~0.6s
from zinnia.tests.comparison import ComparisonTestCase
from zinnia.tests.quick_entry import QuickEntryTestCase  # ~0.4s
from zinnia.tests.sitemaps import ZinniaSitemapsTestCase  # ~0.3s
from zinnia.tests.ping import DirectoryPingerTestCase
from zinnia.tests.ping import ExternalUrlsPingerTestCase
from zinnia.tests.templatetags import TemplateTagsTestCase  # ~0.4s
from zinnia.tests.moderator import EntryCommentModeratorTestCase  # ~0.1s
from zinnia.tests.spam_checker import SpamCheckerTestCase
from zinnia.tests.url_shortener import URLShortenerTestCase
from zinnia.signals import disconnect_zinnia_signals
# TOTAL ~ 6.6s


def suite():
    """Suite of TestCases for Django"""
    suite = TestSuite()
    loader = TestLoader()

    test_cases = (ManagersTestCase, EntryTestCase,
                  EntryGetBaseModelTestCase, SignalsTestCase,
                  EntryHtmlContentTestCase, CategoryTestCase,
                  ZinniaViewsTestCase, ZinniaFeedsTestCase,
                  ZinniaSitemapsTestCase, ComparisonTestCase,
                  DirectoryPingerTestCase, ExternalUrlsPingerTestCase,
                  TemplateTagsTestCase, QuickEntryTestCase,
                  URLShortenerTestCase, EntryCommentModeratorTestCase,
                  ZinniaCustomDetailViews, SpamCheckerTestCase)

    if 'django_xmlrpc' in settings.INSTALLED_APPS:
        test_cases += (PingBackTestCase, MetaWeblogTestCase)

    for test_class in test_cases:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    return suite

disconnect_zinnia_signals()

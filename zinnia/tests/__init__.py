"""Unit tests for Zinnia"""
from unittest import TestSuite
from unittest import TestLoader
from django.conf import settings

from zinnia.tests.entry import EntryTestCase
from zinnia.tests.entry import EntryHtmlContentTestCase
from zinnia.tests.entry import EntryGetBaseModelTestCase
from zinnia.tests.signals import SignalsTestCase
from zinnia.tests.category import CategoryTestCase
from zinnia.tests.admin import EntryAdminTestCase
from zinnia.tests.admin import CategoryAdminTestCase
from zinnia.tests.managers import ManagersTestCase
from zinnia.tests.feeds import ZinniaFeedsTestCase
from zinnia.tests.views import ZinniaViewsTestCase
from zinnia.tests.views import ZinniaCustomDetailViews
from zinnia.tests.pingback import PingBackTestCase
from zinnia.tests.metaweblog import MetaWeblogTestCase
from zinnia.tests.comparison import ComparisonTestCase
from zinnia.tests.quick_entry import QuickEntryTestCase
from zinnia.tests.sitemaps import ZinniaSitemapsTestCase
from zinnia.tests.ping import DirectoryPingerTestCase
from zinnia.tests.ping import ExternalUrlsPingerTestCase
from zinnia.tests.templatetags import TemplateTagsTestCase
from zinnia.tests.moderator import EntryCommentModeratorTestCase
from zinnia.tests.spam_checker import SpamCheckerTestCase
from zinnia.tests.url_shortener import URLShortenerTestCase
from zinnia.tests.long_enough import LongEnoughTestCase
from zinnia.tests.mixins import MixinTestCase
from zinnia.signals import disconnect_zinnia_signals


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
                  ZinniaCustomDetailViews, SpamCheckerTestCase,
                  EntryAdminTestCase, CategoryAdminTestCase,
                  MixinTestCase, LongEnoughTestCase)

    if 'django_xmlrpc' in settings.INSTALLED_APPS:
        test_cases += (PingBackTestCase, MetaWeblogTestCase)

    for test_class in test_cases:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    return suite

disconnect_zinnia_signals()

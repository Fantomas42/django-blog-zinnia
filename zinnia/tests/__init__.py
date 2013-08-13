"""Unit tests for Zinnia"""
from unittest import TestSuite
from unittest import TestLoader

from zinnia.tests.flags import FlagsTestCase
from zinnia.tests.feeds import FeedsTestCase
from zinnia.tests.mixins import MixinTestCase
from zinnia.tests.views import ViewsTestCase
from zinnia.tests.views import CustomDetailViewsTestCase
from zinnia.tests.sitemaps import SitemapsTestCase
from zinnia.tests.entry import EntryTestCase
from zinnia.tests.entry import EntryHtmlContentTestCase
from zinnia.tests.entry import EntryAbsoluteUrlTestCase
from zinnia.tests.author import AuthorTestCase
from zinnia.tests.category import CategoryTestCase
from zinnia.tests.managers import ManagersTestCase
from zinnia.tests.signals import SignalsTestCase
from zinnia.tests.pingback import PingBackTestCase
from zinnia.tests.metaweblog import MetaWeblogTestCase
from zinnia.tests.comparison import ComparisonTestCase
from zinnia.tests.preview import HTMLPreviewTestCase
from zinnia.tests.markups import MarkupsTestCase
from zinnia.tests.markups import MarkupFailImportTestCase
from zinnia.tests.ping import DirectoryPingerTestCase
from zinnia.tests.ping import ExternalUrlsPingerTestCase
from zinnia.tests.templatetags import TemplateTagsTestCase
from zinnia.tests.long_enough import LongEnoughTestCase
from zinnia.tests.spam_checker import SpamCheckerTestCase
from zinnia.tests.moderator import CommentModeratorTestCase
from zinnia.tests.url_shortener import URLShortenerTestCase
from zinnia.tests.models_bases import LoadModelClassTestCase
from zinnia.tests.translated_urls import TranslatedURLsTestCase
from zinnia.tests.admin import EntryAdminTestCase
from zinnia.tests.admin import CategoryAdminTestCase
from zinnia.tests.admin_forms import EntryAdminFormTestCase
from zinnia.tests.admin_forms import CategoryAdminFormTestCase
from zinnia.tests.admin_filters import AuthorListFilterTestCase
from zinnia.tests.admin_filters import CategoryListFilterTestCase
from zinnia.tests.admin_fields import MPTTModelChoiceIteratorTestCase
from zinnia.tests.admin_fields import MPTTModelMultipleChoiceFieldTestCase
from zinnia.tests.admin_widgets import MPTTFilteredSelectMultipleTestCase

from zinnia.signals import disconnect_entry_signals
from zinnia.signals import disconnect_discussion_signals


def suite():
    """Suite of TestCases for Django"""
    suite = TestSuite()
    loader = TestLoader()

    test_cases = (
        # Models
        EntryTestCase,
        AuthorTestCase,
        CategoryTestCase,
        ManagersTestCase,
        LoadModelClassTestCase,
        # Admin
        EntryAdminTestCase,
        CategoryAdminTestCase,
        EntryAdminFormTestCase,
        CategoryAdminFormTestCase,
        AuthorListFilterTestCase,
        CategoryListFilterTestCase,
        MPTTModelChoiceIteratorTestCase,
        MPTTModelMultipleChoiceFieldTestCase,
        MPTTFilteredSelectMultipleTestCase,
        # Front
        MixinTestCase,
        ViewsTestCase,
        CustomDetailViewsTestCase,
        FeedsTestCase,
        SitemapsTestCase,
        ComparisonTestCase,
        TemplateTagsTestCase,
        # HTML
        HTMLPreviewTestCase,
        EntryHtmlContentTestCase,
        MarkupsTestCase,
        MarkupFailImportTestCase,
        # URLs
        URLShortenerTestCase,
        TranslatedURLsTestCase,
        EntryAbsoluteUrlTestCase,
        # Discussions
        FlagsTestCase,
        SignalsTestCase,
        LongEnoughTestCase,
        SpamCheckerTestCase,
        CommentModeratorTestCase,
        # Pinging
        DirectoryPingerTestCase,
        ExternalUrlsPingerTestCase,
        # XML-RPC
        PingBackTestCase,
        MetaWeblogTestCase,
    )

    for test_class in test_cases:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    return suite

disconnect_entry_signals()
disconnect_discussion_signals()

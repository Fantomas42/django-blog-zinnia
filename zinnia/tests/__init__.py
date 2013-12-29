"""Unit tests for Zinnia"""
from unittest import TestSuite
from unittest import TestLoader

from zinnia.tests.test_flags import FlagsTestCase
from zinnia.tests.test_feeds import FeedsTestCase
from zinnia.tests.test_mixins import MixinTestCase
from zinnia.tests.test_views import ViewsTestCase
from zinnia.tests.test_views import CustomDetailViewsTestCase
from zinnia.tests.test_sitemaps import SitemapsTestCase
from zinnia.tests.test_entry import EntryTestCase
from zinnia.tests.test_entry import EntryHtmlContentTestCase
from zinnia.tests.test_entry import EntryAbsoluteUrlTestCase
from zinnia.tests.test_author import AuthorTestCase
from zinnia.tests.test_category import CategoryTestCase
from zinnia.tests.test_managers import ManagersTestCase
from zinnia.tests.test_signals import SignalsTestCase
from zinnia.tests.test_pingback import PingBackTestCase
from zinnia.tests.test_metaweblog import MetaWeblogTestCase
from zinnia.tests.test_comparison import ComparisonTestCase
from zinnia.tests.test_preview import HTMLPreviewTestCase
from zinnia.tests.test_markups import MarkupsTestCase
from zinnia.tests.test_markups import MarkupFailImportTestCase
from zinnia.tests.test_ping import DirectoryPingerTestCase
from zinnia.tests.test_ping import ExternalUrlsPingerTestCase
from zinnia.tests.test_templatetags import TemplateTagsTestCase
from zinnia.tests.test_templatetags import TemplateTagsTimezoneTestCase
from zinnia.tests.test_long_enough import LongEnoughTestCase
from zinnia.tests.test_spam_checker import SpamCheckerTestCase
from zinnia.tests.test_moderator import CommentModeratorTestCase
from zinnia.tests.test_url_shortener import URLShortenerTestCase
from zinnia.tests.test_models_bases import LoadModelClassTestCase
from zinnia.tests.test_translated_urls import TranslatedURLsTestCase
from zinnia.tests.test_admin import EntryAdminTestCase
from zinnia.tests.test_admin import CategoryAdminTestCase
from zinnia.tests.test_admin_forms import EntryAdminFormTestCase
from zinnia.tests.test_admin_forms import CategoryAdminFormTestCase
from zinnia.tests.test_admin_filters import AuthorListFilterTestCase
from zinnia.tests.test_admin_filters import CategoryListFilterTestCase
from zinnia.tests.test_admin_fields import MPTTModelChoiceIteratorTestCase
from zinnia.tests.test_admin_fields import MPTTModelMultipleChoiceFieldTestCase
from zinnia.tests.test_admin_widgets import MPTTFilteredSelectMultipleTestCase

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
        TemplateTagsTimezoneTestCase,
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

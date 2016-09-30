"""Test cases for Zinnia's flags"""
from django.test import TestCase

from zinnia import flags
from zinnia.flags import get_user_flagger
from zinnia.tests.utils import skip_if_custom_user


@skip_if_custom_user
class FlagsTestCase(TestCase):
    """Test cases for zinnia.flags"""

    def setUp(self):
        self.clear_user_flagger_cache()

    def clear_user_flagger_cache(self):
        get_user_flagger.cache_clear()

    def test_get_user_flagger_cache(self):
        get_user_flagger()
        with self.assertNumQueries(0):
            get_user_flagger()

    def test_get_user_flagger_does_not_exist(self):
        original_user_id = flags.COMMENT_FLAG_USER_ID
        flags.COMMENT_FLAG_USER_ID = 4242
        flagger = get_user_flagger()
        self.assertEqual(flagger.username, 'Zinnia-Flagger')
        flags.COMMENT_FLAG_USER_ID = original_user_id

    def test_get_user_flagged_does_not_exist_twice_issue_245(self):
        original_user_id = flags.COMMENT_FLAG_USER_ID
        flags.COMMENT_FLAG_USER_ID = None
        flagger = get_user_flagger()
        self.assertEqual(flagger.username, 'Zinnia-Flagger')
        self.clear_user_flagger_cache()
        flagger = get_user_flagger()
        self.assertEqual(flagger.username, 'Zinnia-Flagger')
        flags.COMMENT_FLAG_USER_ID = original_user_id

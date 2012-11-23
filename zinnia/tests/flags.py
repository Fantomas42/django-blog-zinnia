"""Test cases for Zinnia's flags"""
from __future__ import with_statement

from django.test import TestCase

from zinnia import flags
from zinnia.flags import get_user_flagger
from zinnia.flags import _get_user_flagger


class FlagsTestCase(TestCase):
    """Test cases for zinnia.flags"""

    def test_get_user_flagger_cache(self):
        get_user_flagger()
        with self.assertNumQueries(0):
            get_user_flagger()

    def test_get_user_flagger_does_not_exist(self):
        original_user_id = flags.COMMENT_FLAG_USER_ID
        flags.COMMENT_FLAG_USER_ID = 4242
        flagger = _get_user_flagger()
        self.assertEquals(flagger.username, 'Zinnia-Flagger')
        flags.COMMENT_FLAG_USER_ID = original_user_id

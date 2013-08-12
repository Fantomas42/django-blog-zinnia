# coding=utf-8
"""Test cases for Zinnia's quick entry"""
from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.auth.tests.utils import skipIfCustomUser

from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.managers import DRAFT


@skipIfCustomUser
class QuickEntryTestCase(TestCase):
    """Test cases for quick_entry view"""
    urls = 'zinnia.tests.urls'

    def setUp(self):
        Author.objects.create_user(
            'user', 'user@example.com', 'password')
        Author.objects.create_superuser(
            'admin', 'admin@example.com', 'password')

    def test_quick_entry(self):
        response = self.client.get('/quick-entry/')
        self.assertEquals(response.status_code, 302)
        self.assertEquals(
            response['Location'],
            'http://testserver/accounts/login/?next=/quick-entry/')
        self.client.login(username='user', password='password')
        response = self.client.get('/quick-entry/')
        self.assertEquals(response.status_code, 302)
        self.assertEquals(
            response['Location'],
            'http://testserver/accounts/login/?next=/quick-entry/')
        self.client.logout()
        self.client.login(username='admin', password='password')
        response = self.client.get('/quick-entry/')
        self.assertEquals(response.status_code, 302)
        self.assertEquals(
            response['Location'],
            'http://testserver/admin/zinnia/entry/add/')
        response = self.client.post('/quick-entry/', {'content': 'test'})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(
            response['Location'],
            'http://testserver/admin/zinnia/entry/add/'
            '?tags=&title=&sites=1&content='
            '%3Cp%3Etest%3C%2Fp%3E&authors=2&slug=')
        response = self.client.post('/quick-entry/',
                                    {'title': 'test', 'tags': 'test',
                                     'content': 'Test content',
                                     'save_draft': ''})
        entry = Entry.objects.get(title='test')
        self.assertEquals(response.status_code, 302)
        self.assertEquals(
            response['Location'],
            'http://testserver%s' % entry.get_absolute_url())
        self.assertEquals(entry.status, DRAFT)
        self.assertEquals(entry.title, 'test')
        self.assertEquals(entry.tags, 'test')
        self.assertEquals(entry.content, '<p>Test content</p>')

    def test_quick_entry_non_ascii_title_issue_153(self):
        self.client.login(username='admin', password='password')
        response = self.client.post('/quick-entry/',
                                    {'title': 'тест', 'tags': 'test-2',
                                     'content': 'Test content',
                                     'save_draft': ''})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'],
                          'http://testserver/admin/zinnia/entry/add/'
                          '?tags=test-2&title=%D1%82%D0%B5%D1%81%D1%82'
                          '&sites=1&content=%3Cp%3ETest+content%3C%2Fp%3E'
                          '&authors=2&slug=')

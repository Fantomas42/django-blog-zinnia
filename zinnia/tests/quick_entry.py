# coding=utf-8
"""Test cases for Zinnia's quick entry"""
from django.test import TestCase
from django.contrib.auth.models import User

from zinnia import settings
from zinnia.models import Entry
from zinnia.managers import DRAFT


class QuickEntryTestCase(TestCase):
    """Test cases for quick_entry view"""
    urls = 'zinnia.tests.urls'

    def setUp(self):
        self.original_wysiwyg = settings.WYSIWYG
        settings.WYSIWYG = None

    def tearDown(self):
        settings.WYSIWYG = self.original_wysiwyg

    def test_quick_entry(self):
        User.objects.create_user('user', 'user@example.com', 'password')
        User.objects.create_superuser('admin', 'admin@example.com', 'password')

        response = self.client.get('/quick_entry/', follow=True)
        self.assertEquals(
            response.redirect_chain,
            [('http://testserver/accounts/login/?next=/quick_entry/', 302)])
        self.client.login(username='user', password='password')
        response = self.client.get('/quick_entry/', follow=True)
        self.assertEquals(
            response.redirect_chain,
            [('http://testserver/accounts/login/?next=/quick_entry/', 302)])
        self.client.logout()
        self.client.login(username='admin', password='password')
        response = self.client.get('/quick_entry/', follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/zinnia/entry/add/', 302)])
        response = self.client.post('/quick_entry/', {'title': 'test'},
                                    follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/zinnia/entry/add/' \
                            '?tags=&title=test&sites=1&content=' \
                            '%3Cp%3E%3C%2Fp%3E&authors=2&slug=test', 302)])
        response = self.client.post('/quick_entry/',
                                    {'title': 'test', 'tags': 'test',
                                     'content': 'Test content',
                                     'save_draft': ''})
        entry = Entry.objects.get(title='test')
        self.assertEquals(response.status_code, 302)
        self.assertEquals(entry.status, DRAFT)
        self.assertEquals(entry.title, 'test')
        self.assertEquals(entry.tags, 'test')
        self.assertEquals(entry.content, '<p>Test content</p>')

        response = self.client.post('/quick_entry/',
                                    {'title': 'test', 'tags': 'test-2',
                                     'content': 'Test content',
                                     'save_draft': ''}, follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/zinnia/entry/add/'\
                            '?tags=test-2&title=test&sites=1&'\
                            'content=%3Cp%3ETest+content%3C%2Fp%3E'\
                            '&authors=2&slug=test', 302)])

        response = self.client.post('/quick_entry/',
                                    {'title': u'тест', 'tags': 'test-2',
                                     'content': 'Test content',
                                     'save_draft': ''}, follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/zinnia/entry/add/'\
                            '?tags=test-2&title=%D1%82%D0%B5%D1%81%D1%82'
                            '&sites=1&content=%3Cp%3ETest+content%3C%2Fp%3E'\
                            '&authors=2&slug=', 302)])

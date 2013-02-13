# coding=utf-8
"""Test cases for Zinnia's quick entry"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.test.utils import restore_template_loaders
from django.test.utils import setup_test_template_loader

from zinnia import settings
from zinnia.models.entry import Entry
from zinnia.managers import DRAFT


class QuickEntryTestCase(TestCase):
    """Test cases for quick_entry view"""
    urls = 'zinnia.tests.urls'

    def setUp(self):
        setup_test_template_loader(
            {'404.html': '',
             'admin/change_form.html': '',
             'zinnia/entry_detail.html': ''})

        self.original_wysiwyg = settings.WYSIWYG
        settings.WYSIWYG = None
        User.objects.create_user('user', 'user@example.com', 'password')
        User.objects.create_superuser('admin', 'admin@example.com', 'password')

    def tearDown(self):
        settings.WYSIWYG = self.original_wysiwyg
        restore_template_loaders()

    def test_quick_entry(self):
        response = self.client.get('/quick-entry/', follow=True)
        self.assertEquals(
            response.redirect_chain,
            [('http://testserver/accounts/login/?next=/quick-entry/', 302)])
        self.client.login(username='user', password='password')
        response = self.client.get('/quick-entry/', follow=True)
        self.assertEquals(
            response.redirect_chain,
            [('http://testserver/accounts/login/?next=/quick-entry/', 302)])
        self.client.logout()
        self.client.login(username='admin', password='password')
        response = self.client.get('/quick-entry/', follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/zinnia/entry/add/', 302)])
        response = self.client.post('/quick-entry/', {'content': 'test'},
                                    follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/zinnia/entry/add/'
                            '?tags=&title=&sites=1&content='
                            '%3Cp%3Etest%3C%2Fp%3E&authors=2&slug=', 302)])
        response = self.client.post('/quick-entry/',
                                    {'title': 'test', 'tags': 'test',
                                     'content': 'Test content',
                                     'save_draft': ''}, follow=True)
        entry = Entry.objects.get(title='test')
        self.assertEquals(response.redirect_chain,
                          [('http://testserver%s' %
                            entry.get_absolute_url(), 302)])
        self.assertEquals(entry.status, DRAFT)
        self.assertEquals(entry.title, 'test')
        self.assertEquals(entry.tags, 'test')
        self.assertEquals(entry.content, '<p>Test content</p>')
        response = self.client.post('/quick-entry/',
                                    {'title': 'test', 'tags': 'test-2',
                                     'content': 'Test content',
                                     'save_draft': ''}, follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/zinnia/entry/add/'
                            '?tags=test-2&title=test&sites=1&'
                            'content=%3Cp%3ETest+content%3C%2Fp%3E'
                            '&authors=2&slug=test', 302)])

    def test_quick_entry_non_ascii_title_issue_153(self):
        self.client.login(username='admin', password='password')
        response = self.client.post('/quick-entry/',
                                    {'title': u'тест', 'tags': 'test-2',
                                     'content': 'Test content',
                                     'save_draft': ''}, follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/zinnia/entry/add/'
                            '?tags=test-2&title=%D1%82%D0%B5%D1%81%D1%82'
                            '&sites=1&content=%3Cp%3ETest+content%3C%2Fp%3E'
                            '&authors=2&slug=', 302)])

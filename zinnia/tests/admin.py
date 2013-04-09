"""Test cases for Zinnia's admin"""
from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.auth.tests.utils import skipIfCustomUser

from zinnia import settings
from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.models.category import Category


@skipIfCustomUser
class EntryAdminTestCase(TestCase):
    """Test case for Entry Admin"""
    urls = 'zinnia.tests.urls'

    def setUp(self):
        self.original_wysiwyg = settings.WYSIWYG
        settings.WYSIWYG = None
        Author.objects.create_superuser(
            'admin', 'admin@example.com', 'password')
        category_1 = Category.objects.create(title='Category 1', slug='cat-1')
        Category.objects.create(title='Category 2', slug='cat-2',
                                parent=category_1)

        self.client.login(username='admin', password='password')

    def tearDown(self):
        settings.WYSIWYG = self.original_wysiwyg

    def test_entry_add_and_change(self):
        """Test the insertion of an Entry"""
        self.assertEquals(Entry.objects.count(), 0)
        post_data = {'title': 'New entry',
                     'detail_template': 'entry_detail.html',
                     'content_template': 'zinnia/_entry_detail.html',
                     'creation_date_0': '2011-01-01',
                     'creation_date_1': '12:00:00',
                     'start_publication_0': '2011-01-01',
                     'start_publication_1': '12:00:00',
                     'end_publication_0': '2042-03-15',
                     'end_publication_1': '00:00:00',
                     'status': '2',
                     'sites': '1',
                     'content': 'My content'}

        response = self.client.post('/admin/zinnia/entry/add/', post_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Entry.objects.count(), 0)

        post_data.update({'slug': 'new-entry'})
        response = self.client.post('/admin/zinnia/entry/add/',
                                    post_data, follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/zinnia/entry/', 302)])
        self.assertEquals(Entry.objects.count(), 1)


@skipIfCustomUser
class CategoryAdminTestCase(TestCase):
    """Test cases for Category Admin"""
    urls = 'zinnia.tests.urls'

    def setUp(self):
        Author.objects.create_superuser(
            'admin', 'admin@example.com', 'password')
        self.client.login(username='admin', password='password')

    def test_category_add_and_change(self):
        """Test the insertion of a Category, change error, and new insert"""
        self.assertEquals(Category.objects.count(), 0)
        post_data = {'title': 'New category',
                     'slug': 'new-category'}
        response = self.client.post('/admin/zinnia/category/add/',
                                    post_data, follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/zinnia/category/', 302)])
        self.assertEquals(Category.objects.count(), 1)

        post_data.update({'parent': '1'})
        response = self.client.post('/admin/zinnia/category/1/', post_data)
        self.assertEquals(response.status_code, 200)

        response = self.client.post('/admin/zinnia/category/add/', post_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Category.objects.count(), 1)

        post_data.update({'slug': 'new-category-2'})
        response = self.client.post('/admin/zinnia/category/add/',
                                    post_data, follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/zinnia/category/', 302)])
        self.assertEquals(Category.objects.count(), 2)

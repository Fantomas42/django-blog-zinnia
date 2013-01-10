"""Test cases for Zinnia's admin"""
from django.test import TestCase
from django.contrib.auth.models import User

from zinnia import settings
from zinnia.models.entry import Entry
from zinnia.models.category import Category


class EntryAdminTestCase(TestCase):
    """Test case for Entry Admin"""
    urls = 'zinnia.tests.urls'

    def setUp(self):
        self.original_wysiwyg = settings.WYSIWYG
        settings.WYSIWYG = None
        User.objects.create_superuser('admin', 'admin@example.com', 'password')
        category_1 = Category.objects.create(title='Category 1', slug='cat-1')
        Category.objects.create(title='Category 2', slug='cat-2',
                                parent=category_1)

        self.client.login(username='admin', password='password')

    def tearDown(self):
        settings.WYSIWYG = self.original_wysiwyg

    def test_entry_add_and_change(self):
        """Test the insertion of an Entry"""
        self.assertEquals(Entry.objects.count(), 0)
        post_data = {'title': u'New entry',
                     'detail_template': u'entry_detail.html',
                     'content_template': u'zinnia/_entry_detail.html',
                     'creation_date_0': u'2011-01-01',
                     'creation_date_1': u'12:00:00',
                     'start_publication_0': u'2011-01-01',
                     'start_publication_1': u'12:00:00',
                     'end_publication_0': u'2042-03-15',
                     'end_publication_1': u'00:00:00',
                     'status': u'2',
                     'sites': u'1',
                     'content': u'My content'}

        response = self.client.post('/admin/zinnia/entry/add/', post_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Entry.objects.count(), 0)

        post_data.update({'slug': u'new-entry'})
        response = self.client.post('/admin/zinnia/entry/add/',
                                    post_data, follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/zinnia/entry/', 302)])
        self.assertEquals(Entry.objects.count(), 1)


class CategoryAdminTestCase(TestCase):
    """Test cases for Category Admin"""
    urls = 'zinnia.tests.urls'

    def setUp(self):
        User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.client.login(username='admin', password='password')

    def test_category_add_and_change(self):
        """Test the insertion of a Category, change error, and new insert"""
        self.assertEquals(Category.objects.count(), 0)
        post_data = {'title': u'New category',
                     'slug': u'new-category'}
        response = self.client.post('/admin/zinnia/category/add/',
                                    post_data, follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/zinnia/category/', 302)])
        self.assertEquals(Category.objects.count(), 1)

        post_data.update({'parent': u'1'})
        response = self.client.post('/admin/zinnia/category/1/', post_data)
        self.assertEquals(response.status_code, 200)

        response = self.client.post('/admin/zinnia/category/add/', post_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Category.objects.count(), 1)

        post_data.update({'slug': u'new-category-2'})
        response = self.client.post('/admin/zinnia/category/add/',
                                    post_data, follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/zinnia/category/', 302)])
        self.assertEquals(Category.objects.count(), 2)

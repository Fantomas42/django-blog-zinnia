"""Test cases for Zinnia's admin"""
from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.tests.utils import skipIfCustomUser

from zinnia import settings
from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.models.category import Category
from zinnia.admin.category import CategoryAdmin


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


class BaseAdminTestCase(TestCase):
    rich_urls = 'zinnia.tests.urls'
    poor_urls = 'zinnia.tests.poor_urls'
    urls = rich_urls

    def setUp(self):
        self.site = AdminSite()

    def check_with_rich_and_poor_urls(self, func, args,
                                      result_rich, result_poor):
        self.assertEquals(func(*args), result_rich)
        self.urls = self.poor_urls
        self._urlconf_setup()
        self.assertEquals(func(*args), result_poor)
        self.urls = self.rich_urls


class CategoryAdminTestCase(BaseAdminTestCase):
    """Test cases for Category Admin"""

    def test_get_tree_path(self):
        admin = CategoryAdmin(Category, self.site)
        category = Category.objects.create(title='Category', slug='cat')

        self.check_with_rich_and_poor_urls(
            admin.get_tree_path, (category,),
            '<a href="/categories/cat/" target="blank">/cat/</a>',
            '/cat/')

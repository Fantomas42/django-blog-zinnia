"""Test cases for Zinnia's views"""
from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.template import TemplateDoesNotExist
from django.utils.translation import ugettext_lazy as _

from zinnia.models import Entry
from zinnia.models import Category
from zinnia.managers import PUBLISHED
from zinnia.settings import PAGINATION


class ZinniaViewsTestCase(TestCase):
    """Test cases for generic views used in the application,
    for reproducing and correcting issue :
    http://github.com/Fantomas42/django-blog-zinnia/issues#issue/3
    """
    urls = 'zinnia.tests.urls'
    fixtures = ['zinnia_test_data.json']

    def setUp(self):
        self.site = Site.objects.get_current()
        self.author = User.objects.get(username='admin')
        self.category = Category.objects.get(slug='tests')

    def create_published_entry(self):
        params = {'title': 'My test entry',
                  'content': 'My test content',
                  'slug': 'my-test-entry',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 1, 1),
                  'status': PUBLISHED}
        entry = Entry.objects.create(**params)
        entry.sites.add(self.site)
        entry.categories.add(self.category)
        entry.authors.add(self.author)
        return entry

    def check_publishing_context(self, url, first_expected,
                                 second_expected=None):
        """Test the numbers of entries in context of an url,"""
        response = self.client.get(url)
        self.assertEquals(len(response.context['object_list']), first_expected)
        if second_expected:
            self.create_published_entry()
            response = self.client.get(url)
            self.assertEquals(len(response.context['object_list']), second_expected)

    def test_zinnia_entry_archive_index(self):
        self.check_publishing_context('/', 2, 3)

    def test_zinnia_entry_archive_year(self):
        self.check_publishing_context('/2010/', 2, 3)

    def test_zinnia_entry_archive_month(self):
        self.check_publishing_context('/2010/01/', 1, 2)

    def test_zinnia_entry_archive_day(self):
        self.check_publishing_context('/2010/01/01/', 1, 2)

    def test_zinnia_entry_detail(self):
        entry = self.create_published_entry()
        entry.sites.clear()
        # Check a 404 error, but the 404.html may no exist
        try:
            self.assertRaises(TemplateDoesNotExist, self.client.get,
                              '/2010/01/01/my-test-entry/')
        except AssertionError:
            response = self.client.get('/2010/01/01/my-test-entry/')
            self.assertEquals(response.status_code, 404)

        entry.template = 'zinnia/_entry_detail.html'
        entry.save()
        entry.sites.add(Site.objects.get_current())
        response = self.client.get('/2010/01/01/my-test-entry/')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'zinnia/_entry_detail.html')

    def test_zinnia_entry_detail_login(self):
        entry = self.create_published_entry()
        entry.login_required = True
        entry.save()
        response = self.client.get('/2010/01/01/my-test-entry/')
        self.assertTemplateUsed(response, 'zinnia/login.html')

    def test_zinnia_entry_detail_password(self):
        entry = self.create_published_entry()
        entry.password = 'password'
        entry.save()
        response = self.client.get('/2010/01/01/my-test-entry/')
        self.assertTemplateUsed(response, 'zinnia/password.html')
        self.assertEquals(response.context['error'], False)
        response = self.client.post('/2010/01/01/my-test-entry/',
                                    {'password': 'bad_password'})
        self.assertTemplateUsed(response, 'zinnia/password.html')
        self.assertEquals(response.context['error'], True)
        response = self.client.post('/2010/01/01/my-test-entry/',
                                    {'password': 'password'})
        self.assertEquals(response.status_code, 302)

    def test_zinnia_entry_channel(self):
        self.check_publishing_context('/channel-test/', 2, 3)

    def test_zinnia_category_list(self):
        self.check_publishing_context('/categories/', 1)
        entry = Entry.objects.all()[0]
        entry.categories.add(Category.objects.create(title='New category',
                                                     slug='new-category'))
        self.check_publishing_context('/categories/', 2)

    def test_zinnia_category_detail(self):
        self.check_publishing_context('/categories/tests/', 2, 3)

    def test_zinnia_category_detail_paginated(self):
        """Test case reproducing issue #42 on category
        detail view paginated"""
        for i in range(PAGINATION):
            params = {'title': 'My entry %i' % i,
                      'content': 'My content %i' % i,
                      'slug': 'my-entry-%i' % i,
                      'creation_date': datetime(2010, 1, 1),
                      'status': PUBLISHED}
            entry = Entry.objects.create(**params)
            entry.sites.add(self.site)
            entry.categories.add(self.category)
            entry.authors.add(self.author)
        response = self.client.get('/categories/tests/')
        self.assertEquals(len(response.context['object_list']), PAGINATION)
        response = self.client.get('/categories/tests/?page=2')
        self.assertEquals(len(response.context['object_list']), 2)
        response = self.client.get('/categories/tests/page/2/')
        self.assertEquals(len(response.context['object_list']), 2)

    def test_zinnia_author_list(self):
        self.check_publishing_context('/authors/', 1)
        entry = Entry.objects.all()[0]
        entry.authors.add(User.objects.create(username='new-user',
                                              email='new_user@example.com'))
        self.check_publishing_context('/authors/', 2)

    def test_zinnia_author_detail(self):
        self.check_publishing_context('/authors/admin/', 2, 3)

    def test_zinnia_tag_list(self):
        self.check_publishing_context('/tags/', 1)
        entry = Entry.objects.all()[0]
        entry.tags = 'tests, tag'
        entry.save()
        self.check_publishing_context('/tags/', 2)

    def test_zinnia_tag_detail(self):
        self.check_publishing_context('/tags/tests/', 2, 3)

    def test_zinnia_entry_search(self):
        self.check_publishing_context('/search/?pattern=test', 2, 3)
        response = self.client.get('/search/?pattern=ab')
        self.assertEquals(len(response.context['object_list']), 0)
        self.assertEquals(response.context['error'], _('The pattern is too short'))
        response = self.client.get('/search/')
        self.assertEquals(len(response.context['object_list']), 0)
        self.assertEquals(response.context['error'], _('No pattern to search found'))

    def test_zinnia_sitemap(self):
        response = self.client.get('/sitemap/')
        self.assertEquals(len(response.context['entries']), 2)
        self.assertEquals(len(response.context['categories']), 1)
        entry = self.create_published_entry()
        entry.categories.add(Category.objects.create(title='New category',
                                                     slug='new-category'))
        response = self.client.get('/sitemap/')
        self.assertEquals(len(response.context['entries']), 3)
        self.assertEquals(len(response.context['categories']), 2)

    def test_zinnia_trackback(self):
        # Check a 404 error, but the 404.html may no exist
        try:
            self.assertRaises(TemplateDoesNotExist, self.client.post,
                              '/trackback/404/')
        except AssertionError:
            response = self.client.post('/trackback/404/')
            self.assertEquals(response.status_code, 404)
        self.assertEquals(self.client.post('/trackback/test-1/').status_code, 302)
        self.assertEquals(self.client.get('/trackback/test-1/').status_code, 302)
        entry = Entry.objects.get(slug='test-1')
        entry.pingback_enabled = False
        entry.save()
        self.assertEquals(self.client.post('/trackback/test-1/', {'url': 'http://example.com'}).content,
                          '<?xml version="1.0" encoding="utf-8"?>\n<response>\n  \n  <error>1</error>\n  '
                          '<message>Trackback is not enabled for Test 1</message>\n  \n</response>\n')
        entry.pingback_enabled = True
        entry.save()
        self.assertEquals(self.client.post('/trackback/test-1/', {'url': 'http://example.com'}).content,
                          '<?xml version="1.0" encoding="utf-8"?>\n<response>\n  \n  <error>0</error>\n  \n</response>\n')
        self.assertEquals(self.client.post('/trackback/test-1/', {'url': 'http://example.com'}).content,
                          '<?xml version="1.0" encoding="utf-8"?>\n<response>\n  \n  <error>1</error>\n  '
                          '<message>Trackback is already registered</message>\n  \n</response>\n')

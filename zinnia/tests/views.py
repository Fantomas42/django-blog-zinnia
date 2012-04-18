"""Test cases for Zinnia's views"""
from datetime import date
from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test.utils import override_settings
from django.utils.translation import ugettext_lazy as _

from zinnia.models import Entry
from zinnia.models import Category
from zinnia.managers import PUBLISHED
from zinnia.settings import PAGINATION


class ViewsBaseCase(TestCase):
    """
    Setup and utility function base case.
    """

    def setUp(self):
        self.site = Site.objects.get_current()
        self.author = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='password')
        self.category = Category.objects.create(title='Tests', slug='tests')
        params = {'title': 'Test 1',
                  'content': 'First test entry published',
                  'slug': 'test-1',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 1, 1),
                  'status': PUBLISHED}
        entry = Entry.objects.create(**params)
        entry.sites.add(self.site)
        entry.categories.add(self.category)
        entry.authors.add(self.author)

        params = {'title': 'Test 2',
                  'content': 'Second test entry published',
                  'slug': 'test-2',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 6, 1),
                  'status': PUBLISHED}
        entry = Entry.objects.create(**params)
        entry.sites.add(self.site)
        entry.categories.add(self.category)
        entry.authors.add(self.author)

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
                                 second_expected=None,
                                 friendly_context=None):
        """Test the numbers of entries in context of an url,"""
        response = self.client.get(url)
        self.assertEquals(len(response.context['object_list']), first_expected)
        if second_expected:
            self.create_published_entry()
            response = self.client.get(url)
            self.assertEquals(
                len(response.context['object_list']), second_expected)
        if friendly_context:
            self.assertEquals(
                response.context['object_list'],
                response.context[friendly_context])
        return response

    def check_capabilities(self, url, mimetype):
        """Test simple views for the Weblog capabilities"""
        response = self.client.get(url)
        self.assertEquals(response['Content-Type'], mimetype)
        self.assertTrue('protocol' in response.context)

ViewsBaseCase = override_settings(
    TEMPLATE_CONTEXT_PROCESSORS=(
        'django.core.context_processors.request',
        ),
    TEMPLATE_LOADERS=(
        ('django.template.loaders.cached.Loader', (
            'django.template.loaders.app_directories.Loader',
            'django.template.loaders.eggs.Loader',
            )
         ),
        ))(ViewsBaseCase)


class ZinniaViewsTestCase(ViewsBaseCase):
    """
    Test cases for generic views used in the application,
    for reproducing and correcting issue :
    http://github.com/Fantomas42/django-blog-zinnia/issues#issue/3
    """
    urls = 'zinnia.tests.urls'

    def test_zinnia_entry_archive_index(self):
        self.check_publishing_context('/', 2, 3, 'entry_list')

    def test_zinnia_entry_archive_year(self):
        self.check_publishing_context('/2010/', 2, 3, 'entry_list')

    def test_zinnia_entry_archive_week(self):
        response = self.check_publishing_context('/2010/week/00/', 1, 2,
                                                 'entry_list')
        # All days in a new year preceding the first Monday
        # are considered to be in week 0.
        self.assertEquals(response.context['week'], date(2009, 12, 28))
        self.assertEquals(response.context['week_end_day'], date(2010, 1, 3))

    def test_zinnia_entry_archive_month(self):
        response = self.check_publishing_context('/2010/01/',
                                                 1, 2, 'entry_list')
        self.assertEquals(response.context['previous_month'], None)
        self.assertEquals(response.context['next_month'], date(2010, 6, 1))
        response = self.client.get('/2010/06/')
        self.assertEquals(response.context['previous_month'], date(2010, 1, 1))
        self.assertEquals(response.context['next_month'], None)

    def test_zinnia_entry_archive_day(self):
        response = self.check_publishing_context('/2010/01/01/',
                                                 1, 2, 'entry_list')
        self.assertEquals(response.context['previous_month'], None)
        self.assertEquals(response.context['next_month'], date(2010, 6, 1))
        self.assertEquals(response.context['previous_day'], None)
        self.assertEquals(response.context['next_day'], date(2010, 6, 1))
        response = self.client.get('/2010/06/01/')
        self.assertEquals(response.context['previous_month'], date(2010, 1, 1))
        self.assertEquals(response.context['next_month'], None)
        self.assertEquals(response.context['previous_day'], date(2010, 1, 1))
        self.assertEquals(response.context['next_day'], None)

    def test_zinnia_entry_archive_today(self):
        response = self.client.get('/today/')
        self.assertEquals(response.context['day'], datetime.today().date())
        self.assertTemplateUsed(response, 'zinnia/entry_archive_today.html')
        self.assertEquals(response.context['previous_month'], date(2010, 6, 1))
        self.assertEquals(response.context['next_month'], None)
        self.assertEquals(response.context['previous_day'], date(2010, 6, 1))
        self.assertEquals(response.context['next_day'], None)

    def test_zinnia_entry_shortlink(self):
        response = self.client.get('/1/', follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/2010/01/01/test-1/', 301)])

    def test_zinnia_entry_detail(self):
        entry = self.create_published_entry()
        entry.sites.clear()
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
        response = self.client.post('/2010/01/01/my-test-entry/',
                                    {'username': 'admin',
                                     'password': 'password'})
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'zinnia/entry_detail.html')

    def test_zinnia_entry_detail_password(self):
        entry = self.create_published_entry()
        entry.password = 'password'
        entry.save()
        response = self.client.get('/2010/01/01/my-test-entry/')
        self.assertTemplateUsed(response, 'zinnia/password.html')
        self.assertEquals(response.context['error'], False)
        response = self.client.post('/2010/01/01/my-test-entry/',
                                    {'entry_password': 'bad_password'})
        self.assertTemplateUsed(response, 'zinnia/password.html')
        self.assertEquals(response.context['error'], True)
        response = self.client.post('/2010/01/01/my-test-entry/',
                                    {'entry_password': 'password'})
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'zinnia/entry_detail.html')

    def test_zinnia_entry_detail_login_password(self):
        entry = self.create_published_entry()
        entry.password = 'password'
        entry.login_required = True
        entry.save()
        response = self.client.get('/2010/01/01/my-test-entry/')
        self.assertTemplateUsed(response, 'zinnia/login.html')
        response = self.client.post('/2010/01/01/my-test-entry/',
                                    {'username': 'admin',
                                     'password': 'password'})
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'zinnia/password.html')
        self.assertEquals(response.context['error'], False)
        response = self.client.post('/2010/01/01/my-test-entry/',
                                    {'entry_password': 'password'})
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'zinnia/entry_detail.html')

    def test_zinnia_entry_channel(self):
        self.check_publishing_context('/channel-test/', 2, 3)

    def test_zinnia_category_list(self):
        self.check_publishing_context('/categories/', 1,
                                      friendly_context='category_list')
        entry = Entry.objects.all()[0]
        entry.categories.add(Category.objects.create(title='New category',
                                                     slug='new-category'))
        self.check_publishing_context('/categories/', 2)

    def test_zinnia_category_detail(self):
        response = self.check_publishing_context('/categories/tests/', 2, 3,
                                                 'entry_list')
        self.assertTemplateUsed(response, 'zinnia/category/entry_list.html')
        self.assertEquals(response.context['category'].slug, 'tests')

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
        self.assertEquals(response.context['category'].slug, 'tests')

    def test_zinnia_author_list(self):
        self.check_publishing_context('/authors/', 1,
                                      friendly_context='author_list')
        user = User.objects.create(username='new-user',
                                   email='new_user@example.com')
        self.check_publishing_context('/authors/', 1)
        entry = Entry.objects.all()[0]
        entry.authors.add(user)
        self.check_publishing_context('/authors/', 2)

    def test_zinnia_author_detail(self):
        response = self.check_publishing_context('/authors/admin/', 2, 3,
                                                 'entry_list')
        self.assertTemplateUsed(response, 'zinnia/author/entry_list.html')
        self.assertEquals(response.context['author'].username, 'admin')

    def test_zinnia_tag_list(self):
        self.check_publishing_context('/tags/', 1,
                                      friendly_context='tag_list')
        entry = Entry.objects.all()[0]
        entry.tags = 'tests, tag'
        entry.save()
        self.check_publishing_context('/tags/', 2)

    def test_zinnia_tag_detail(self):
        response = self.check_publishing_context('/tags/tests/', 2, 3,
                                                 'entry_list')
        self.assertTemplateUsed(response, 'zinnia/tag/entry_list.html')
        self.assertEquals(response.context['tag'].name, 'tests')
        response = self.client.get('/tags/404/')
        self.assertEquals(response.status_code, 404)

    def test_zinnia_entry_search(self):
        self.check_publishing_context('/search/?pattern=test', 2, 3,
                                      'entry_list')
        response = self.client.get('/search/?pattern=ab')
        self.assertEquals(len(response.context['object_list']), 0)
        self.assertEquals(response.context['error'],
                          _('The pattern is too short'))
        response = self.client.get('/search/')
        self.assertEquals(len(response.context['object_list']), 0)
        self.assertEquals(response.context['error'],
                          _('No pattern to search found'))

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
        response = self.client.post('/trackback/404/')
        self.assertEquals(response.status_code, 404)
        self.assertEquals(
            self.client.post('/trackback/1/').status_code, 301)
        self.assertEquals(
            self.client.get('/trackback/1/').status_code, 301)
        entry = Entry.objects.get(slug='test-1')
        entry.pingback_enabled = False
        entry.save()
        self.assertEquals(
            self.client.post('/trackback/1/',
                             {'url': 'http://example.com'}).content,
            '<?xml version="1.0" encoding="utf-8"?>\n<response>\n  \n  '
            '<error>1</error>\n  <message>Trackback is not enabled for '
            'Test 1</message>\n  \n</response>\n')
        entry.pingback_enabled = True
        entry.save()
        self.assertEquals(
            self.client.post('/trackback/1/',
                             {'url': 'http://example.com'}).content,
            '<?xml version="1.0" encoding="utf-8"?>\n<response>\n  \n  '
            '<error>0</error>\n  \n</response>\n')
        self.assertEquals(
            self.client.post('/trackback/1/',
                             {'url': 'http://example.com'}).content,
            '<?xml version="1.0" encoding="utf-8"?>\n<response>\n  \n  '
            '<error>1</error>\n  <message>Trackback is already registered'
            '</message>\n  \n</response>\n')

    def test_capabilities(self):
        self.check_capabilities('/humans.txt', 'text/plain')
        self.check_capabilities('/rsd.xml', 'application/rsd+xml')
        self.check_capabilities('/wlwmanifest.xml',
                                'application/wlwmanifest+xml')
        self.check_capabilities('/opensearch.xml',
                                'application/opensearchdescription+xml')


class ZinniaCustomDetailViews(ViewsBaseCase):
    """
    Tests with an alternate urls.py that modifies how author_detail,
    tags_detail and categories_detail views to be called with a custom
    template_name keyword argument and an extra_context.
    """
    urls = 'zinnia.tests.custom_views_detail_urls'

    def test_custom_category_detail(self):
        response = self.check_publishing_context('/categories/tests/', 2, 3)
        self.assertTemplateUsed(response, 'zinnia/entry_list.html')
        self.assertEquals(response.context['category'].slug, 'tests')
        self.assertEquals(response.context['extra'], 'context')

    def test_custom_author_detail(self):
        response = self.check_publishing_context('/authors/admin/', 2, 3)
        self.assertTemplateUsed(response, 'zinnia/entry_list.html')
        self.assertEquals(response.context['author'].username, 'admin')
        self.assertEquals(response.context['extra'], 'context')

    def test_custom_tag_detail(self):
        response = self.check_publishing_context('/tags/tests/', 2, 3)
        self.assertTemplateUsed(response, 'zinnia/entry_list.html')
        self.assertEquals(response.context['tag'].name, 'tests')
        self.assertEquals(response.context['extra'], 'context')

"""Test cases for Zinnia's views"""
from __future__ import with_statement
from datetime import date

from django.test import TestCase
from django.utils import timezone
from django.contrib import comments
from django.contrib.sites.models import Site
from django.test.utils import override_settings
from django.test.utils import restore_template_loaders
from django.test.utils import setup_test_template_loader
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import update_last_login

from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.models.category import Category
from zinnia.managers import PUBLISHED
from zinnia.settings import PAGINATION
from zinnia.tests.utils import datetime
from zinnia.flags import get_user_flagger
from zinnia.signals import connect_discussion_signals
from zinnia.signals import disconnect_discussion_signals


class ViewsBaseCase(TestCase):
    """
    Setup and utility function base case.
    """

    def setUp(self):
        self.site = Site.objects.get_current()
        self.author = Author.objects.create_user(username='admin',
                                                 email='admin@example.com',
                                                 password='password')
        self.category = Category.objects.create(title='Tests', slug='tests')
        params = {'title': 'Test 1',
                  'content': 'First test entry published',
                  'slug': 'test-1',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 1, 1, 13, 25),
                  'status': PUBLISHED}
        entry = Entry.objects.create(**params)
        entry.sites.add(self.site)
        entry.categories.add(self.category)
        entry.authors.add(self.author)

        params = {'title': 'Test 2',
                  'content': 'Second test entry published',
                  'slug': 'test-2',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 6, 1, 12, 12),
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
                  'creation_date': datetime(2010, 1, 1, 15, 15),
                  'status': PUBLISHED}
        entry = Entry.objects.create(**params)
        entry.sites.add(self.site)
        entry.categories.add(self.category)
        entry.authors.add(self.author)
        return entry

    def check_publishing_context(self, url, first_expected,
                                 second_expected=None,
                                 friendly_context=None,
                                 queries=None):
        """Test the numbers of entries in context of an url,"""
        if queries is not None:
            with self.assertNumQueries(queries):
                response = self.client.get(url)
        else:
            response = self.client.get(url)
        self.assertEquals(len(response.context['object_list']),
                          first_expected)
        if second_expected:
            self.create_published_entry()
            response = self.client.get(url)
            self.assertEquals(len(response.context['object_list']),
                              second_expected)
        if friendly_context:
            self.assertEquals(
                response.context['object_list'],
                response.context[friendly_context])
        return response

    def check_capabilities(self, url, mimetype, queries=0):
        """Test simple views for the Weblog capabilities"""
        with self.assertNumQueries(queries):
            response = self.client.get(url)
        self.assertEquals(response['Content-Type'], mimetype)
        self.assertTrue('protocol' in response.context)

ViewsBaseCase = override_settings(
    TEMPLATE_CONTEXT_PROCESSORS=(
        'django.core.context_processors.request',
    ))(ViewsBaseCase)


class ZinniaViewsTestCase(ViewsBaseCase):
    """
    Test cases for generic views used in the application,
    for reproducing and correcting issue :
    http://github.com/Fantomas42/django-blog-zinnia/issues#issue/3
    """
    urls = 'zinnia.tests.urls'

    def tearDown(self):
        """Always try to restore the initial template loaders
        even if the test_template_loader has not been enabled,
        to avoid cascading errors if a test fails"""
        try:
            restore_template_loaders()
        except AttributeError:
            pass

    def test_zinnia_entry_archive_index(self):
        template_name_today = 'zinnia/archives/%s/entry_archive.html' % \
                              date.today().strftime('%Y/%m/%d')
        setup_test_template_loader(
            {template_name_today: ''})
        response = self.check_publishing_context(
            '/', 2, 3, 'entry_list', 2)
        self.assertTemplateUsed(response, template_name_today)
        restore_template_loaders()

    def test_zinnia_entry_archive_year(self):
        setup_test_template_loader(
            {'zinnia/archives/2010/entry_archive_year.html': ''})
        response = self.check_publishing_context(
            '/2010/', 2, 3, 'entry_list', 2)
        self.assertTemplateUsed(
            response, 'zinnia/archives/2010/entry_archive_year.html')
        restore_template_loaders()

    def test_zinnia_entry_archive_week(self):
        setup_test_template_loader(
            {'zinnia/archives/2010/week/00/entry_archive_week.html': ''})
        response = self.check_publishing_context(
            '/2010/week/00/', 1, 2, 'entry_list', 1)
        self.assertTemplateUsed(
            response, 'zinnia/archives/2010/week/00/entry_archive_week.html')
        # All days in a new year preceding the first Monday
        # are considered to be in week 0.
        self.assertEquals(response.context['week'], date(2009, 12, 28))
        self.assertEquals(response.context['week_end_day'], date(2010, 1, 3))
        restore_template_loaders()

    def test_zinnia_entry_archive_month(self):
        setup_test_template_loader(
            {'zinnia/archives/2010/month/01/entry_archive_month.html': '',
             'zinnia/entry_archive_month.html': ''})
        response = self.check_publishing_context(
            '/2010/01/', 1, 2, 'entry_list', 4)
        self.assertTemplateUsed(
            response, 'zinnia/archives/2010/month/01/entry_archive_month.html')
        self.assertEquals(response.context['previous_month'], None)
        self.assertEquals(response.context['next_month'], date(2010, 6, 1))
        response = self.client.get('/2010/06/')
        self.assertEquals(response.context['previous_month'], date(2010, 1, 1))
        self.assertEquals(response.context['next_month'], None)
        response = self.client.get('/2009/12/')
        self.assertEquals(response.context['previous_month'], None)
        self.assertEquals(response.context['next_month'], date(2010, 1, 1))
        restore_template_loaders()

    def test_zinnia_entry_archive_day(self):
        setup_test_template_loader(
            {'zinnia/archives/2010/01/01/entry_archive_day.html': '',
             'zinnia/entry_archive_day.html': ''})
        response = self.check_publishing_context(
            '/2010/01/01/', 1, 2, 'entry_list', 5)
        self.assertTemplateUsed(
            response, 'zinnia/archives/2010/01/01/entry_archive_day.html')
        self.assertEquals(response.context['previous_month'], None)
        self.assertEquals(response.context['next_month'], date(2010, 6, 1))
        self.assertEquals(response.context['previous_day'], None)
        self.assertEquals(response.context['next_day'], date(2010, 6, 1))
        response = self.client.get('/2010/06/01/')
        self.assertEquals(response.context['previous_month'], date(2010, 1, 1))
        self.assertEquals(response.context['next_month'], None)
        self.assertEquals(response.context['previous_day'], date(2010, 1, 1))
        self.assertEquals(response.context['next_day'], None)
        restore_template_loaders()

    def test_zinnia_entry_archive_today(self):
        setup_test_template_loader(
            {'zinnia/entry_archive_today.html': ''})
        with self.assertNumQueries(5):
            response = self.client.get('/today/')
        self.assertEquals(response.context['day'], timezone.localtime(
            timezone.now()).date())
        self.assertTemplateUsed(response, 'zinnia/entry_archive_today.html')
        self.assertEquals(response.context['previous_month'], date(2010, 6, 1))
        self.assertEquals(response.context['next_month'], None)
        self.assertEquals(response.context['previous_day'], date(2010, 6, 1))
        self.assertEquals(response.context['next_day'], None)
        restore_template_loaders()

    def test_zinnia_entry_shortlink(self):
        with self.assertNumQueries(1):
            response = self.client.get('/1/')
        self.assertEquals(response.status_code, 301)
        self.assertEquals(response['Location'],
                          'http://testserver/2010/01/01/test-1/')

    def test_zinnia_entry_detail(self):
        setup_test_template_loader(
            {'zinnia/_entry_detail.html': '',
             '404.html': ''})
        entry = self.create_published_entry()
        entry.sites.clear()
        response = self.client.get('/2010/01/01/my-test-entry/')
        self.assertEquals(response.status_code, 404)
        entry.detail_template = '_entry_detail.html'
        entry.save()
        entry.sites.add(Site.objects.get_current())
        with self.assertNumQueries(1):
            response = self.client.get('/2010/01/01/my-test-entry/')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'zinnia/_entry_detail.html')
        restore_template_loaders()

    def test_zinnia_entry_detail_login(self):
        setup_test_template_loader(
            {'zinnia/entry_detail.html': '',
             'zinnia/login.html': ''})
        entry = self.create_published_entry()
        entry.login_required = True
        entry.save()
        with self.assertNumQueries(4):
            response = self.client.get('/2010/01/01/my-test-entry/')
        self.assertTemplateUsed(response, 'zinnia/login.html')
        response = self.client.post('/2010/01/01/my-test-entry/',
                                    {'username': 'admin',
                                     'password': 'password'})
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'zinnia/entry_detail.html')
        restore_template_loaders()

    def test_zinnia_entry_detail_password(self):
        setup_test_template_loader(
            {'zinnia/entry_detail.html': '',
             'zinnia/password.html': ''})
        entry = self.create_published_entry()
        entry.password = 'password'
        entry.save()
        with self.assertNumQueries(1):
            response = self.client.get('/2010/01/01/my-test-entry/')
        self.assertTemplateUsed(response, 'zinnia/password.html')
        self.assertEquals(response.context['error'], False)
        with self.assertNumQueries(4):
            response = self.client.post('/2010/01/01/my-test-entry/',
                                        {'entry_password': 'bad_password'})
        self.assertTemplateUsed(response, 'zinnia/password.html')
        self.assertEquals(response.context['error'], True)
        with self.assertNumQueries(5):
            response = self.client.post('/2010/01/01/my-test-entry/',
                                        {'entry_password': 'password'})
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'zinnia/entry_detail.html')
        restore_template_loaders()

    def test_zinnia_entry_detail_login_password(self):
        user_logged_in.disconnect(update_last_login)
        setup_test_template_loader(
            {'zinnia/entry_detail.html': '',
             'zinnia/login.html': '',
             'zinnia/password.html': ''})
        entry = self.create_published_entry()
        entry.password = 'password'
        entry.login_required = True
        entry.save()
        with self.assertNumQueries(4):
            response = self.client.get('/2010/01/01/my-test-entry/')
        self.assertTemplateUsed(response, 'zinnia/login.html')
        with self.assertNumQueries(9):
            response = self.client.post('/2010/01/01/my-test-entry/',
                                        {'username': 'admin',
                                         'password': 'password'})
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'zinnia/password.html')
        self.assertEquals(response.context['error'], False)
        with self.assertNumQueries(6):
            response = self.client.post('/2010/01/01/my-test-entry/',
                                        {'entry_password': 'password'})
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'zinnia/entry_detail.html')
        restore_template_loaders()
        user_logged_in.connect(update_last_login)

    def test_zinnia_entry_channel(self):
        setup_test_template_loader(
            {'zinnia/entry_list.html': ''})
        self.check_publishing_context(
            '/channel-test/', 2, 3, 'entry_list', 1)
        restore_template_loaders()

    def test_zinnia_category_list(self):
        setup_test_template_loader(
            {'zinnia/category_list.html': ''})
        self.check_publishing_context(
            '/categories/', 1,
            friendly_context='category_list',
            queries=0)
        entry = Entry.objects.all()[0]
        entry.categories.add(Category.objects.create(
            title='New category', slug='new-category'))
        self.check_publishing_context('/categories/', 2)
        restore_template_loaders()

    def test_zinnia_category_detail(self):
        setup_test_template_loader(
            {'zinnia/category/tests/entry_list.html': ''})
        response = self.check_publishing_context(
            '/categories/tests/', 2, 3, 'entry_list', 2)
        self.assertTemplateUsed(
            response, 'zinnia/category/tests/entry_list.html')
        self.assertEquals(response.context['category'].slug, 'tests')
        restore_template_loaders()

    def test_zinnia_category_detail_paginated(self):
        """Test case reproducing issue #42 on category
        detail view paginated"""
        setup_test_template_loader(
            {'zinnia/entry_list.html': ''})
        for i in range(PAGINATION):
            params = {'title': 'My entry %i' % i,
                      'content': 'My content %i' % i,
                      'slug': 'my-entry-%i' % i,
                      'creation_date': datetime(2010, 1, 1),
                      'status': PUBLISHED}
            entry = Entry.objects.create(**params)
            entry.sites.add(self.site)
            entry.categories.add(self.category)
        response = self.client.get('/categories/tests/')
        self.assertEquals(len(response.context['object_list']), PAGINATION)
        response = self.client.get('/categories/tests/?page=2')
        self.assertEquals(len(response.context['object_list']), 2)
        response = self.client.get('/categories/tests/page/2/')
        self.assertEquals(len(response.context['object_list']), 2)
        self.assertEquals(response.context['category'].slug, 'tests')
        restore_template_loaders()

    def test_zinnia_author_list(self):
        setup_test_template_loader(
            {'zinnia/author_list.html': ''})
        self.check_publishing_context(
            '/authors/', 1,
            friendly_context='author_list',
            queries=0)
        user = Author.objects.create(username='new-user',
                                     email='new_user@example.com')
        self.check_publishing_context('/authors/', 1)
        entry = Entry.objects.all()[0]
        entry.authors.add(user)
        self.check_publishing_context('/authors/', 2)
        restore_template_loaders()

    def test_zinnia_author_detail(self):
        setup_test_template_loader(
            {'zinnia/author/admin/entry_list.html': ''})
        response = self.check_publishing_context(
            '/authors/admin/', 2, 3, 'entry_list', 2)
        self.assertTemplateUsed(
            response, 'zinnia/author/admin/entry_list.html')
        self.assertEquals(response.context['author'].username, 'admin')
        restore_template_loaders()

    def test_zinnia_author_detail_paginated(self):
        """Test case reproducing issue #207 on author
        detail view paginated"""
        setup_test_template_loader(
            {'zinnia/entry_list.html': ''})
        for i in range(PAGINATION):
            params = {'title': 'My entry %i' % i,
                      'content': 'My content %i' % i,
                      'slug': 'my-entry-%i' % i,
                      'creation_date': datetime(2010, 1, 1),
                      'status': PUBLISHED}
            entry = Entry.objects.create(**params)
            entry.sites.add(self.site)
            entry.authors.add(self.author)
        response = self.client.get('/authors/admin/')
        self.assertEquals(len(response.context['object_list']), PAGINATION)
        response = self.client.get('/authors/admin/?page=2')
        self.assertEquals(len(response.context['object_list']), 2)
        response = self.client.get('/authors/admin/page/2/')
        self.assertEquals(len(response.context['object_list']), 2)
        self.assertEquals(response.context['author'].username, 'admin')
        restore_template_loaders()

    def test_zinnia_tag_list(self):
        setup_test_template_loader(
            {'zinnia/tag_list.html': ''})
        self.check_publishing_context(
            '/tags/', 1,
            friendly_context='tag_list',
            queries=1)
        entry = Entry.objects.all()[0]
        entry.tags = 'tests, tag'
        entry.save()
        self.check_publishing_context('/tags/', 2)
        restore_template_loaders()

    def test_zinnia_tag_detail(self):
        setup_test_template_loader(
            {'zinnia/tag/tests/entry_list.html': '',
             '404.html': ''})
        response = self.check_publishing_context(
            '/tags/tests/', 2, 3, 'entry_list', 2)
        self.assertTemplateUsed(
            response, 'zinnia/tag/tests/entry_list.html')
        self.assertEquals(response.context['tag'].name, 'tests')
        response = self.client.get('/tags/404/')
        self.assertEquals(response.status_code, 404)
        restore_template_loaders()

    def test_zinnia_tag_detail_paginated(self):
        setup_test_template_loader(
            {'zinnia/entry_list.html': ''})
        for i in range(PAGINATION):
            params = {'title': 'My entry %i' % i,
                      'content': 'My content %i' % i,
                      'slug': 'my-entry-%i' % i,
                      'tags': 'tests',
                      'creation_date': datetime(2010, 1, 1),
                      'status': PUBLISHED}
            entry = Entry.objects.create(**params)
            entry.sites.add(self.site)
        response = self.client.get('/tags/tests/')
        self.assertEquals(len(response.context['object_list']), PAGINATION)
        response = self.client.get('/tags/tests/?page=2')
        self.assertEquals(len(response.context['object_list']), 2)
        response = self.client.get('/tags/tests/page/2/')
        self.assertEquals(len(response.context['object_list']), 2)
        self.assertEquals(response.context['tag'].name, 'tests')
        restore_template_loaders()

    def test_zinnia_entry_search(self):
        setup_test_template_loader(
            {'zinnia/entry_search.html': ''})
        self.check_publishing_context(
            '/search/?pattern=test', 2, 3, 'entry_list', 1)
        response = self.client.get('/search/?pattern=ab')
        self.assertEquals(len(response.context['object_list']), 0)
        self.assertEquals(response.context['error'],
                          _('The pattern is too short'))
        response = self.client.get('/search/')
        self.assertEquals(len(response.context['object_list']), 0)
        self.assertEquals(response.context['error'],
                          _('No pattern to search found'))
        restore_template_loaders()

    def test_zinnia_entry_random(self):
        setup_test_template_loader(
            {'zinnia/entry_detail.html': ''})
        response = self.client.get('/random/', follow=True)
        self.assertTrue(response.redirect_chain[0][0].startswith(
            'http://testserver/2010/'))
        self.assertEquals(response.redirect_chain[0][1], 302)
        restore_template_loaders()

    def test_zinnia_sitemap(self):
        setup_test_template_loader(
            {'zinnia/sitemap.html': ''})
        with self.assertNumQueries(0):
            response = self.client.get('/sitemap/')
        self.assertEquals(len(response.context['entries']), 2)
        self.assertEquals(len(response.context['categories']), 1)
        entry = self.create_published_entry()
        entry.categories.add(Category.objects.create(title='New category',
                                                     slug='new-category'))
        response = self.client.get('/sitemap/')
        self.assertEquals(len(response.context['entries']), 3)
        self.assertEquals(len(response.context['categories']), 2)
        restore_template_loaders()

    def test_zinnia_trackback(self):
        setup_test_template_loader(
            {'404.html': ''})
        response = self.client.post('/trackback/404/')
        self.assertEquals(response.status_code, 404)
        restore_template_loaders()
        self.assertEquals(
            self.client.post('/trackback/1/').status_code, 301)
        self.assertEquals(
            self.client.get('/trackback/1/').status_code, 301)
        entry = Entry.objects.get(slug='test-1')
        self.assertEquals(entry.trackback_count, 0)
        entry.trackback_enabled = False
        entry.save()
        self.assertEquals(
            self.client.post('/trackback/1/',
                             {'url': 'http://example.com'}).content,
            '<?xml version="1.0" encoding="utf-8"?>\n<response>\n  \n  '
            '<error>1</error>\n  <message>Trackback is not enabled for '
            'Test 1</message>\n  \n</response>\n')
        entry.trackback_enabled = True
        entry.save()
        connect_discussion_signals()
        get_user_flagger()  # Memoize user flagger for stable query number
        with self.assertNumQueries(6):
            self.assertEquals(
                self.client.post('/trackback/1/',
                                 {'url': 'http://example.com'}).content,
                '<?xml version="1.0" encoding="utf-8"?>\n<response>\n  \n  '
                '<error>0</error>\n  \n</response>\n')
        disconnect_discussion_signals()
        entry = Entry.objects.get(pk=entry.pk)
        self.assertEquals(entry.trackback_count, 1)
        self.assertEquals(
            self.client.post('/trackback/1/',
                             {'url': 'http://example.com'}).content,
            '<?xml version="1.0" encoding="utf-8"?>\n<response>\n  \n  '
            '<error>1</error>\n  <message>Trackback is already registered'
            '</message>\n  \n</response>\n')

    def test_zinnia_trackback_on_entry_without_author(self):
        entry = Entry.objects.get(slug='test-1')
        entry.authors.clear()
        self.assertEquals(
            self.client.post('/trackback/1/',
                             {'url': 'http://example.com'}).content,
            '<?xml version="1.0" encoding="utf-8"?>\n<response>\n  \n  '
            '<error>0</error>\n  \n</response>\n')

    def test_capabilities(self):
        self.check_capabilities('/humans.txt', 'text/plain', 0)
        self.check_capabilities('/rsd.xml', 'application/rsd+xml', 0)
        self.check_capabilities('/wlwmanifest.xml',
                                'application/wlwmanifest+xml', 0)
        self.check_capabilities('/opensearch.xml',
                                'application/opensearchdescription+xml', 1)

    def test_comment_success(self):
        setup_test_template_loader(
            {'comments/zinnia/entry/posted.html': '',
             'zinnia/entry_list.html': ''})
        with self.assertNumQueries(0):
            response = self.client.get('/comments/success/')
        self.assertTemplateUsed(response, 'comments/zinnia/entry/posted.html')
        self.assertEquals(response.context['comment'], None)

        with self.assertNumQueries(1):
            response = self.client.get('/comments/success/?c=42')
        self.assertEquals(response.context['comment'], None)

        comment = comments.get_model().objects.create(
            comment='My Comment 1', content_object=self.category,
            site=self.site, is_public=False)
        with self.assertNumQueries(1):
            response = self.client.get('/comments/success/?c=1')
        self.assertEquals(response.context['comment'], comment)
        comment.is_public = True
        comment.save()
        with self.assertNumQueries(5):
            response = self.client.get('/comments/success/?c=1', follow=True)
        self.assertEquals(
            response.redirect_chain[1],
            ('http://example.com/categories/tests/', 302))
        restore_template_loaders()


class ZinniaCustomDetailViews(ViewsBaseCase):
    """
    Tests with an alternate urls.py that modifies how author_detail,
    tags_detail and categories_detail views to be called with a custom
    template_name keyword argument and an extra_context.
    """
    urls = 'zinnia.tests.custom_views_detail_urls'

    def setUp(self):
        """We don't need to generate the full template
        to make the tests working"""
        super(ZinniaCustomDetailViews, self).setUp()
        setup_test_template_loader(
            {'zinnia/entry_search.html': ''})

    def tearDown(self):
        restore_template_loaders()

    def test_custom_category_detail(self):
        response = self.check_publishing_context('/categories/tests/', 2, 3)
        self.assertTemplateUsed(response, 'zinnia/entry_search.html')
        self.assertEquals(response.context['category'].slug, 'tests')
        self.assertEquals(response.context['extra'], 'context')

    def test_custom_author_detail(self):
        response = self.check_publishing_context('/authors/admin/', 2, 3)
        self.assertTemplateUsed(response, 'zinnia/entry_search.html')
        self.assertEquals(response.context['author'].username, 'admin')
        self.assertEquals(response.context['extra'], 'context')

    def test_custom_tag_detail(self):
        response = self.check_publishing_context('/tags/tests/', 2, 3)
        self.assertTemplateUsed(response, 'zinnia/entry_search.html')
        self.assertEquals(response.context['tag'].name, 'tests')
        self.assertEquals(response.context['extra'], 'context')

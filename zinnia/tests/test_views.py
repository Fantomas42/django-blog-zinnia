# coding=utf-8
"""Test cases for Zinnia's views"""
from datetime import date

from django.contrib.auth.models import update_last_login
from django.contrib.auth.signals import user_logged_in
from django.contrib.sites.models import Site
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import django_comments as comments

from zinnia.flags import get_user_flagger
from zinnia.managers import DRAFT
from zinnia.managers import PUBLISHED
from zinnia.models.author import Author
from zinnia.models.category import Category
from zinnia.models.entry import Entry
from zinnia.settings import PAGINATION
from zinnia.signals import connect_discussion_signals
from zinnia.signals import disconnect_discussion_signals
from zinnia.signals import disconnect_entry_signals
from zinnia.tests.utils import datetime
from zinnia.tests.utils import skip_if_custom_user
from zinnia.tests.utils import url_equal
from zinnia.url_shortener.backends.default import base36
from zinnia.views import quick_entry


@skip_if_custom_user
@override_settings(
    SESSION_ENGINE='django.contrib.sessions.backends.cache',
    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.request',
                ],
                'loaders': [
                    'zinnia.tests.utils.VoidLoader',
                ]
            }
        }
    ]
)
class ViewsBaseCase(TestCase):
    """
    Setup and utility function base case.
    """

    def setUp(self):
        disconnect_entry_signals()
        disconnect_discussion_signals()
        self.site = Site.objects.get_current()
        self.author = Author.objects.create_user(username='admin',
                                                 email='admin@example.com',
                                                 password='password')
        self.category = Category.objects.create(title='Tests', slug='tests')
        params = {'title': 'Test 1',
                  'content': 'First test entry published',
                  'slug': 'test-1',
                  'tags': 'tests',
                  'publication_date': datetime(2010, 1, 1, 23, 0),
                  'status': PUBLISHED}
        entry = Entry.objects.create(**params)
        entry.sites.add(self.site)
        entry.categories.add(self.category)
        entry.authors.add(self.author)
        self.first_entry = entry

        params = {'title': 'Test 2',
                  'content': 'Second test entry published',
                  'slug': 'test-2',
                  'tags': 'tests',
                  'publication_date': datetime(2010, 5, 31, 23, 00),
                  'status': PUBLISHED}
        entry = Entry.objects.create(**params)
        entry.sites.add(self.site)
        entry.categories.add(self.category)
        entry.authors.add(self.author)
        self.second_entry = entry

    def create_published_entry(self):
        params = {'title': 'My test entry',
                  'content': 'My test content',
                  'slug': 'my-test-entry',
                  'tags': 'tests',
                  'publication_date': datetime(2010, 1, 1, 23, 0),
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
        """Test the numbers of entries in context of an url."""
        if queries is not None:
            with self.assertNumQueries(queries):
                response = self.client.get(url)
        else:
            response = self.client.get(url)
        self.assertEqual(len(response.context['object_list']),
                         first_expected)
        if second_expected:
            self.create_published_entry()
            response = self.client.get(url)
            self.assertEqual(len(response.context['object_list']),
                             second_expected)
        if friendly_context:
            self.assertEqual(
                response.context['object_list'],
                response.context[friendly_context])
        return response

    def check_capabilities(self, url, mimetype, queries=0):
        """Test simple views for the Weblog capabilities"""
        with self.assertNumQueries(queries):
            response = self.client.get(url)
        self.assertEqual(response['Content-Type'], mimetype)
        self.assertTrue('protocol' in response.context)


@override_settings(
    ROOT_URLCONF='zinnia.tests.implementations.urls.default'
)
class ViewsTestCase(ViewsBaseCase):
    """
    Test cases for generic views used in the application,
    for reproducing and correcting issue :
    http://github.com/Fantomas42/django-blog-zinnia/issues#issue/3
    """

    @override_settings(USE_TZ=False)
    def test_zinnia_entry_archive_index_no_timezone(self):
        template_name_today = 'zinnia/archives/%s/entry_archive.html' % \
                              date.today().strftime('%Y/%m/%d')
        response = self.check_publishing_context(
            '/', 2, 3, 'entry_list', 2)
        self.assertTemplateUsed(response, template_name_today)

    @override_settings(USE_TZ=True, TIME_ZONE='Europe/Paris')
    def test_zinnia_entry_archive_index_with_timezone(self):
        template_name_today = 'zinnia/archives/%s/entry_archive.html' % \
                              timezone.localtime(timezone.now()
                                                 ).strftime('%Y/%m/%d')
        response = self.check_publishing_context(
            '/', 2, 3, 'entry_list', 2)
        self.assertTemplateUsed(response, template_name_today)

    @override_settings(USE_TZ=False)
    def test_zinnia_entry_archive_year_no_timezone(self):
        response = self.check_publishing_context(
            '/2010/', 2, 3, 'entry_list', 3)
        self.assertTemplateUsed(
            response, 'zinnia/archives/2010/entry_archive_year.html')
        self.assertEqual(response.context['previous_year'], None)
        self.assertEqual(response.context['next_year'], None)
        response = self.client.get('/2011/')
        self.assertEqual(response.context['previous_year'], date(2010, 1, 1))
        self.assertEqual(response.context['next_year'], None)

    @override_settings(USE_TZ=True, TIME_ZONE='Europe/Paris')
    def test_zinnia_entry_archive_year_with_timezone(self):
        response = self.check_publishing_context(
            '/2010/', 2, 3, 'entry_list', 3)
        self.assertTemplateUsed(
            response, 'zinnia/archives/2010/entry_archive_year.html')
        self.assertEqual(response.context['previous_year'], None)
        self.assertEqual(response.context['next_year'], None)
        response = self.client.get('/2011/')
        self.assertEqual(response.context['previous_year'], date(2010, 1, 1))
        self.assertEqual(response.context['next_year'], None)

    @override_settings(USE_TZ=False)
    def test_zinnia_entry_archive_week_no_timezone(self):
        response = self.check_publishing_context(
            '/2010/week/00/', 1, 2, 'entry_list', 3)
        self.assertTemplateUsed(
            response, 'zinnia/archives/2010/week/00/entry_archive_week.html')
        # All days in a new year preceding the first Monday
        # are considered to be in week 0.
        self.assertEqual(response.context['week'], date(2009, 12, 28))
        self.assertEqual(response.context['week_end_day'], date(2010, 1, 3))
        self.assertEqual(response.context['previous_week'], None)
        self.assertEqual(response.context['next_week'], date(2010, 5, 31))
        self.assertEqual(list(response.context['date_list']),
                         [datetime(2010, 1, 1)])
        response = self.client.get('/2011/week/01/')
        self.assertEqual(response.context['week'], date(2011, 1, 3))
        self.assertEqual(response.context['week_end_day'], date(2011, 1, 9))
        self.assertEqual(response.context['previous_week'], date(2010, 5, 31))
        self.assertEqual(response.context['next_week'], None)
        self.assertEqual(list(response.context['date_list']), [])

    @override_settings(USE_TZ=True, TIME_ZONE='Europe/Paris')
    def test_zinnia_entry_archive_week_with_timezone(self):
        response = self.check_publishing_context(
            '/2010/week/00/', 1, 2, 'entry_list', 3)
        self.assertTemplateUsed(
            response, 'zinnia/archives/2010/week/00/entry_archive_week.html')
        # All days in a new year preceding the first Monday
        # are considered to be in week 0.
        self.assertEqual(response.context['week'], date(2009, 12, 28))
        self.assertEqual(response.context['week_end_day'], date(2010, 1, 3))
        self.assertEqual(response.context['previous_week'], None)
        self.assertEqual(response.context['next_week'], date(2010, 5, 31))
        self.assertEqual(response.context['date_list'][0].date(),
                         datetime(2010, 1, 2).date())
        response = self.client.get('/2011/week/01/')
        self.assertEqual(response.context['week'], date(2011, 1, 3))
        self.assertEqual(response.context['week_end_day'], date(2011, 1, 9))
        self.assertEqual(response.context['previous_week'], date(2010, 5, 31))
        self.assertEqual(response.context['next_week'], None)
        self.assertEqual(list(response.context['date_list']), [])

    @override_settings(USE_TZ=False)
    def test_zinnia_entry_archive_month_no_timezone(self):
        response = self.check_publishing_context(
            '/2010/01/', 1, 2, 'entry_list', 3)
        self.assertTemplateUsed(
            response, 'zinnia/archives/2010/month/01/entry_archive_month.html')
        self.assertEqual(response.context['previous_month'], None)
        self.assertEqual(response.context['next_month'], date(2010, 5, 1))
        self.assertEqual(list(response.context['date_list']),
                         [datetime(2010, 1, 1)])
        response = self.client.get('/2010/05/')
        self.assertEqual(response.context['previous_month'], date(2010, 1, 1))
        self.assertEqual(response.context['next_month'], None)
        self.assertEqual(list(response.context['date_list']),
                         [datetime(2010, 5, 31)])

    @override_settings(USE_TZ=True, TIME_ZONE='Europe/Paris')
    def test_zinnia_entry_archive_month_with_timezone(self):
        response = self.check_publishing_context(
            '/2010/01/', 1, 2, 'entry_list', 3)
        self.assertTemplateUsed(
            response, 'zinnia/archives/2010/month/01/entry_archive_month.html')
        self.assertEqual(response.context['previous_month'], None)
        self.assertEqual(response.context['next_month'], date(2010, 6, 1))
        self.assertEqual(response.context['date_list'][0].date(),
                         datetime(2010, 1, 2).date())
        response = self.client.get('/2010/06/')
        self.assertEqual(response.context['previous_month'], date(2010, 1, 1))
        self.assertEqual(response.context['next_month'], None)
        self.assertEqual(response.context['date_list'][0].date(),
                         datetime(2010, 6, 1).date())

    @override_settings(USE_TZ=False)
    def test_zinnia_entry_archive_day_no_timezone(self):
        response = self.check_publishing_context(
            '/2010/01/01/', 1, 2, 'entry_list', 2)
        self.assertTemplateUsed(
            response, 'zinnia/archives/2010/01/01/entry_archive_day.html')
        self.assertEqual(response.context['previous_month'], None)
        self.assertEqual(response.context['next_month'], date(2010, 5, 1))
        self.assertEqual(response.context['previous_day'], None)
        self.assertEqual(response.context['next_day'], date(2010, 5, 31))
        response = self.client.get('/2010/05/31/')
        self.assertEqual(response.context['previous_month'], date(2010, 1, 1))
        self.assertEqual(response.context['next_month'], None)
        self.assertEqual(response.context['previous_day'], date(2010, 1, 1))
        self.assertEqual(response.context['next_day'], None)

    @override_settings(USE_TZ=True, TIME_ZONE='Europe/Paris')
    def test_zinnia_entry_archive_day_with_timezone(self):
        response = self.check_publishing_context(
            '/2010/01/02/', 1, 2, 'entry_list', 2)
        self.assertTemplateUsed(
            response, 'zinnia/archives/2010/01/02/entry_archive_day.html')
        self.assertEqual(response.context['previous_month'], None)
        self.assertEqual(response.context['next_month'], date(2010, 6, 1))
        self.assertEqual(response.context['previous_day'], None)
        self.assertEqual(response.context['next_day'], date(2010, 6, 1))
        response = self.client.get('/2010/06/01/')
        self.assertEqual(response.context['previous_month'], date(2010, 1, 1))
        self.assertEqual(response.context['next_month'], None)
        self.assertEqual(response.context['previous_day'], date(2010, 1, 2))
        self.assertEqual(response.context['next_day'], None)

    @override_settings(USE_TZ=False)
    def test_zinnia_entry_archive_today_no_timezone(self):
        template_name_today = 'zinnia/archives/%s/entry_archive_today.html' % \
                              date.today().strftime('%Y/%m/%d')
        with self.assertNumQueries(2):
            response = self.client.get('/today/')
        self.assertTemplateUsed(response, template_name_today)
        self.assertEqual(response.context['day'], date.today())
        self.assertEqual(response.context['previous_month'], date(2010, 5, 1))
        self.assertEqual(response.context['next_month'], None)
        self.assertEqual(response.context['previous_day'], date(2010, 5, 31))
        self.assertEqual(response.context['next_day'], None)

    @override_settings(USE_TZ=True, TIME_ZONE='Europe/Paris')
    def test_zinnia_entry_archive_today_with_timezone(self):
        template_name_today = 'zinnia/archives/%s/entry_archive_today.html' % \
                              timezone.localtime(timezone.now()
                                                 ).strftime('%Y/%m/%d')
        with self.assertNumQueries(2):
            response = self.client.get('/today/')
        self.assertTemplateUsed(response, template_name_today)
        self.assertEqual(response.context['day'], timezone.localtime(
            timezone.now()).date())
        self.assertEqual(response.context['previous_month'], date(2010, 6, 1))
        self.assertEqual(response.context['next_month'], None)
        self.assertEqual(response.context['previous_day'], date(2010, 6, 1))
        self.assertEqual(response.context['next_day'], None)

    def test_zinnia_entry_shortlink(self):
        with self.assertNumQueries(1):
            response = self.client.get('/%s/' % base36(self.first_entry.pk))
        self.assertEqual(response.status_code, 301)
        self.assertEqual(
            response['Location'],
            self.first_entry.get_absolute_url())

    def test_zinnia_entry_shortlink_unpublished(self):
        """
        https://github.com/Fantomas42/django-blog-zinnia/pull/367
        """
        self.first_entry.sites.clear()
        with self.assertNumQueries(1):
            response = self.client.get('/%s/' % base36(self.first_entry.pk))
        self.assertEqual(response.status_code, 404)

    def test_zinnia_entry_detail(self):
        entry = self.first_entry
        with self.assertNumQueries(1):
            response = self.client.get(entry.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        entry.sites.clear()
        with self.assertNumQueries(1):
            response = self.client.get(entry.get_absolute_url())
        self.assertEqual(response.status_code, 404)
        entry.sites.add(self.site)

        entry.status = DRAFT
        entry.save()
        with self.assertNumQueries(2):
            response = self.client.get(entry.get_absolute_url())
        self.assertEqual(response.status_code, 404)
        entry.status = PUBLISHED

        entry.start_publication = datetime(2030, 1, 1, 12, 0)
        entry.save()
        with self.assertNumQueries(2):
            response = self.client.get(entry.get_absolute_url())
        self.assertEqual(response.status_code, 404)
        entry.start_publication = None

        entry.save()
        with self.assertNumQueries(1):
            response = self.client.get(entry.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    @override_settings(USE_TZ=False)
    def test_zinnia_entry_detail_no_timezone(self):
        entry = self.create_published_entry()
        entry.detail_template = 'entry_custom.html'
        entry.save()
        entry.sites.add(Site.objects.get_current())
        with self.assertNumQueries(1):
            response = self.client.get(entry.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'zinnia/archives/2010/01/01/my-test-entry_entry_custom.html')

    @override_settings(USE_TZ=True, TIME_ZONE='Europe/Paris')
    def test_zinnia_entry_detail_with_timezone(self):
        entry = self.create_published_entry()
        entry.detail_template = 'entry_custom.html'
        entry.save()
        with self.assertNumQueries(1):
            response = self.client.get(entry.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'zinnia/archives/2010/01/02/my-test-entry_entry_custom.html')

    @override_settings(USE_TZ=False)
    def test_zinnia_entry_detail_login(self):
        entry = self.create_published_entry()
        entry.login_required = True
        entry.save()
        with self.assertNumQueries(1):
            response = self.client.get(entry.get_absolute_url())
        self.assertTemplateUsed(response, 'zinnia/login.html')
        with self.assertNumQueries(3):
            response = self.client.post(entry.get_absolute_url(),
                                        {'username': 'admin',
                                         'password': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'zinnia/archives/2010/01/01/my-test-entry_entry_detail.html')

    @override_settings(USE_TZ=False)
    def test_zinnia_entry_detail_password(self):
        entry = self.create_published_entry()
        entry.password = 'password'
        entry.save()
        with self.assertNumQueries(1):
            response = self.client.get(entry.get_absolute_url())
        self.assertTemplateUsed(response, 'zinnia/password.html')
        self.assertEqual(response.context['error'], False)
        with self.assertNumQueries(1):
            response = self.client.post(entry.get_absolute_url(),
                                        {'entry_password': 'bad_password'})
        self.assertTemplateUsed(response, 'zinnia/password.html')
        self.assertEqual(response.context['error'], True)
        with self.assertNumQueries(1):
            response = self.client.post(entry.get_absolute_url(),
                                        {'entry_password': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'zinnia/archives/2010/01/01/my-test-entry_entry_detail.html')

    @override_settings(USE_TZ=False)
    def test_zinnia_entry_detail_login_password(self):
        user_logged_in.disconnect(update_last_login)
        entry = self.create_published_entry()
        entry.password = 'password'
        entry.login_required = True
        entry.save()
        with self.assertNumQueries(1):
            response = self.client.get(entry.get_absolute_url())
        self.assertTemplateUsed(response, 'zinnia/login.html')
        with self.assertNumQueries(3):
            response = self.client.post(entry.get_absolute_url(),
                                        {'username': 'admin',
                                         'password': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'zinnia/password.html')
        self.assertEqual(response.context['error'], False)
        with self.assertNumQueries(2):
            response = self.client.post(entry.get_absolute_url(),
                                        {'entry_password': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'zinnia/archives/2010/01/01/my-test-entry_entry_detail.html')
        user_logged_in.connect(update_last_login)

    def test_zinnia_entry_detail_preview(self):
        self.first_entry.status = DRAFT
        self.first_entry.save()
        url = self.first_entry.get_absolute_url()
        with self.assertNumQueries(2):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        Author.objects.create_superuser(
            'root', 'root@example.com', 'password')
        self.client.login(username='root', password='password')
        with self.assertNumQueries(2):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.client.login(username=self.author.username, password='password')
        with self.assertNumQueries(5):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_zinnia_entry_channel(self):
        self.check_publishing_context(
            '/channel-test/', 2, 3, 'entry_list', 1)

    def test_zinnia_category_list(self):
        category = Category.objects.create(
            title='New category', slug='new-category')
        self.check_publishing_context(
            '/categories/', 1,
            friendly_context='category_list',
            queries=0)
        self.first_entry.categories.add(category)
        self.check_publishing_context('/categories/', 2)

    def test_zinnia_category_detail(self):
        response = self.check_publishing_context(
            '/categories/tests/', 2, 3, 'entry_list', 2)
        self.assertTemplateUsed(
            response, 'zinnia/category/tests/entry_list.html')
        self.assertEqual(response.context['category'].slug, 'tests')

    def test_zinnia_category_detail_paginated(self):
        """Test case reproducing issue #42 on category
        detail view paginated"""
        for i in range(PAGINATION):
            params = {'title': 'My entry %i' % i,
                      'content': 'My content %i' % i,
                      'slug': 'my-entry-%i' % i,
                      'publication_date': datetime(2010, 1, 1),
                      'status': PUBLISHED}
            entry = Entry.objects.create(**params)
            entry.sites.add(self.site)
            entry.categories.add(self.category)
        response = self.client.get('/categories/tests/')
        self.assertEqual(len(response.context['object_list']), PAGINATION)
        response = self.client.get('/categories/tests/?page=2')
        self.assertEqual(len(response.context['object_list']), 2)
        response = self.client.get('/categories/tests/page/2/')
        self.assertEqual(len(response.context['object_list']), 2)
        self.assertEqual(response.context['category'].slug, 'tests')

    def test_zinnia_author_list(self):
        user = Author.objects.create(username='new-user',
                                     email='new_user@example.com')
        self.check_publishing_context(
            '/authors/', 1,
            friendly_context='author_list',
            queries=0)
        self.first_entry.authors.add(user)
        self.check_publishing_context('/authors/', 2)

    def test_zinnia_author_detail(self):
        response = self.check_publishing_context(
            '/authors/admin/', 2, 3, 'entry_list', 2)
        self.assertTemplateUsed(
            response, 'zinnia/author/admin/entry_list.html')
        self.assertEqual(response.context['author'].username, 'admin')

    def test_zinnia_author_detail_paginated(self):
        """Test case reproducing issue #207 on author
        detail view paginated"""
        for i in range(PAGINATION):
            params = {'title': 'My entry %i' % i,
                      'content': 'My content %i' % i,
                      'slug': 'my-entry-%i' % i,
                      'publication_date': datetime(2010, 1, 1),
                      'status': PUBLISHED}
            entry = Entry.objects.create(**params)
            entry.sites.add(self.site)
            entry.authors.add(self.author)
        response = self.client.get('/authors/admin/')
        self.assertEqual(len(response.context['object_list']), PAGINATION)
        response = self.client.get('/authors/admin/?page=2')
        self.assertEqual(len(response.context['object_list']), 2)
        response = self.client.get('/authors/admin/page/2/')
        self.assertEqual(len(response.context['object_list']), 2)
        self.assertEqual(response.context['author'].username, 'admin')

    def test_zinnia_tag_list(self):
        self.check_publishing_context(
            '/tags/', 1,
            friendly_context='tag_list',
            queries=1)
        self.first_entry.tags = 'tests, tag'
        self.first_entry.save()
        self.check_publishing_context('/tags/', 2)

    def test_zinnia_tag_detail(self):
        response = self.check_publishing_context(
            '/tags/tests/', 2, 3, 'entry_list', 2)
        self.assertTemplateUsed(
            response, 'zinnia/tag/tests/entry_list.html')
        self.assertEqual(response.context['tag'].name, 'tests')
        response = self.client.get('/tags/404/')
        self.assertEqual(response.status_code, 404)

    def test_zinnia_tag_detail_paginated(self):
        for i in range(PAGINATION):
            params = {'title': 'My entry %i' % i,
                      'content': 'My content %i' % i,
                      'slug': 'my-entry-%i' % i,
                      'tags': 'tests',
                      'publication_date': datetime(2010, 1, 1),
                      'status': PUBLISHED}
            entry = Entry.objects.create(**params)
            entry.sites.add(self.site)
        response = self.client.get('/tags/tests/')
        self.assertEqual(len(response.context['object_list']), PAGINATION)
        response = self.client.get('/tags/tests/?page=2')
        self.assertEqual(len(response.context['object_list']), 2)
        response = self.client.get('/tags/tests/page/2/')
        self.assertEqual(len(response.context['object_list']), 2)
        self.assertEqual(response.context['tag'].name, 'tests')

    def test_zinnia_entry_search(self):
        self.check_publishing_context(
            '/search/?pattern=test', 2, 3, 'entry_list', 1)
        response = self.client.get('/search/?pattern=ab')
        self.assertEqual(len(response.context['object_list']), 0)
        self.assertEqual(response.context['error'],
                         _('The pattern is too short'))
        response = self.client.get('/search/')
        self.assertEqual(len(response.context['object_list']), 0)
        self.assertEqual(response.context['error'],
                         _('No pattern to search found'))

    def test_zinnia_entry_random(self):
        response = self.client.get('/random/', follow=True)
        self.assertTrue(response.redirect_chain[0][0].startswith('/2010/'))
        self.assertEqual(response.redirect_chain[0][1], 302)

    def test_zinnia_sitemap(self):
        with self.assertNumQueries(0):
            response = self.client.get('/sitemap/')
        self.assertEqual(len(response.context['entries']), 2)
        self.assertEqual(len(response.context['categories']), 1)
        entry = self.create_published_entry()
        entry.categories.add(Category.objects.create(title='New category',
                                                     slug='new-category'))
        response = self.client.get('/sitemap/')
        self.assertEqual(len(response.context['entries']), 3)
        self.assertEqual(len(response.context['categories']), 2)

    def test_zinnia_trackback(self):
        # Clear the cache of user flagger to avoid error on MySQL
        get_user_flagger.cache_clear()
        # Disable spam-checkers
        import zinnia.spam_checker
        original_scb = zinnia.spam_checker.SPAM_CHECKER_BACKENDS
        zinnia.spam_checker.SPAM_CHECKER_BACKENDS = []

        response = self.client.post('/trackback/404/')
        trackback_url = '/trackback/%s/' % self.first_entry.pk
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.client.post(trackback_url).status_code, 301)
        self.first_entry.trackback_enabled = False
        self.first_entry.save()
        self.assertEqual(self.first_entry.trackback_count, 0)
        response = self.client.post(trackback_url,
                                    {'url': 'http://example.com'})
        self.assertEqual(response['Content-Type'], 'text/xml')
        self.assertEqual(response.context['error'],
                         'Trackback is not enabled for Test 1')
        self.first_entry.trackback_enabled = True
        self.first_entry.save()
        connect_discussion_signals()
        get_user_flagger()  # Memoize user flagger for stable query number
        if comments.get_comment_app_name() == comments.DEFAULT_COMMENTS_APP:
            # If we are using the default comment app,
            # we can count the database queries executed.
            with self.assertNumQueries(8):
                response = self.client.post(trackback_url,
                                            {'url': 'http://example.com'})
        else:
            response = self.client.post(trackback_url,
                                        {'url': 'http://example.com'})
        self.assertEqual(response['Content-Type'], 'text/xml')
        self.assertEqual('error' in response.context, False)
        disconnect_discussion_signals()
        entry = Entry.objects.get(pk=self.first_entry.pk)
        self.assertEqual(entry.trackback_count, 1)
        response = self.client.post(trackback_url,
                                    {'url': 'http://example.com'})
        self.assertEqual(response.context['error'],
                         'Trackback is already registered')
        zinnia.spam_checker.SPAM_CHECKER_BACKENDS = original_scb

    def test_zinnia_trackback_on_entry_without_author(self):
        # Clear the cache of user flagger to avoid error on MySQL
        get_user_flagger.cache_clear()
        # Disable spam-checkers
        import zinnia.spam_checker
        original_scb = zinnia.spam_checker.SPAM_CHECKER_BACKENDS
        zinnia.spam_checker.SPAM_CHECKER_BACKENDS = []

        self.first_entry.authors.clear()
        response = self.client.post('/trackback/%s/' % self.first_entry.pk,
                                    {'url': 'http://example.com'})
        self.assertEqual(response['Content-Type'], 'text/xml')
        self.assertEqual('error' in response.context, False)
        zinnia.spam_checker.SPAM_CHECKER_BACKENDS = original_scb

    def test_zinnia_trackback_spam_check(self):
        # Clear the cache of user flagger to avoid error on MySQL
        get_user_flagger.cache_clear()
        import zinnia.spam_checker
        original_scb = zinnia.spam_checker.SPAM_CHECKER_BACKENDS
        zinnia.spam_checker.SPAM_CHECKER_BACKENDS = (
            'zinnia.spam_checker.backends.all_is_spam',
        )
        response = self.client.post('/trackback/%s/' % self.first_entry.pk,
                                    {'url': 'http://example.com',
                                     'excerpt': 'Spam'})
        self.assertEqual(response['Content-Type'], 'text/xml')
        self.assertEqual(response.context['error'],
                         'Trackback considered like spam')
        zinnia.spam_checker.SPAM_CHECKER_BACKENDS = []
        response = self.client.post('/trackback/%s/' % self.first_entry.pk,
                                    {'url': 'http://example.com',
                                     'excerpt': 'Spam'})
        self.assertEqual(response['Content-Type'], 'text/xml')
        self.assertEqual('error' in response.context, False)
        zinnia.spam_checker.SPAM_CHECKER_BACKENDS = original_scb

    def test_capabilities(self):
        self.check_capabilities('/humans.txt', 'text/plain', 0)
        self.check_capabilities('/rsd.xml', 'application/rsd+xml', 0)
        self.check_capabilities('/wlwmanifest.xml',
                                'application/wlwmanifest+xml', 0)
        self.check_capabilities('/opensearch.xml',
                                'application/opensearchdescription+xml', 0)

    def test_comment_success(self):
        with self.assertNumQueries(0):
            response = self.client.get('/comments/success/')
        self.assertTemplateUsed(response, 'comments/zinnia/entry/posted.html')
        self.assertEqual(response.context['comment'], None)

        with self.assertNumQueries(1):
            response = self.client.get('/comments/success/?c=404')
        self.assertEqual(response.context['comment'], None)

        comment = comments.get_model().objects.create(
            submit_date=timezone.now(),
            comment='My Comment 1', content_object=self.category,
            site=self.site, is_public=False)
        success_url = '/comments/success/?c=%s' % comment.pk
        with self.assertNumQueries(1):
            response = self.client.get(success_url)
        self.assertEqual(response.context['comment'], comment)
        comment.is_public = True
        comment.save()
        with self.assertNumQueries(5):
            response = self.client.get(success_url, follow=True)
        self.assertEqual(
            response.redirect_chain[1],
            ('http://example.com/categories/tests/', 302))

    def test_comment_success_invalid_pk_issue_292(self):
        with self.assertNumQueries(0):
            response = self.client.get('/comments/success/?c=file.php')
        self.assertTemplateUsed(response, 'comments/zinnia/entry/posted.html')
        self.assertEqual(response.context['comment'], None)

    def test_quick_entry(self):
        Author.objects.create_superuser(
            'root', 'root@example.com', 'password')
        response = self.client.get('/quick-entry/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            '/accounts/login/?next=/quick-entry/')
        self.client.login(username='admin', password='password')
        response = self.client.get('/quick-entry/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            '/accounts/login/?next=/quick-entry/')
        self.client.logout()
        self.client.login(username='root', password='password')
        response = self.client.get('/quick-entry/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            '/admin/zinnia/entry/add/')
        response = self.client.post('/quick-entry/', {'content': 'test'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(url_equal(
            response['Location'],
            '/admin/zinnia/entry/add/'
            '?tags=&title=&sites=1&content='
            '%3Cp%3Etest%3C%2Fp%3E&authors=2&slug='))
        response = self.client.post('/quick-entry/',
                                    {'title': 'test', 'tags': 'test',
                                     'content': 'Test content',
                                     'save_draft': ''})
        entry = Entry.objects.get(title='test')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            entry.get_absolute_url())
        self.assertEqual(entry.status, DRAFT)
        self.assertEqual(entry.title, 'test')
        self.assertEqual(entry.tags, 'test')
        self.assertEqual(entry.content, '<p>Test content</p>')

    def test_quick_entry_non_ascii_title_issue_153(self):
        Author.objects.create_superuser(
            'root', 'root@example.com', 'password')
        self.client.login(username='root', password='password')
        response = self.client.post('/quick-entry/',
                                    {'title': 'тест', 'tags': 'test-2',
                                     'content': 'Test content',
                                     'save_draft': ''})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(url_equal(
            response['Location'],
            '/admin/zinnia/entry/add/'
            '?tags=test-2&title=%D1%82%D0%B5%D1%81%D1%82'
            '&sites=1&content=%3Cp%3ETest+content%3C%2Fp%3E'
            '&authors=2&slug='))

    def test_quick_entry_markup_language_issue_270(self):
        original_markup_language = quick_entry.MARKUP_LANGUAGE
        quick_entry.MARKUP_LANGUAGE = 'restructuredtext'
        Author.objects.create_superuser(
            'root', 'root@example.com', 'password')
        self.client.login(username='root', password='password')
        response = self.client.post('/quick-entry/',
                                    {'title': 'Test markup',
                                     'tags': 'test, markup',
                                     'content': 'Hello *World* !',
                                     'save_draft': ''})
        entry = Entry.objects.get(title='Test markup')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            entry.get_absolute_url())
        self.assertEqual(
            entry.content,
            'Hello *World* !')
        quick_entry.MARKUP_LANGUAGE = original_markup_language


@override_settings(
    ROOT_URLCONF='zinnia.tests.implementations.urls.custom_detail_views'
)
class CustomDetailViewsTestCase(ViewsBaseCase):
    """
    Tests with an alternate urls.py that modifies how author_detail,
    tags_detail and categories_detail views to be called with a custom
    template_name keyword argument and an extra_context.
    """

    def test_custom_category_detail(self):
        response = self.check_publishing_context('/categories/tests/', 2, 3)
        self.assertTemplateUsed(response, 'zinnia/entry_custom_list.html')
        self.assertEqual(response.context['category'].slug, 'tests')
        self.assertEqual(response.context['extra'], 'context')

    def test_custom_author_detail(self):
        response = self.check_publishing_context('/authors/admin/', 2, 3)
        self.assertTemplateUsed(response, 'zinnia/entry_custom_list.html')
        self.assertEqual(response.context['author'].username, 'admin')
        self.assertEqual(response.context['extra'], 'context')

    def test_custom_tag_detail(self):
        response = self.check_publishing_context('/tags/tests/', 2, 3)
        self.assertTemplateUsed(response, 'zinnia/entry_custom_list.html')
        self.assertEqual(response.context['tag'].name, 'tests')
        self.assertEqual(response.context['extra'], 'context')

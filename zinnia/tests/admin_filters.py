"""Test cases for Zinnia's admin filters"""
from __future__ import with_statement

from django.test import TestCase
from django.test import RequestFactory
from django.contrib.admin import site
from django.contrib.admin import ModelAdmin
from django.contrib.sites.models import Site
from django.utils.translation import activate
from django.utils.translation import deactivate
from django.contrib.admin.views.main import ChangeList

from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.models.category import Category
from zinnia.managers import PUBLISHED
from zinnia.admin.filters import AuthorListFilter
from zinnia.admin.filters import CategoryListFilter


class MiniEntryAuthorAdmin(ModelAdmin):
    list_filter = [AuthorListFilter]


class MiniEntryCategoryAdmin(ModelAdmin):
    list_filter = [CategoryListFilter]


class AuthorListFilterTestCase(TestCase):
    """Test case for AuthorListFilter"""
    urls = 'zinnia.tests.urls'

    def setUp(self):
        activate('en')
        self.request_factory = RequestFactory()

        self.site = Site.objects.get_current()
        self.authors = [
            Author.objects.create_user(username='webmaster',
                                       email='webmaster@example.com'),
            Author.objects.create_user(username='contributor',
                                       email='contributor@example.com'),
            Author.objects.create_user(username='reader',
                                       email='reader@example.com')]

        params = {'title': 'My entry 1',
                  'content': 'My content 1',
                  'status': PUBLISHED,
                  'slug': 'my-entry-1'}
        self.entry_1 = Entry.objects.create(**params)
        self.entry_1.authors.add(self.authors[0])
        self.entry_1.sites.add(self.site)

        params = {'title': 'My entry 2',
                  'content': 'My content 2',
                  'status': PUBLISHED,
                  'slug': 'my-entry-2'}
        self.entry_2 = Entry.objects.create(**params)
        self.entry_2.authors.add(*self.authors[:-1])
        self.entry_2.sites.add(self.site)

    def tearDown(self):
        deactivate()

    def get_changelist(self, request, model, modeladmin):
        return ChangeList(
            request, model, modeladmin.list_display,
            modeladmin.list_display_links, modeladmin.list_filter,
            modeladmin.date_hierarchy, modeladmin.search_fields,
            modeladmin.list_select_related, modeladmin.list_per_page,
            modeladmin.list_max_show_all, modeladmin.list_editable, modeladmin)

    def test_filter(self):
        modeladmin = MiniEntryAuthorAdmin(Entry, site)

        request = self.request_factory.get('/')
        changelist = self.get_changelist(request, Entry, modeladmin)
        queryset = changelist.get_query_set(request)
        self.assertEqual(queryset.count(), 2)

        request = self.request_factory.get('/', {'author': '2'})
        changelist = self.get_changelist(request, Entry, modeladmin)
        queryset = changelist.get_query_set(request)
        self.assertEqual(queryset.count(), 1)

        with self.assertNumQueries(1):
            filterspec = changelist.get_filters(request)[0][0]
            self.assertEquals(filterspec.title, 'published authors')
            self.assertEquals(filterspec.used_parameters, {'author': u'2'})
            self.assertEquals(filterspec.lookup_choices,
                              [('1', u'webmaster (2 entries)'),
                               ('2', u'contributor (1 entry)')])


class CategoryListFilterTestCase(TestCase):
    """Test case for CategoryListFilter"""
    urls = 'zinnia.tests.urls'

    def setUp(self):
        activate('en')
        self.request_factory = RequestFactory()

        self.site = Site.objects.get_current()
        self.categories = [
            Category.objects.create(title='Category 1',
                                    slug='cat-1'),
            Category.objects.create(title='Category 2',
                                    slug='cat-2'),
            Category.objects.create(title='Category 3',
                                    slug='cat-3')]

        params = {'title': 'My entry 1',
                  'content': 'My content 1',
                  'status': PUBLISHED,
                  'slug': 'my-entry-1'}
        self.entry_1 = Entry.objects.create(**params)
        self.entry_1.categories.add(self.categories[0])
        self.entry_1.sites.add(self.site)

        params = {'title': 'My entry 2',
                  'content': 'My content 2',
                  'status': PUBLISHED,
                  'slug': 'my-entry-2'}
        self.entry_2 = Entry.objects.create(**params)
        self.entry_2.categories.add(*self.categories[:-1])
        self.entry_2.sites.add(self.site)

    def tearDown(self):
        deactivate()

    def get_changelist(self, request, model, modeladmin):
        return ChangeList(
            request, model, modeladmin.list_display,
            modeladmin.list_display_links, modeladmin.list_filter,
            modeladmin.date_hierarchy, modeladmin.search_fields,
            modeladmin.list_select_related, modeladmin.list_per_page,
            modeladmin.list_max_show_all, modeladmin.list_editable, modeladmin)

    def test_filter(self):
        modeladmin = MiniEntryCategoryAdmin(Entry, site)

        request = self.request_factory.get('/')
        changelist = self.get_changelist(request, Entry, modeladmin)
        queryset = changelist.get_query_set(request)
        self.assertEqual(queryset.count(), 2)

        request = self.request_factory.get('/', {'category': '2'})
        changelist = self.get_changelist(request, Entry, modeladmin)
        queryset = changelist.get_query_set(request)
        self.assertEqual(queryset.count(), 1)

        with self.assertNumQueries(1):
            filterspec = changelist.get_filters(request)[0][0]
            self.assertEquals(filterspec.title, 'published categories')
            self.assertEquals(filterspec.used_parameters, {'category': u'2'})
            self.assertEquals(filterspec.lookup_choices,
                              [('1', u'Category 1 (2 entries)'),
                               ('2', u'Category 2 (1 entry)')])

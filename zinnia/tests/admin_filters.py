"""Test cases for Zinnia's admin filters"""
from __future__ import with_statement

from django.test import TestCase
from django.test import RequestFactory
from django.contrib.admin import site
from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.translation import deactivate
from django.contrib.admin.views.main import ChangeList

from zinnia.models import Entry
from zinnia.managers import PUBLISHED
from zinnia.admin.filters import AuthorListFilter


class MiniEntryAdmin(ModelAdmin):
    list_filter = [AuthorListFilter]


class AuthorListFilterTestCase(TestCase):
    """Test case for AuthorListFilter"""
    urls = 'zinnia.tests.urls'

    def setUp(self):
        self.request_factory = RequestFactory()

        self.site = Site.objects.get_current()
        self.authors = [
            User.objects.create_user(username='webmaster',
                                     email='webmaster@example.com'),
            User.objects.create_user(username='contributor',
                                     email='contributor@example.com'),
            User.objects.create_user(username='reader',
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

    def get_changelist(self, request, model, modeladmin):
        return ChangeList(
            request, model, modeladmin.list_display,
            modeladmin.list_display_links, modeladmin.list_filter,
            modeladmin.date_hierarchy, modeladmin.search_fields,
            modeladmin.list_select_related, modeladmin.list_per_page,
            modeladmin.list_max_show_all, modeladmin.list_editable, modeladmin)

    def test_filter(self):
        modeladmin = MiniEntryAdmin(Entry, site)

        request = self.request_factory.get('/')
        changelist = self.get_changelist(request, Entry, modeladmin)
        queryset = changelist.get_query_set(request)
        self.assertEqual(queryset.count(), 2)

        request = self.request_factory.get('/', {'author': '2'})
        changelist = self.get_changelist(request, Entry, modeladmin)
        queryset = changelist.get_query_set(request)
        self.assertEqual(queryset.count(), 1)

        deactivate()
        with self.assertNumQueries(1):
            filterspec = changelist.get_filters(request)[0][0]
            self.assertEquals(filterspec.title, 'author')
            self.assertEquals(filterspec.used_parameters, {'author': u'2'})
            self.assertEquals(filterspec.lookup_choices,
                              [('1', u'webmaster (2 entries)'),
                               ('2', u'contributor (1 entry)')])

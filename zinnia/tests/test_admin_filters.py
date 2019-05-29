"""Test cases for Zinnia's admin filters"""
from django.contrib.admin import ModelAdmin
from django.contrib.admin import site
from django.contrib.admin.views.main import ChangeList
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test import RequestFactory
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.translation import activate
from django.utils.translation import deactivate

from zinnia.admin.filters import AuthorListFilter
from zinnia.admin.filters import CategoryListFilter
from zinnia.managers import PUBLISHED
from zinnia.models.author import Author
from zinnia.models.category import Category
from zinnia.models.entry import Entry
from zinnia.signals import disconnect_entry_signals
from zinnia.tests.utils import skip_if_custom_user


class MiniEntryAuthorAdmin(ModelAdmin):
    list_filter = [AuthorListFilter]


class MiniEntryCategoryAdmin(ModelAdmin):
    list_filter = [CategoryListFilter]


@override_settings(
    ROOT_URLCONF='zinnia.tests.implementations.urls.default'
)
class BaseListFilterTestCase(TestCase):
    """Base TestCase for testing Filters"""

    def setUp(self):
        disconnect_entry_signals()
        activate('en')
        self.root = User.objects.create_superuser(
            'root', 'root@exemple.com', 'toor'
        )
        self.request_factory = RequestFactory()
        self.site = Site.objects.get_current()

        params = {'title': 'My entry 1',
                  'content': 'My content 1',
                  'status': PUBLISHED,
                  'slug': 'my-entry-1'}
        self.entry_1 = Entry.objects.create(**params)
        self.entry_1.sites.add(self.site)

        params = {'title': 'My entry 2',
                  'content': 'My content 2',
                  'status': PUBLISHED,
                  'slug': 'my-entry-2'}
        self.entry_2 = Entry.objects.create(**params)
        self.entry_2.sites.add(self.site)

        params = {'title': 'My entry draft',
                  'content': 'My content draft',
                  'slug': 'my-entry-draft'}
        self.entry_draft = Entry.objects.create(**params)
        self.entry_draft.sites.add(self.site)

    def tearDown(self):
        deactivate()

    def get_changelist(self, request, model, modeladmin):
        return ChangeList(
            request, model, modeladmin.list_display,
            modeladmin.list_display_links, modeladmin.list_filter,
            modeladmin.date_hierarchy, modeladmin.search_fields,
            modeladmin.list_select_related, modeladmin.list_per_page,
            modeladmin.list_max_show_all, modeladmin.list_editable,
            modeladmin, modeladmin.sortable_by)


@skip_if_custom_user
class AuthorListFilterTestCase(BaseListFilterTestCase):
    """Test case for AuthorListFilter"""

    def setUp(self):
        super(AuthorListFilterTestCase, self).setUp()
        self.authors = [
            Author.objects.create_user(username='webmaster',
                                       email='webmaster@example.com'),
            Author.objects.create_user(username='contributor',
                                       email='contributor@example.com'),
            Author.objects.create_user(username='reader',
                                       email='reader@example.com')]
        self.entry_1.authors.add(self.authors[0])
        self.entry_2.authors.add(*self.authors[:-1])
        self.entry_draft.authors.add(*self.authors)

    def test_filter(self):
        modeladmin = MiniEntryAuthorAdmin(Entry, site)

        request = self.request_factory.get('/')
        request.user = self.root
        changelist = self.get_changelist(request, Entry, modeladmin)
        queryset = changelist.get_queryset(request)
        self.assertEqual(queryset.count(), 3)

        request = self.request_factory.get('/', {'author': self.authors[1].pk})
        request.user = self.root
        changelist = self.get_changelist(request, Entry, modeladmin)
        queryset = changelist.get_queryset(request)
        self.assertEqual(queryset.count(), 2)

        with self.assertNumQueries(1):
            filterspec = changelist.get_filters(request)[0][0]
            self.assertEqual(filterspec.title, 'published authors')
            self.assertEqual(filterspec.used_parameters,
                             {'author': str(self.authors[1].pk)})
            self.assertEqual(filterspec.lookup_choices,
                             [(str(self.authors[0].pk),
                               'webmaster (2 entries)'),
                              (str(self.authors[1].pk),
                               'contributor (1 entry)')])


@skip_if_custom_user
class CategoryListFilterTestCase(BaseListFilterTestCase):
    """Test case for CategoryListFilter"""

    def setUp(self):
        super(CategoryListFilterTestCase, self).setUp()
        self.categories = [
            Category.objects.create(title='Category 1',
                                    slug='cat-1'),
            Category.objects.create(title='Category 2',
                                    slug='cat-2'),
            Category.objects.create(title='Category 3',
                                    slug='cat-3')]

        self.entry_1.categories.add(self.categories[0])
        self.entry_2.categories.add(*self.categories[:-1])
        self.entry_draft.categories.add(*self.categories)

    def test_filter(self):
        modeladmin = MiniEntryCategoryAdmin(Entry, site)

        request = self.request_factory.get('/')
        request.user = self.root
        changelist = self.get_changelist(request, Entry, modeladmin)
        queryset = changelist.get_queryset(request)
        self.assertEqual(queryset.count(), 3)

        request = self.request_factory.get(
            '/', {'category': str(self.categories[1].pk)}
        )
        request.user = self.root
        changelist = self.get_changelist(request, Entry, modeladmin)
        queryset = changelist.get_queryset(request)
        self.assertEqual(queryset.count(), 2)

        with self.assertNumQueries(1):
            filterspec = changelist.get_filters(request)[0][0]
            self.assertEqual(filterspec.title, 'published categories')
            self.assertEqual(filterspec.used_parameters,
                             {'category': str(self.categories[1].pk)})
            self.assertEqual(filterspec.lookup_choices,
                             [(str(self.categories[0].pk),
                               'Category 1 (2 entries)'),
                              (str(self.categories[1].pk),
                               'Category 2 (1 entry)')])

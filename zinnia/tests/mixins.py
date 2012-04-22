"""Test cases for Zinnia's mixins"""
from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured

from zinnia.views.mixins.mimetypes import MimeTypeMixin
from zinnia.views.mixins.callable_queryset import CallableQuerysetMixin
from zinnia.views.mixins.templates import EntryQuerysetTemplateResponseMixin
from zinnia.views.mixins.templates import \
     EntryQuerysetArchiveTemplateResponseMixin


class MixinTestCase(TestCase):
    """Test cases for zinnia.views.mixins"""

    def test_callable_queryset_mixin(self):
        instance = CallableQuerysetMixin()
        self.assertRaises(ImproperlyConfigured,
                          instance.get_queryset)

        def qs():
            return []

        instance.queryset = qs
        self.assertEquals(instance.get_queryset(),
                          [])

    def test_mimetype_mixin(self):
        instance = MimeTypeMixin()
        self.assertRaises(ImproperlyConfigured,
                          instance.get_mimetype)

        instance.mimetype = 'mimetype'
        self.assertEquals(instance.get_mimetype(),
                          'mimetype')

    def test_entry_queryset_template_response_mixin(self):
        instance = EntryQuerysetTemplateResponseMixin()
        self.assertRaises(ImproperlyConfigured,
                          instance.get_model_type)
        self.assertRaises(ImproperlyConfigured,
                          instance.get_model_name)
        instance.model_type = 'model'
        instance.model_name = 'name'
        self.assertEquals(instance.get_model_type(),
                          'model')
        self.assertEquals(instance.get_model_name(),
                          'name')
        self.assertEquals(instance.get_template_names(),
                          ['zinnia/model/name/entry_list.html',
                           'zinnia/model/name_entry_list.html',
                           'zinnia/model/entry_list.html',
                           'zinnia/entry_list.html'])
        instance.template_name = 'zinnia/entry_search.html'
        self.assertEquals(instance.get_template_names(),
                          ['zinnia/entry_search.html',
                           'zinnia/model/name/entry_list.html',
                           'zinnia/model/name_entry_list.html',
                           'zinnia/model/entry_list.html',
                           'zinnia/entry_list.html'])

    def test_entry_queryset_archive_template_response_mixin(self):
        get_year = lambda: 2012
        get_week = lambda: 16
        get_month = lambda: '04'
        get_day = lambda: 21
        instance = EntryQuerysetArchiveTemplateResponseMixin()
        self.assertEquals(
            instance.get_template_names(),
            ['zinnia/archives/entry_archive.html',
             'zinnia/entry_archive.html'])
        instance.get_year = get_year
        self.assertEquals(
            instance.get_template_names(),
            ['zinnia/archives/2012/entry_archive.html',
             'zinnia/archives/entry_archive.html',
             'zinnia/entry_archive.html'])
        instance.get_week = get_week
        self.assertEquals(
            instance.get_template_names(),
            ['zinnia/archives/2012/week/16/entry_archive.html',
             'zinnia/archives/week/16/entry_archive.html',
             'zinnia/archives/2012/entry_archive.html',
             'zinnia/archives/entry_archive.html',
             'zinnia/entry_archive.html'])
        instance.get_month = get_month
        self.assertEquals(
            instance.get_template_names(),
            ['zinnia/archives/2012/month/04/entry_archive.html',
             'zinnia/archives/month/04/entry_archive.html',
             'zinnia/archives/2012/week/16/entry_archive.html',
             'zinnia/archives/week/16/entry_archive.html',
             'zinnia/archives/2012/entry_archive.html',
             'zinnia/archives/entry_archive.html',
             'zinnia/entry_archive.html'])
        instance.get_day = get_day
        self.assertEquals(
            instance.get_template_names(),
            ['zinnia/archives/2012/04/21/entry_archive.html',
             'zinnia/archives/month/04/day/21/entry_archive.html',
             'zinnia/archives/2012/day/21/entry_archive.html',
             'zinnia/archives/day/21/entry_archive.html',
             'zinnia/archives/2012/month/04/entry_archive.html',
             'zinnia/archives/month/04/entry_archive.html',
             'zinnia/archives/2012/week/16/entry_archive.html',
             'zinnia/archives/week/16/entry_archive.html',
             'zinnia/archives/2012/entry_archive.html',
             'zinnia/archives/entry_archive.html',
             'zinnia/entry_archive.html'])

        instance.template_name = 'zinnia/entry_search.html'
        self.assertEquals(
            instance.get_template_names(),
            ['zinnia/entry_search.html',
             'zinnia/archives/2012/04/21/entry_archive.html',
             'zinnia/archives/month/04/day/21/entry_archive.html',
             'zinnia/archives/2012/day/21/entry_archive.html',
             'zinnia/archives/day/21/entry_archive.html',
             'zinnia/archives/2012/month/04/entry_archive.html',
             'zinnia/archives/month/04/entry_archive.html',
             'zinnia/archives/2012/week/16/entry_archive.html',
             'zinnia/archives/week/16/entry_archive.html',
             'zinnia/archives/2012/entry_archive.html',
             'zinnia/archives/entry_archive.html',
             'zinnia/entry_archive.html'])

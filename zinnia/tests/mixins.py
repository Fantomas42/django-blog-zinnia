"""Test cases for Zinnia's mixins"""
from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured

from zinnia.views.mixins import MimeTypeMixin
from zinnia.views.mixins import CallableQuerysetMixin
from zinnia.views.mixins import EntryQuerysetTemplateResponseMixin


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

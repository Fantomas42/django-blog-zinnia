"""Test cases for Zinnia's admin forms"""
from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper

from zinnia.models import Category
from zinnia.admin.forms import EntryAdminForm
from zinnia.admin.forms import CategoryAdminForm


class EntryAdminFormTestCase(TestCase):

    def test_categories_has_related_widget(self):
        form = EntryAdminForm()
        self.assertTrue(
            isinstance(form.fields['categories'].widget,
                       RelatedFieldWidgetWrapper))

    def test_initial_sites(self):
        form = EntryAdminForm()
        self.assertEqual(
            len(form.fields['sites'].initial), 1)


class CategoryAdminFormTestCase(TestCase):

    def test_parent_has_related_widget(self):
        form = CategoryAdminForm()
        self.assertTrue(
            isinstance(form.fields['parent'].widget,
                       RelatedFieldWidgetWrapper))

    def test_clean_parent(self):
        category = Category.objects.create(
            title='Category 1', slug='cat-1')
        datas = {'parent': category.pk,
                 'title': category.title,
                 'slug': category.slug}
        form = CategoryAdminForm(datas, instance=category)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors['parent']), 1)

        subcategory = Category.objects.create(
            title='Category 2', slug='cat-2')
        self.assertEqual(subcategory.parent, None)

        datas = {'parent': category.pk,
                 'title': subcategory.title,
                 'slug': subcategory.slug}
        form = CategoryAdminForm(datas, instance=subcategory)
        self.assertTrue(form.is_valid())

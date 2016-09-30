"""Test cases for Zinnia's admin forms"""
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.test import TestCase

from zinnia.admin.forms import CategoryAdminForm
from zinnia.admin.forms import EntryAdminForm
from zinnia.models import Category


class EntryAdminFormTestCase(TestCase):

    def test_categories_has_related_widget(self):
        form = EntryAdminForm()
        self.assertTrue(
            isinstance(form.fields['categories'].widget,
                       RelatedFieldWidgetWrapper))


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

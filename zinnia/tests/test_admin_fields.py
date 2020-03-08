"""Test cases for Zinnia's admin fields"""
from django.test import TestCase
from django.utils.encoding import smart_str

from zinnia.admin.fields import MPTTModelChoiceIterator
from zinnia.admin.fields import MPTTModelMultipleChoiceField
from zinnia.models import Category


class MPTTModelChoiceIteratorTestCase(TestCase):

    def test_choice(self):
        category_1 = Category.objects.create(
            title='Category 1', slug='cat-1')
        category_2 = Category.objects.create(
            title='Category 2', slug='cat-2',
            parent=category_1)

        class FakeField(object):
            queryset = Category.objects.all()

            def prepare_value(self, value):
                return value.pk

            def label_from_instance(self, obj):
                return smart_str(obj)

        field = FakeField()
        iterator = MPTTModelChoiceIterator(field)

        self.assertEqual(iterator.choice(category_1),
                         (category_1.pk, 'Category 1', (1, 1)))
        self.assertEqual(iterator.choice(category_2),
                         (category_2.pk, 'Category 2', (1, 2)))


class MPTTModelMultipleChoiceFieldTestCase(TestCase):

    def setUp(self):
        self.category_1 = Category.objects.create(
            title='Category 1', slug='cat-1')
        self.category_2 = Category.objects.create(
            title='Category 2', slug='cat-2',
            parent=self.category_1)

    def test_label_from_instance(self):
        queryset = Category.objects.all()

        field = MPTTModelMultipleChoiceField(
            queryset=queryset)
        self.assertEqual(field.label_from_instance(self.category_1),
                         'Category 1')
        self.assertEqual(field.label_from_instance(self.category_2),
                         '|-- Category 2')
        field = MPTTModelMultipleChoiceField(
            level_indicator='-->', queryset=queryset)
        self.assertEqual(field.label_from_instance(self.category_2),
                         '--> Category 2')

    def test_get_choices(self):
        queryset = Category.objects.all()

        field = MPTTModelMultipleChoiceField(
            queryset=queryset)
        self.assertEqual(list(field.choices),
                         [(self.category_1.pk, 'Category 1', (1, 1)),
                          (self.category_2.pk, '|-- Category 2', (1, 2))])

        field = MPTTModelMultipleChoiceField(
            level_indicator='-->', queryset=queryset)
        self.assertEqual(list(field.choices),
                         [(self.category_1.pk, 'Category 1', (1, 1)),
                          (self.category_2.pk, '--> Category 2', (1, 2))])

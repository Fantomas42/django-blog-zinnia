"""Test cases for Zinnia's Category"""
from __future__ import with_statement

from django.test import TestCase
from django.contrib.sites.models import Site

from zinnia.models.entry import Entry
from zinnia.models.category import Category
from zinnia.managers import PUBLISHED


class CategoryTestCase(TestCase):

    def setUp(self):
        self.site = Site.objects.get_current()
        self.categories = [Category.objects.create(title='Category 1',
                                                   slug='category-1'),
                           Category.objects.create(title='Category 2',
                                                   slug='category-2')]
        params = {'title': 'My entry',
                  'content': 'My content',
                  'tags': 'zinnia, test',
                  'slug': 'my-entry'}

        self.entry = Entry.objects.create(**params)
        self.entry.categories.add(*self.categories)
        self.entry.sites.add(self.site)

    def test_entries_published(self):
        category = self.categories[0]
        self.assertEqual(category.entries_published().count(), 0)
        self.entry.status = PUBLISHED
        self.entry.save()
        self.assertEqual(category.entries_published().count(), 1)

        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'tags': 'zinnia, test',
                  'status': PUBLISHED,
                  'slug': 'my-second-entry'}

        new_entry = Entry.objects.create(**params)
        new_entry.sites.add(self.site)
        new_entry.categories.add(self.categories[0])

        self.assertEqual(self.categories[0].entries_published().count(), 2)
        self.assertEqual(self.categories[1].entries_published().count(), 1)

    def test_entries_tree_path(self):
        self.categories.extend([Category.objects.create(title='Category 3',
                                                        slug='category-3'),
                                Category.objects.create(title='Category 4',
                                                        slug='category-4')])
        with self.assertNumQueries(0):
            self.assertEqual(self.categories[0].tree_path, 'category-1')
            self.assertEqual(self.categories[1].tree_path, 'category-2')

        self.categories[1].parent = self.categories[0]
        self.categories[1].save()
        self.categories[1].parent = self.categories[0]
        self.categories[1].save()
        self.categories[2].parent = self.categories[1]
        self.categories[2].save()
        self.categories[3].parent = self.categories[2]
        self.categories[3].save()

        category = Category.objects.get(slug='category-2')
        with self.assertNumQueries(1):
            self.assertEqual(category.tree_path, 'category-1/category-2')

        category = Category.objects.get(slug='category-4')
        with self.assertNumQueries(1):
            self.assertEqual(category.tree_path,
                             'category-1/category-2/category-3/category-4')

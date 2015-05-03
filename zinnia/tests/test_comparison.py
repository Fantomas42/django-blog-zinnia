"""Test cases for Zinnia's comparison"""
from django.test import TestCase

from zinnia.models.entry import Entry
from zinnia.comparison import pearson_score
from zinnia.comparison import VectorBuilder
from zinnia.comparison import ClusteredModel
from zinnia.signals import disconnect_entry_signals


class ComparisonTestCase(TestCase):
    """Test cases for comparison tools"""

    def setUp(self):
        disconnect_entry_signals()

    def test_pearson_score(self):
        self.assertEqual(pearson_score([42], [42]), 1.0)
        self.assertEqual(pearson_score([0, 1, 2], [0, 1, 2]), 1.0)
        self.assertEqual(pearson_score([0, 1, 3], [0, 1, 2]),
                         0.9819805060619656)
        self.assertEqual(pearson_score([0, 1, 2], [0, 1, 3]),
                         0.9819805060619656)

    def test_clustered_model(self):
        params = {'title': 'My entry 1', 'content': 'My content 1',
                  'tags': 'zinnia, test', 'slug': 'my-entry-1'}
        entry_1 = Entry.objects.create(**params)
        params = {'title': 'My entry 2', 'content': 'My content 2',
                  'tags': 'zinnia, test', 'slug': 'my-entry-2'}
        entry_2 = Entry.objects.create(**params)
        cm = ClusteredModel(Entry.objects.all(), ['id'])
        self.assertEqual(sorted(cm.dataset().values()),
                         sorted([str(entry_1.pk), str(entry_2.pk)]))
        cm = ClusteredModel(Entry.objects.all(),
                            ['title', 'excerpt', 'content'])
        self.assertEqual(sorted(cm.dataset().values()),
                         sorted([' entry 1   content 1',
                                 ' entry 2   content 2']))

    def test_vector_builder(self):
        vectors = VectorBuilder(Entry.objects.all(),
                                ['title', 'excerpt', 'content'])
        self.assertEqual(vectors.dataset, {})
        self.assertEqual(vectors.columns, [])
        params = {'title': 'My entry 1', 'content':
                  'This is my first content',
                  'tags': 'zinnia, test', 'slug': 'my-entry-1'}
        Entry.objects.create(**params)
        params = {'title': 'My entry 2', 'content':
                  'My second entry',
                  'tags': 'zinnia, test', 'slug': 'my-entry-2'}
        Entry.objects.create(**params)
        self.assertEqual(vectors._dataset, {})
        self.assertEqual(vectors._columns, [])
        self.assertEqual(sorted(vectors.columns), sorted(
            ['1', '2', 'content']))
        self.assertEqual(sorted([sorted(row) for row in
                                 vectors._dataset.values()]),
                         sorted([sorted([0, 0, 1]),
                                 sorted([0, 1, 1])]))

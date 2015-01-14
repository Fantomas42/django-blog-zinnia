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
        cm = ClusteredModel(Entry.objects.all())
        self.assertEqual(list(cm.dataset().values()),
                         [str(entry_1.pk), str(entry_2.pk)])
        cm = ClusteredModel(Entry.objects.all(),
                            ['title', 'excerpt', 'content'])
        self.assertEqual(list(cm.dataset().values()),
                         ['My entry 1  My content 1',
                          'My entry 2  My content 2'])

    def test_vector_builder(self):
        vectors = VectorBuilder(Entry.objects.all(),
                                ['title', 'excerpt', 'content'])
        params = {'title': 'My entry 1', 'content':
                  'This is my first content',
                  'tags': 'zinnia, test', 'slug': 'my-entry-1'}
        Entry.objects.create(**params)
        params = {'title': 'My entry 2', 'content':
                  'My second entry',
                  'tags': 'zinnia, test', 'slug': 'my-entry-2'}
        Entry.objects.create(**params)
        columns, dataset = vectors()
        self.assertEqual(sorted(columns), sorted(
            ['content', 'this', 'is', '1',
             'second', '2', 'first']))
        self.assertEqual(sorted([sorted(row) for row in dataset.values()]),
                         sorted([sorted([1, 1, 1, 1, 0, 0, 1]),
                                 sorted([0, 0, 0, 0, 1, 1, 0])]))

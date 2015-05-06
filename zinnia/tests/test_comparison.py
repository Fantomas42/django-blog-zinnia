"""Test cases for Zinnia's comparison"""
from django.test import TestCase

from zinnia.models.entry import Entry
from zinnia.comparison import pearson_score
from zinnia.comparison import compute_related
from zinnia.comparison import VectorBuilder
from zinnia.comparison import ClusteredModel
from zinnia.comparison import get_comparison_cache
from zinnia.signals import disconnect_entry_signals


class ComparisonTestCase(TestCase):
    """Test cases for comparison tools"""

    def setUp(self):
        disconnect_entry_signals()

    def test_clustered_model(self):
        params = {'title': 'My entry 1', 'content': 'My content 1.',
                  'tags': 'zinnia, test', 'slug': 'my-entry-1'}
        entry_1 = Entry.objects.create(**params)
        params = {'title': 'My entry 2', 'content': 'My content 2.',
                  'tags': 'zinnia, test', 'slug': 'my-entry-2'}
        entry_2 = Entry.objects.create(**params)
        cm = ClusteredModel(Entry.objects.all(), ['id'])
        self.assertEqual(sorted(cm.dataset().values()),
                         sorted([str(entry_1.pk), str(entry_2.pk)]))
        cm = ClusteredModel(Entry.objects.all(),
                            ['title', 'content', 'tags'])
        self.assertEqual(sorted(cm.dataset().values()),
                         sorted([' entry 1  content 1 zinnia test',
                                 ' entry 2  content 2 zinnia test']))

    def test_vector_builder(self):
        cache = get_comparison_cache()
        cache.delete('vectors')
        vectors = VectorBuilder(Entry.objects.all(),
                                ['title', 'excerpt', 'content'])
        self.assertEqual(vectors.dataset, {})
        self.assertEqual(vectors.columns, [])
        params = {'title': 'My entry 1', 'content':
                  'This is my first content',
                  'slug': 'my-entry-1'}
        e1 = Entry.objects.create(**params)
        params = {'title': 'My entry 2', 'content':
                  'My second entry',
                  'slug': 'my-entry-2'}
        e2 = Entry.objects.create(**params)
        self.assertEqual(vectors.dataset, {})
        self.assertEqual(vectors.columns, [])
        cache.delete('vectors')
        self.assertEqual(sorted(vectors.columns), sorted(
            ['1', '2', 'content', 'entry']))
        self.assertEqual(sorted(vectors.dataset[e1.pk]), [0, 1, 1, 1])
        self.assertEqual(sorted(vectors.dataset[e2.pk]), [0, 0, 1, 2])

    def test_pearson_score(self):
        self.assertRaises(ZeroDivisionError, pearson_score,
                          [42], [42])
        self.assertRaises(ZeroDivisionError, pearson_score,
                          [2, 2, 2], [1, 1, 1])
        self.assertEqual(pearson_score([0, 1, 2], [0, 1, 2]), 1.0)
        self.assertEqual(pearson_score([0, 1, 3], [0, 1, 2]),
                         0.9819805060619656)
        self.assertEqual(pearson_score([0, 1, 2], [0, 1, 3]),
                         0.9819805060619656)
        self.assertEqual(pearson_score([2, 0, 0, 0], [0, 1, 1, 1]),
                         -1)

    def test_compute_related(self):
        dataset = {1: [1, 2, 3],
                   2: [1, 5, 7],
                   3: [2, 8, 3],
                   4: [1, 8, 3],
                   5: [7, 3, 5]}
        self.assertEqual(compute_related('error', dataset), [])
        self.assertEqual(compute_related(1, dataset), [2, 4, 3, 5])
        self.assertEqual(compute_related(2, dataset), [1, 4, 3, 5])
        self.assertEqual(compute_related(3, dataset), [4, 2, 1, 5])
        self.assertEqual(compute_related(4, dataset), [3, 2, 1, 5])
        dataset[2] = [0, 0, 0]
        self.assertEqual(compute_related(1, dataset), [4, 3, 5])

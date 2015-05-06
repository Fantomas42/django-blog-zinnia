"""Test cases for Zinnia's comparison"""
from django.test import TestCase

from zinnia.models.entry import Entry
from zinnia.comparison import pearson_score
from zinnia.comparison import ModelVectorBuilder
from zinnia.signals import disconnect_entry_signals


class ComparisonTestCase(TestCase):
    """Test cases for comparison tools"""

    def setUp(self):
        disconnect_entry_signals()

    def test_raw_dataset(self):
        params = {'title': 'My entry 1', 'content': 'My content 1.',
                  'tags': 'zinnia, test', 'slug': 'my-entry-1'}
        entry_1 = Entry.objects.create(**params)
        params = {'title': 'My entry 2', 'content': 'My content 2.',
                  'tags': 'zinnia, test', 'slug': 'my-entry-2'}
        entry_2 = Entry.objects.create(**params)
        v = ModelVectorBuilder(queryset=Entry.objects.all(), fields=['id'])
        self.assertEqual(sorted(v.raw_dataset.values()),
                         sorted([str(entry_1.pk), str(entry_2.pk)]))
        v = ModelVectorBuilder(queryset=Entry.objects.all(),
                               fields=['title', 'content', 'tags'])
        self.assertEqual(sorted(v.raw_dataset.values()),
                         sorted(['entry 1  content 1 zinnia test',
                                 'entry 2  content 2 zinnia test']))
        v = ModelVectorBuilder(queryset=Entry.objects.all().order_by('-pk'),
                               fields=['title'], limit=1)
        self.assertEqual(v.raw_dataset.values(), ['entry 2'])

    def test_column_dataset(self):
        vectors = ModelVectorBuilder(queryset=Entry.objects.all(),
                                     fields=['title', 'excerpt', 'content'])
        self.assertEqual(vectors.dataset, {})
        self.assertEqual(vectors.columns, [])
        params = {'title': 'My entry 1', 'content':
                  'This is my first content 1',
                  'slug': 'my-entry-1'}
        e1 = Entry.objects.create(**params)
        params = {'title': 'My entry 2', 'content':
                  'My second content entry 2',
                  'slug': 'my-entry-2'}
        e2 = Entry.objects.create(**params)
        vectors = ModelVectorBuilder(queryset=Entry.objects.all(),
                                     fields=['title', 'excerpt', 'content'])
        self.assertEqual(vectors.columns, ['1', '2', 'content', 'entry'])
        self.assertEqual(vectors.dataset[e1.pk], [2, 0, 1, 1])
        self.assertEqual(vectors.dataset[e2.pk], [0, 2, 1, 2])

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
        class VirtualVectorBuilder(ModelVectorBuilder):
            dataset = {1: [1, 2, 3],
                       2: [1, 5, 7],
                       3: [2, 8, 3],
                       4: [1, 8, 3],
                       5: [7, 3, 5]}

        v = VirtualVectorBuilder()
        self.assertEqual(v.compute_related('error'), [])
        self.assertEqual(v.compute_related(1), [2, 4, 3, 5])
        self.assertEqual(v.compute_related(2), [1, 4, 3, 5])
        self.assertEqual(v.compute_related(3), [4, 2, 1, 5])
        self.assertEqual(v.compute_related(4), [3, 2, 1, 5])
        v.dataset[2] = [0, 0, 0]
        self.assertEqual(v.compute_related(1), [4, 3, 5])

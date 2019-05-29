"""Test cases for Zinnia's comparison"""
from django.test import TestCase

from mots_vides import stop_words

from zinnia import comparison
from zinnia.comparison import CachedModelVectorBuilder
from zinnia.comparison import ModelVectorBuilder
from zinnia.comparison import pearson_score
from zinnia.models.entry import Entry
from zinnia.signals import disconnect_entry_signals


class ComparisonTestCase(TestCase):
    """Test cases for comparison tools"""

    def setUp(self):
        english_stop_words = stop_words('english')
        self.original_stop_words = comparison.STOP_WORDS
        comparison.STOP_WORDS = english_stop_words
        disconnect_entry_signals()

    def tearDown(self):
        comparison.STOP_WORDS = self.original_stop_words

    def test_raw_dataset(self):
        params = {'title': 'My entry 1', 'content': 'My content 1.',
                  'tags': 'zinnia, test', 'slug': 'my-entry-1'}
        Entry.objects.create(**params)
        params = {'title': 'My entry 2', 'content': 'My content 2.',
                  'tags': 'zinnia, test', 'slug': 'my-entry-2'}
        Entry.objects.create(**params)
        v = ModelVectorBuilder(queryset=Entry.objects.all(), fields=['title'])
        with self.assertNumQueries(1):
            self.assertEqual(len(v.raw_dataset), 2)
            self.assertEqual(sorted(v.raw_dataset.values()),
                             [['entry'], ['entry']])
        v = ModelVectorBuilder(queryset=Entry.objects.all(),
                               fields=['title', 'content', 'tags'])
        self.assertEqual(sorted(v.raw_dataset.values()),
                         [['entry', 'content', 'zinnia', 'test'],
                          ['entry', 'content', 'zinnia', 'test']])
        v = ModelVectorBuilder(queryset=Entry.objects.all().order_by('-pk'),
                               fields=['title'], limit=1)
        self.assertEqual(list(v.raw_dataset.values()), [['entry']])

    def test_column_dataset(self):
        vectors = ModelVectorBuilder(queryset=Entry.objects.all(),
                                     fields=['title', 'excerpt', 'content'])
        with self.assertNumQueries(1):
            self.assertEqual(vectors.dataset, {})
            self.assertEqual(vectors.columns, [])
        params = {'title': 'My entry 1 (01)', 'content':
                  'This is my first content 1 (01)',
                  'slug': 'my-entry-1'}
        e1 = Entry.objects.create(**params)
        params = {'title': 'My entry 2 (02)', 'content':
                  'My second content entry 2 (02)',
                  'slug': 'my-entry-2'}
        e2 = Entry.objects.create(**params)
        vectors = ModelVectorBuilder(queryset=Entry.objects.all(),
                                     fields=['title', 'excerpt', 'content'])
        self.assertEqual(vectors.columns, ['01', '02', 'content', 'entry'])
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
        self.assertEqual(v.compute_related(1),
                         [(2, 0.9819805060619659),
                          (4, 0.2773500981126146),
                          (3, 0.15554275420956382),
                          (5, -0.5)])
        self.assertEqual(v.compute_related(2),
                         [(1, 0.9819805060619659),
                          (4, 0.4539206495016019),
                          (3, 0.33942211665106525),
                          (5, -0.6546536707079772)])
        self.assertEqual(v.compute_related(3),
                         [(4, 0.9922153572367627),
                          (2, 0.33942211665106525),
                          (1, 0.15554275420956382),
                          (5, -0.9332565252573828)])
        self.assertEqual(v.compute_related(4),
                         [(3, 0.9922153572367627),
                          (2, 0.4539206495016019),
                          (1, 0.2773500981126146),
                          (5, -0.9707253433941511)])
        v.dataset[2] = [0, 0, 0]
        self.assertEqual(v.compute_related(1),
                         [(4, 0.2773500981126146),
                          (3, 0.15554275420956382),
                          (5, -0.5)])

    def test_get_related(self):
        params = {'title': 'My entry 01', 'content':
                  'This is my first content 01',
                  'slug': 'my-entry-1'}
        e1 = Entry.objects.create(**params)
        vectors = ModelVectorBuilder(queryset=Entry.objects.all(),
                                     fields=['title', 'content'])
        with self.assertNumQueries(1):
            self.assertEqual(vectors.get_related(e1, 10), [])

        params = {'title': 'My entry 02', 'content':
                  'My second content entry 02',
                  'slug': 'my-entry-2'}
        e2 = Entry.objects.create(**params)
        with self.assertNumQueries(0):
            self.assertEqual(vectors.get_related(e1, 10), [])

        vectors = ModelVectorBuilder(queryset=Entry.objects.all(),
                                     fields=['title', 'content'])
        with self.assertNumQueries(2):
            self.assertEqual(vectors.get_related(e1, 10), [e2])
        with self.assertNumQueries(1):
            self.assertEqual(vectors.get_related(e1, 10), [e2])

    def test_cached_vector_builder(self):
        params = {'title': 'My entry number 1',
                  'content': 'My content number 1',
                  'slug': 'my-entry-1'}
        e1 = Entry.objects.create(**params)
        v = CachedModelVectorBuilder(
            queryset=Entry.objects.all(), fields=['title', 'content'])
        with self.assertNumQueries(1):
            self.assertEqual(len(v.columns), 3)
        with self.assertNumQueries(0):
            self.assertEqual(len(v.columns), 3)
        with self.assertNumQueries(0):
            self.assertEqual(v.get_related(e1, 5), [])

        for i in range(1, 3):
            params = {'title': 'My entry %s' % i,
                      'content': 'My content %s' % i,
                      'slug': 'my-entry-%s' % i}
            Entry.objects.create(**params)
        v = CachedModelVectorBuilder(
            queryset=Entry.objects.all(), fields=['title', 'content'])
        with self.assertNumQueries(0):
            self.assertEqual(len(v.columns), 3)
        with self.assertNumQueries(0):
            self.assertEqual(v.get_related(e1, 5), [])

        v.cache_flush()
        with self.assertNumQueries(2):
            self.assertEqual(len(v.get_related(e1, 5)), 2)
        with self.assertNumQueries(0):
            self.assertEqual(len(v.get_related(e1, 5)), 2)
        with self.assertNumQueries(0):
            self.assertEqual(len(v.columns), 3)

        v = CachedModelVectorBuilder(
            queryset=Entry.objects.all(), fields=['title', 'content'])
        with self.assertNumQueries(0):
            self.assertEqual(len(v.columns), 3)
        with self.assertNumQueries(0):
            self.assertEqual(len(v.get_related(e1, 5)), 2)

    def test_raw_clean(self):
        v = ModelVectorBuilder(queryset=Entry.objects.none(), fields=['title'])
        self.assertEqual(v.raw_clean('<p>HTML Content</p>'),
                         ['html', 'content'])
        self.assertEqual(v.raw_clean('<p>An HTML Content</p>'),
                         ['html', 'content'])
        self.assertEqual(v.raw_clean('<p>An HTML Content 2</p>'),
                         ['html', 'content'])
        self.assertEqual(v.raw_clean('<p>!HTML Content ?</p>'),
                         ['html', 'content'])

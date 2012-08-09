"""Test cases for Zinnia's comparison"""
from django.test import TestCase

from zinnia.models.entry import Entry
from zinnia.comparison import pearson_score
from zinnia.comparison import VectorBuilder
from zinnia.comparison import ClusteredModel


class ComparisonTestCase(TestCase):
    """Test cases for comparison tools"""

    def test_pearson_score(self):
        self.assertEquals(pearson_score([42], [42]), 0.0)
        self.assertEquals(pearson_score([0, 1, 2], [0, 1, 2]), 0.0)
        self.assertEquals(pearson_score([0, 1, 3], [0, 1, 2]),
                          0.051316701949486232)
        self.assertEquals(pearson_score([0, 1, 2], [0, 1, 3]),
                          0.051316701949486232)

    def test_clustered_model(self):
        params = {'title': 'My entry 1', 'content': 'My content 1',
                  'tags': 'zinnia, test', 'slug': 'my-entry-1'}
        Entry.objects.create(**params)
        params = {'title': 'My entry 2', 'content': 'My content 2',
                  'tags': 'zinnia, test', 'slug': 'my-entry-2'}
        Entry.objects.create(**params)
        cm = ClusteredModel(Entry.objects.all())
        self.assertEquals(cm.dataset().values(), ['1', '2'])
        cm = ClusteredModel(Entry.objects.all(),
                            ['title', 'excerpt', 'content'])
        self.assertEquals(cm.dataset().values(), ['My entry 1  My content 1',
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
        self.assertEquals(columns, ['content', 'This', 'my', 'is', '1',
                                    'second', '2', 'first'])
        self.assertEquals(dataset.values(), [[1, 1, 1, 1, 1, 0, 0, 1],
                                             [0, 0, 0, 0, 0, 1, 1, 0]])

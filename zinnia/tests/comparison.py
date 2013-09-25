"""Test cases for Zinnia's comparison"""
from django.test import TestCase

from zinnia.models.entry import Entry
from zinnia.comparison import pearson_score
from zinnia.comparison import VectorBuilder
from zinnia.comparison import ClusteredModel


class ComparisonTestCase(TestCase):
    """Test cases for comparison tools"""

    def test_pearson_score(self):
        self.assertEqual(pearson_score([42], [42]), 0.0)
        self.assertEqual(pearson_score([0, 1, 2], [0, 1, 2]), 0.0)
        #The pearson algorithm was incorrect. My results have been verified
        #with a wolfram calculator here:
        #http://www.wolframalpha.com/widgets/view.jsp?
        #id=3038cb5ccf72f21a13801d9c78f70937

        #One thing that I don't understand is why the pearson
        #calculator is returning 1-r . I've left it as is.
        self.assertEqual(pearson_score([0, 1, 3], [0, 1, 2]),
                          0.01801949393803437)
        self.assertEqual(pearson_score([0, 1, 2], [0, 1, 3]),
                          0.01801949393803437)

    def test_clustered_model(self):
        params = {'title': 'My entry 1', 'content': 'My content 1',
                  'tags': 'zinnia, test', 'slug': 'my-entry-1'}
        Entry.objects.create(**params)
        params = {'title': 'My entry 2', 'content': 'My content 2',
                  'tags': 'zinnia, test', 'slug': 'my-entry-2'}
        Entry.objects.create(**params)
        cm = ClusteredModel(Entry.objects.all())
        #In python 2.7 and up, values and friends return views, not lists
        self.assertEqual(list(cm.dataset().values()), ['1', '2'])
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
        #The ordering of columns is dependent on the order that a dictionary's
        #keys were iterated through (words_total.items, to be specific)
        #, which is undefined. Therefore, we cannot rely on its order being
        #fixed. So, I just sort the list to get it in a consistant order
        self.assertEqual(sorted(columns), sorted(
            ['content', 'This', 'my', 'is', '1',
             'second', '2', 'first']))
        #Again, we can't rely on the ordering of dict contents
        #being constant. I *think* I've addressed all of
        #the sorting issues, but I might have missed something.
        #If the vectorbuilder needs ordering to matter,
        #the algorithm used needs to be changed significantly.
        self.assertEqual(sorted([sorted(row) for row in dataset.values()]),
                         sorted([sorted([1, 1, 1, 1, 1, 0, 0, 1]),
                                 sorted([0, 0, 0, 0, 0, 1, 1, 0])]))

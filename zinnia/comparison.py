"""Comparison tools for Zinnia"""
import sys
import unicodedata
from math import sqrt

from django.utils import six
from django.core.cache import caches
from django.utils.html import strip_tags
from django.core.cache import InvalidCacheBackendError

from zinnia.settings import STOP_WORDS


PUNCTUATION = dict.fromkeys(
    i for i in range(sys.maxunicode)
    if unicodedata.category(six.unichr(i)).startswith('P')
)


class ClusteredModel(object):
    """
    Wrapper around Model class
    building a dataset of instances.
    """

    def __init__(self, queryset, fields):
        self.fields = fields
        self.queryset = queryset

    def dataset(self):
        """
        Generate a dataset based on the queryset
        and the specified fields.
        """
        dataset = {}
        for item in self.queryset.values_list(*(['pk'] + self.fields)):
            item = list(item)
            item_pk = item.pop(0)
            datas = ' '.join(map(six.text_type, item))
            dataset[item_pk] = self.clean(datas)
        return dataset

    def clean(self, datas):
        """
        Apply a cleaning on the datas.
        """
        datas = strip_tags(datas)             # Remove HTML
        datas = datas.translate(PUNCTUATION)  # Remove punctuation
        datas = STOP_WORDS.rebase(datas, '')  # Remove STOP WORDS
        datas = datas.lower()
        return datas


class VectorBuilder(object):
    """
    Build a list of vectors based on datasets.
    """

    def __init__(self, queryset, fields):
        self.clustered_model = ClusteredModel(queryset, fields)

    def build_dataset(self):
        """
        Generate the whole dataset.
        """
        data = {}
        words_total = {}

        model_data = self.clustered_model.dataset()
        for instance, words in model_data.items():
            words_item_total = {}
            for word in words.split():
                words_total.setdefault(word, 0)
                words_item_total.setdefault(word, 0)
                words_total[word] += 1
                words_item_total[word] += 1
            data[instance] = words_item_total

        dataset = {}
        columns = list(words_total.keys())
        for instance in data.keys():
            dataset[instance] = [data[instance].get(word, 0)
                                 for word in columns]
        return columns, dataset

    def columns_dataset(self):
        """
        Cache system for columns and dataset.
        """
        cache = get_comparison_cache()
        columns_dataset = cache.get('vectors')
        if not columns_dataset:
            columns_dataset = self.build_dataset()
            cache.set('vectors', columns_dataset)
        return columns_dataset

    @property
    def columns(self):
        """
        Access to columns.
        """
        return self.columns_dataset()[0]

    @property
    def dataset(self):
        """
        Access to dataset.
        """
        return self.columns_dataset()[1]


def pearson_score(list1, list2):
    """
    Compute the Pearson' score between 2 lists of vectors.
    """
    size = len(list1)
    sum1 = sum(list1)
    sum2 = sum(list2)
    sum_sq1 = sum([pow(l, 2) for l in list1])
    sum_sq2 = sum([pow(l, 2) for l in list2])

    prod_sum = sum([list1[i] * list2[i] for i in range(size)])

    num = prod_sum - (sum1 * sum2 / float(size))
    den = sqrt((sum_sq1 - pow(sum1, 2.0) / size) *
               (sum_sq2 - pow(sum2, 2.0) / size))

    return num / den


def compute_related(object_id, dataset):
    """
    Compute related pks to an object with a dataset.
    """
    object_vector = dataset.get(object_id)
    if not object_vector:
        return []

    object_related = {}
    for o_id, o_vector in dataset.items():
        if o_id != object_id:
            try:
                object_related[o_id] = pearson_score(object_vector, o_vector)
            except ZeroDivisionError:
                pass

    related = sorted(object_related.items(),
                     key=lambda k_v: k_v[1], reverse=True)
    return [rel[0] for rel in related]


def get_comparison_cache():
    """
    Try to access to ``zinnia_comparison`` cache backend,
    if fail use the ``default`` cache backend.
    """
    try:
        comparison_cache = caches['zinnia_comparison']
    except InvalidCacheBackendError:
        comparison_cache = caches['default']
    return comparison_cache

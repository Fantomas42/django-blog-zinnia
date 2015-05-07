"""Comparison tools for Zinnia"""
import sys
import unicodedata
from math import sqrt

from django.utils import six
from django.core.cache import caches
from django.utils.html import strip_tags
from django.utils.functional import cached_property
from django.core.cache import InvalidCacheBackendError

from zinnia.models.entry import Entry
from zinnia.settings import STOP_WORDS
from zinnia.settings import COMPARISON_FIELDS


PUNCTUATION = dict.fromkeys(
    i for i in range(sys.maxunicode)
    if unicodedata.category(six.unichr(i)).startswith('P')
)


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


class ModelVectorBuilder(object):
    """
    Build a list of vectors based on a Queryset.
    """
    limit = None
    fields = None
    queryset = None

    def __init__(self, **kwargs):
        self.limit = kwargs.pop('limit', self.limit)
        self.fields = kwargs.pop('fields', self.fields)
        self.queryset = kwargs.pop('queryset', self.queryset)

    def compute_related(self, object_id, score=pearson_score):
        """
        Compute the most related pks to an object's pk.
        """
        dataset = self.dataset
        object_vector = dataset.get(object_id)
        if not object_vector:
            return []

        object_related = {}
        for o_id, o_vector in dataset.items():
            if o_id != object_id:
                try:
                    object_related[o_id] = score(object_vector, o_vector)
                except ZeroDivisionError:
                    pass

        related = sorted(object_related.items(),
                         key=lambda k_v: k_v[1], reverse=True)
        return [rel[0] for rel in related]

    @cached_property
    def raw_dataset(self):
        """
        Generate a raw dataset based on the queryset
        and the specified fields.
        """
        dataset = {}
        queryset = self.queryset.values_list(*(['pk'] + self.fields))
        if self.limit:
            queryset = queryset[:self.limit]
        for item in queryset:
            item = list(item)
            item_pk = item.pop(0)
            datas = ' '.join(map(six.text_type, item))
            dataset[item_pk] = self.raw_clean(datas)
        return dataset

    def raw_clean(self, datas):
        """
        Apply a cleaning on raw datas.
        """
        datas = strip_tags(datas)             # Remove HTML
        datas = STOP_WORDS.rebase(datas, '')  # Remove STOP WORDS
        datas = datas.translate(PUNCTUATION)  # Remove punctuation
        datas = datas.lower()
        return datas.strip()

    @cached_property
    def columns_dataset(self):
        """
        Generate the columns and the whole dataset.
        """
        data = {}
        words_total = {}

        for instance, words in self.raw_dataset.items():
            words_item_total = {}
            for word in words.split():
                words_total.setdefault(word, 0)
                words_item_total.setdefault(word, 0)
                words_total[word] += 1
                words_item_total[word] += 1
            data[instance] = words_item_total

        columns = sorted([word for word, count in
                          words_total.items() if count > 1])
        dataset = {}
        for instance in data.keys():
            dataset[instance] = [data[instance].get(word, 0)
                                 for word in columns]
        return columns, dataset

    @property
    def columns(self):
        """
        Access to columns.
        """
        return self.columns_dataset[0]

    @property
    def dataset(self):
        """
        Access to dataset.
        """
        return self.columns_dataset[1]


class CachedModelVectorBuilder(ModelVectorBuilder):
    """
    Cached version of VectorBuilder.
    """

    @property
    def columns_dataset(self):
        """
        Implement high level cache system for columns and dataset.
        """
        cache = get_comparison_cache()
        columns_dataset = cache.get('vectors')
        if not columns_dataset:
            columns_dataset = super(CachedModelVectorBuilder, self
                                    ).columns_dataset
            cache.set('vectors', columns_dataset)
        return columns_dataset


class EntryPublishedVectorBuilder(CachedModelVectorBuilder):
    """
    Vector builder for published entries.
    """
    limit = 100
    queryset = Entry.published
    fields = COMPARISON_FIELDS


def get_comparison_cache():
    """
    Try to access to ``zinnia_comparison`` cache backend,
    if fail use the ``default`` cache backend.
    """
    try:
        comparison_cache = caches['comparison']
    except InvalidCacheBackendError:
        comparison_cache = caches['default']
    return comparison_cache

"""Comparison tools for Zinnia"""
from math import sqrt

from django.contrib.sites.models import Site
from django.core.cache import InvalidCacheBackendError
from django.core.cache import caches
from django.utils.functional import cached_property
from django.utils.html import strip_tags

import regex as re

from zinnia.models.entry import Entry
from zinnia.settings import COMPARISON_FIELDS
from zinnia.settings import STOP_WORDS


PUNCTUATION = re.compile(r'\p{P}+')


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

    def get_related(self, instance, number):
        """
        Return a list of the most related objects to instance.
        """
        related_pks = self.compute_related(instance.pk)[:number]
        related_pks = [pk for pk, score in related_pks]
        related_objects = sorted(
            self.queryset.model.objects.filter(pk__in=related_pks),
            key=lambda x: related_pks.index(x.pk))
        return related_objects

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
                         key=lambda k_v: (k_v[1], k_v[0]), reverse=True)
        return related

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
            datas = ' '.join(map(str, item))
            dataset[item_pk] = self.raw_clean(datas)
        return dataset

    def raw_clean(self, datas):
        """
        Apply a cleaning on raw datas.
        """
        datas = strip_tags(datas)             # Remove HTML
        datas = STOP_WORDS.rebase(datas, '')  # Remove STOP WORDS
        datas = PUNCTUATION.sub('', datas)    # Remove punctuation
        datas = datas.lower()
        return [d for d in datas.split() if len(d) > 1]

    @cached_property
    def columns_dataset(self):
        """
        Generate the columns and the whole dataset.
        """
        data = {}
        words_total = {}

        for instance, words in self.raw_dataset.items():
            words_item_total = {}
            for word in words:
                words_total.setdefault(word, 0)
                words_item_total.setdefault(word, 0)
                words_total[word] += 1
                words_item_total[word] += 1
            data[instance] = words_item_total

        columns = sorted(words_total.keys(),
                         key=lambda w: words_total[w],
                         reverse=True)[:250]
        columns = sorted(columns)
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
    def cache_backend(self):
        """
        Try to access to ``comparison`` cache value,
        if fail use the ``default`` cache backend config.
        """
        try:
            comparison_cache = caches['comparison']
        except InvalidCacheBackendError:
            comparison_cache = caches['default']
        return comparison_cache

    @property
    def cache_key(self):
        """
        Key for the cache.
        """
        return self.__class__.__name__

    def get_cache(self):
        """
        Get the cache from cache.
        """
        return self.cache_backend.get(self.cache_key, {})

    def set_cache(self, value):
        """
        Assign the cache in cache.
        """
        value.update(self.cache)
        return self.cache_backend.set(self.cache_key, value)

    cache = property(get_cache, set_cache)

    def cache_flush(self):
        """
        Flush the cache for this instance.
        """
        return self.cache_backend.delete(self.cache_key)

    def get_related(self, instance, number):
        """
        Implement high level cache system for get_related.
        """
        cache = self.cache
        cache_key = '%s:%s' % (instance.pk, number)
        if cache_key not in cache:
            related_objects = super(CachedModelVectorBuilder,
                                    self).get_related(instance, number)
            cache[cache_key] = related_objects
            self.cache = cache
        return cache[cache_key]

    @property
    def columns_dataset(self):
        """
        Implement high level cache system for columns and dataset.
        """
        cache = self.cache
        cache_key = 'columns_dataset'
        if cache_key not in cache:
            columns_dataset = super(CachedModelVectorBuilder, self
                                    ).columns_dataset
            cache[cache_key] = columns_dataset
            self.cache = cache
        return cache[cache_key]


class EntryPublishedVectorBuilder(CachedModelVectorBuilder):
    """
    Vector builder for published entries.
    """
    limit = 100
    queryset = Entry.published
    fields = COMPARISON_FIELDS

    @property
    def cache_key(self):
        """
        Key for the cache handling current site.
        """
        return '%s:%s' % (super(EntryPublishedVectorBuilder, self).cache_key,
                          Site.objects.get_current().pk)

"""Comparison tools for Zinnia
Based on clustered_models app"""
from math import sqrt

from zinnia.settings import F_MIN
from zinnia.settings import F_MAX


def pearson_score(list1, list2):
    """Compute the pearson score between 2 lists of vectors"""
    sum1 = sum(list1)
    sum2 = sum(list2)
    sum_sq1 = sum([pow(l, 2) for l in list1])
    sum_sq2 = sum([pow(l, 2) for l in list2])

    prod_sum = sum([list1[i] * list2[i] for i in range(len(list1))])

    num = prod_sum - (sum1 * sum2 / len(list1))
    den = sqrt((sum_sq1 - pow(sum1, 2) / len(list1)) *
               (sum_sq2 - pow(sum2, 2) / len(list2)))
    if den == 0:
        return 0.0
    return 1.0 - num / den


class ClusteredModel(object):
    """Wrapper around Model class
    building a dataset of instances"""

    def __init__(self, queryset, fields=['id']):
        self.fields = fields
        self.queryset = queryset

    def dataset(self):
        """Generate a dataset with the queryset
        and specified fields"""
        dataset = {}
        for item in self.queryset.filter():
            dataset[item] = ' '.join([unicode(getattr(item, field))
                                      for field in self.fields])
        return dataset


class VectorBuilder(object):
    """Build a list of vectors based on datasets"""

    def __init__(self, queryset, fields):
        self.key = ''
        self.columns = []
        self.dataset = {}
        self.clustered_model = ClusteredModel(queryset, fields)
        self.build_dataset()

    def build_dataset(self):
        """Generate whole dataset"""
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

        top_words = []
        for word, count in words_total.items():
            frequency = float(count) / len(data)
            if frequency > F_MIN and frequency < F_MAX:
                top_words.append(word)

        self.dataset = {}
        self.columns = top_words
        for instance in data.keys():
            self.dataset[instance] = [data[instance].get(word, 0)
                                      for word in top_words]
        self.key = self.generate_key()

    def generate_key(self):
        """Generate key for this list of vectors"""
        return self.clustered_model.queryset.count()

    def flush(self):
        """Flush the dataset"""
        if self.key != self.generate_key():
            self.build_dataset()

    def __call__(self):
        self.flush()
        return self.columns, self.dataset

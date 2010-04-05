"""Comparison tools for zinnia
Based on clustered_models app"""
from math import sqrt

from zinnia.settings import F_MIN
from zinnia.settings import F_MAX

def pearson_score(l1, l2):
    """Compute the pearson score between 2 lists of vectors"""
    sum1 = sum(l1)
    sum2 = sum(l2)
    sum_sq1 = sum([pow(l, 2) for l in l1])
    sum_sq2 = sum([pow(l, 2) for l in l2])

    prod_sum = sum([l1[i] * l2[i] for i in range(len(l1))])

    num = prod_sum - (sum1 * sum2 / len(l1))
    den = sqrt((sum_sq1 - pow(sum1, 2) / len(l1)) *
               (sum_sq2 - pow(sum2, 2) / len(l2)))
    if den == 0:
        return 0
    return 1.0 - num / den


class ClusteredModel(object):

    def __init__(self, info_dict):
        self.queryset = info_dict.get('queryset', [])
        self.fields = info_dict.get('fields', ['pk',])

    def dataset(self):
        dataset = {}
        for item in self.queryset.filter():
            dataset[item] = ' '.join([item.__dict__[field] for field in self.fields])
        return dataset


class VectorBuilder(object):
    """Build a list of vectors"""

    def __init__(self, *models_conf):
        self.key = ''
        self.columns = []
        self.dataset = {}
        self.clustered_models = [ClusteredModel(conf) for conf in models_conf]
        self.build_dataset()

    def build_dataset(self):
        data = {}
        words_total = {}

        for clustered_model in self.clustered_models:
            model_data = clustered_model.dataset()
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
            self.dataset[instance] = [data[instance].get(word, 0) for word in top_words]
        self.key = self.generate_key()

    def generate_key(self):
        return '-'.join([str(c.queryset.filter().count()) for c in self.clustered_models])

    def flush(self):
        if self.key != self.generate_key():
            self.build_dataset()

    def __call__(self):
        self.flush()
        return self.columns, self.dataset
    
        

"""Mixins for enabling prefetching in views returning list of entries"""
from django.core.exceptions import ImproperlyConfigured


class PrefetchRelatedMixin(object):
    """
    Mixin allow you to provides list of relation names
    to be prefetching when the queryset is build.
    """
    relation_names = None

    def get_queryset(self):
        """
        Check if relation_names is correctly set and
        do a prefetch related on the queryset with it.
        """
        if self.relation_names is None:
            raise ImproperlyConfigured(
                u"'%s' must define 'relation_names'" %
                self.__class__.__name__)
        if not isinstance(self.relation_names, (tuple, list)):
            raise ImproperlyConfigured(
                u"%s's relation_names property must be a tuple or list." %
                self.__class__.__name__)
        return super(PrefetchRelatedMixin, self
                     ).get_queryset().prefetch_related(*self.relation_names)


class PrefetchCategoriesAuthorsMixin(PrefetchRelatedMixin):
    """
    Mixin for prefetching categories and authors related
    to the entries in the queryset.
    """
    relation_names = ('categories', 'authors')

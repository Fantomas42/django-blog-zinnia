"""Filters for Zinnia admin"""
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ungettext_lazy
from django.utils.translation import ugettext_lazy as _

from zinnia.models.author import Author
from zinnia.models.category import Category
from django.db.models import Count


class RelatedPublishedFilter(SimpleListFilter):
    """
    Base filter for related objects to published entries.
    """
    model = None
    lookup_key = None

    def lookups(self, request, model_admin):
        """
        Return published objects with the number of entries.
        """
        active_objects = self.model.published.all().annotate(
            number_of_entries=Count('entries'))
        for active_object in active_objects:
            yield (
                str(active_object.pk), ungettext_lazy(
                    '%(item)s (%(count)i entry)',
                    '%(item)s (%(count)i entries)',
                    active_object.number_of_entries) % {
                        'item': active_object.__unicode__(),
                        'count': active_object.number_of_entries})

    def queryset(self, request, queryset):
        """
        Return the object's entries if a value is set.
        """
        if self.value():
            params = {self.lookup_key: self.value()}
            return queryset.filter(**params)


class AuthorListFilter(RelatedPublishedFilter):
    """
    List filter for EntryAdmin with published authors only.
    """
    model = Author
    lookup_key = 'authors__id'
    title = _('published authors')
    parameter_name = 'author'


class CategoryListFilter(RelatedPublishedFilter):
    """
    List filter for EntryAdmin about categories
    with published entries.
    """
    model = Category
    lookup_key = 'categories__id'
    title = _('published categories')
    parameter_name = 'category'

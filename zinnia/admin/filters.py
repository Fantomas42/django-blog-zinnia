"""Filters for Zinnia admin"""
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _

from zinnia.models import Author
from django.db.models import Count


class AuthorListFilter(SimpleListFilter):
    """List filter for EntryAdmin filtering
    possibilities to published authors only."""
    title = _('author')
    parameter_name = 'author'

    def lookups(self, request, model_admin):
        """Return published auhtors choicex"""
        active_authors = Author.published.all().annotate(
            number_of_entries=Count('entries'))
        for author in active_authors:
            yield (str(author.pk), _('%s (%i entries)') % (
                author.__unicode__(), author.number_of_entries))

    def queryset(self, request, queryset):
        """Return the author's entries"""
        if self.value():
            return queryset.filter(authors__id=self.value())

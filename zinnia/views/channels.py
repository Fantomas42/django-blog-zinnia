"""Views for Zinnia channels"""
from django.views.generic.list import ListView

from zinnia.models.entry import Entry
from zinnia.settings import PAGINATION
from zinnia.views.mixins.prefetch_related import PrefetchCategoriesAuthorsMixin


class BaseEntryChannel(object):
    """
    Mixin for displaying a custom selection of entries
    based on a search query, useful to build SEO/SMO pages
    aggregating entries on a thematic or for building a
    custom homepage.
    """
    query = ''

    def get_queryset(self):
        """
        Override the get_queryset method to build
        the queryset with entry matching query.
        """
        return Entry.published.search(self.query)

    def get_context_data(self, **kwargs):
        """
        Add query in context.
        """
        context = super(BaseEntryChannel, self).get_context_data(**kwargs)
        context.update({'query': self.query})
        return context


class EntryChannel(PrefetchCategoriesAuthorsMixin,
                   BaseEntryChannel,
                   ListView):
    """
    Channel view for entries combinating these mixins:

    - PrefetchCategoriesAuthorsMixin to prefetch related Categories
      and Authors to belonging the entry list.
    - BaseEntryChannel to provide the behavior of the view.
    - ListView to implement the ListView and template name resolution.
    """
    paginate_by = PAGINATION

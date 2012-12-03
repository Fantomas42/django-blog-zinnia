"""Views for Zinnia entries search"""
from django.views.generic.list import ListView
from django.utils.translation import ugettext as _

from zinnia.models.entry import Entry
from zinnia.settings import PAGINATION
from zinnia.views.mixins.prefetch_related import PrefetchCategoriesAuthorsMixin


class BaseEntrySearch(object):
    """
    Mixin providing the behavior of the entry search view,
    by returning in the context the pattern searched, the
    error if something wrong has happened and finally the
    the queryset of published entries matching the pattern.
    """
    pattern = ''
    error = None

    def get_queryset(self):
        """
        Overridde the get_queryset method to
        do some validations and build the search queryset.
        """
        entries = Entry.published.none()

        if self.request.GET:
            self.pattern = self.request.GET.get('pattern', '')
            if len(self.pattern) < 3:
                self.error = _('The pattern is too short')
            else:
                entries = Entry.published.search(self.pattern)
        else:
            self.error = _('No pattern to search found')
        return entries

    def get_context_data(self, **kwargs):
        """
        Add error and pattern in context.
        """
        context = super(BaseEntrySearch, self).get_context_data(**kwargs)
        context.update({'error': self.error, 'pattern': self.pattern})
        return context


class EntrySearch(PrefetchCategoriesAuthorsMixin,
                  BaseEntrySearch,
                  ListView):
    """
    Search view for entries combinating these mixins:

    - PrefetchCategoriesAuthorsMixin to prefetch related Categories
      and Authors to belonging the entry list.
    - BaseEntrySearch to provide the behavior of the view.
    - ListView to implement the ListView and template name resolution.
    """
    paginate_by = PAGINATION
    template_name_suffix = '_search'

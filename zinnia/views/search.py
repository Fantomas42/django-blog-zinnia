"""Views for Zinnia entries search"""
from django.views.generic.list import ListView
from django.utils.translation import ugettext as _

from zinnia.models import Entry
from zinnia.settings import PAGINATION


class EntrySearch(ListView):
    """View for searching entries"""
    pattern = ''
    error = None
    paginate_by = PAGINATION
    template_name = 'zinnia/entry_search.html'

    def get_queryset(self):
        """Overridde the get_queryset method to
        do some validations and the search queryset"""
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
        """Add error and pattern in the context"""
        context = super(ListView, self).get_context_data(**kwargs)
        context.update({'error': self.error, 'pattern': self.pattern})
        return context

"""Views for Zinnia authors"""
from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.list import BaseListView

from zinnia.models import Author
from zinnia.settings import PAGINATION
from zinnia.views.mixins import CallableQuerysetMixin
from zinnia.views.mixins import EntryQuerysetTemplateResponseMixin


class AuthorList(CallableQuerysetMixin, ListView):
    """View returning a list of all published authors"""
    queryset = Author.published.all
    context_object_name = 'author'


class AuthorDetail(EntryQuerysetTemplateResponseMixin, BaseListView):
    """Display the entries of an author"""
    model_type = 'author'
    paginate_by = PAGINATION

    def get_model_name(self):
        """The model name is the author's username"""
        return self.author.username

    def get_queryset(self):
        """Return a queryset of entries published
        belonging to the current author"""
        self.author = get_object_or_404(Author, username=self.kwargs['username'])
        return self.author.entries_published()

    def get_context_data(self, **kwargs):
        """Add the current author in context"""
        context = super(AuthorDetail, self).get_context_data(**kwargs)
        context['author'] = self.author
        return context

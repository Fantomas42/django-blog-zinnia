"""Views for Zinnia authors"""
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.list import BaseListView

from zinnia.settings import PAGINATION
from zinnia.models.author import Author
from zinnia.views.mixins.templates import EntryQuerysetTemplateResponseMixin
from zinnia.views.mixins.prefetch_related import PrefetchCategoriesAuthorsMixin


class AuthorList(ListView):
    """
    View returning a list of all published authors.
    """

    def get_queryset(self):
        """
        Return a queryset of published authors,
        with a count of their entries published.
        """
        return Author.published.all().annotate(
            count_entries_published=Count('entries'))


class BaseAuthorDetail(object):
    """
    Mixin providing the behavior of the author detail view,
    by returning in the context the current author and a
    queryset containing the entries written by author.
    """

    def get_queryset(self):
        """
        Retrieve the author by his username and
        build a queryset of his published entries.
        """
        self.author = get_object_or_404(
            Author, username=self.kwargs['username'])
        return self.author.entries_published()

    def get_context_data(self, **kwargs):
        """
        Add the current author in context.
        """
        context = super(BaseAuthorDetail, self).get_context_data(**kwargs)
        context['author'] = self.author
        return context


class AuthorDetail(EntryQuerysetTemplateResponseMixin,
                   PrefetchCategoriesAuthorsMixin,
                   BaseAuthorDetail,
                   BaseListView):
    """
    Detailed view for an Author combinating these mixins:

    - EntryQuerysetTemplateResponseMixin to provide custom templates
      for the author display page.
    - PrefetchCategoriesAuthorsMixin to prefetch related Categories
      and Authors to belonging the entry list.
    - BaseAuthorDetail to provide the behavior of the view.
    - BaseListView to implement the ListView.
    """
    model_type = 'author'
    paginate_by = PAGINATION

    def get_model_name(self):
        """
        The model name is the author's username.
        """
        return self.author.username

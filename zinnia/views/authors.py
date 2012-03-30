"""Views for Zinnia authors"""
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from zinnia.models import Author
from zinnia.settings import PAGINATION
from zinnia.views.mixins import EntryQuerysetTemplatesMixin

class AuthorList(ListView):
    model = Author
    context_object_name = 'author'

    def get_object(self,queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        username = self.kwargs.get('username',None)

        if username is not None:
            queryset = queryset.filter()


class AuthorDetail(EntryQuerysetTemplatesMixin, ListView):
    """Display the entries of an author"""

    model_type = 'author'
    context_object_name = 'queryset'
    paginate_by = PAGINATION

    def get_model_name(self):
        return self.author.username

    def get_queryset(self):
        return self.author.entries_published()

    def get_context_data(self,**kwargs):
        context = super(AuthorDetail,self).get_context_data(**kwargs)
        context['author'] = self.author
        return context

    def get(self,*args,**kwargs):
        self.author = get_object_or_404(Author,username=kwargs['username'])
        return super(AuthorDetail,self).get(*args,**kwargs)
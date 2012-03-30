"""Views for Zinnia categories"""
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from zinnia.models import Category
from zinnia.settings import PAGINATION
from zinnia.views.mixins import EntryQuerysetTemplatesMixin


def get_category_or_404(path):
    """Retrieve a Category by a path"""
    path_bits = [p for p in path.split('/') if p]
    return get_object_or_404(Category, slug=path_bits[-1])


class CategoryListView(ListView):
    model = Category


class CategoryDetailView(EntryQuerysetTemplatesMixin, ListView):
    model_type = 'category'
    paginate_by = PAGINATION

    def get_model_name(self):
        return self.category.slug

    def get_queryset(self):
        return self.category.entries_published()

    def get_context_data(self,**kwargs):
        context = super(CategoryDetailView,self).get_context_data(**kwargs)
        context['category'] = self.category
        return context

    def get(self,*args,**kwargs):
        self.category = get_category_or_404(self.kwargs['path'])
        return super(CategoryDetailView,self).get(*args,**kwargs)
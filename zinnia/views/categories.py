"""Views for Zinnia categories"""
from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.list import BaseListView

from zinnia.models import Category
from zinnia.settings import PAGINATION
from zinnia.views.mixins.templates import EntryQuerysetTemplateResponseMixin


def get_category_or_404(path):
    """Retrieve a Category instance by a path"""
    path_bits = [p for p in path.split('/') if p]
    return get_object_or_404(Category, slug=path_bits[-1])


class CategoryList(ListView):
    """View returning a list of all the categories"""
    queryset = Category.objects.all()


class CategoryDetail(EntryQuerysetTemplateResponseMixin, BaseListView):
    """View returning a list of all the entries
    belonging to a category"""
    model_type = 'category'
    paginate_by = PAGINATION

    def get_model_name(self):
        """The model name is the category's slug"""
        return self.category.slug

    def get_queryset(self):
        """Return a queryset of entries published
        belonging to the current category"""
        self.category = get_category_or_404(self.kwargs['path'])
        return self.category.entries_published()

    def get_context_data(self, **kwargs):
        """Add the current category in context"""
        context = super(CategoryDetail, self).get_context_data(**kwargs)
        context['category'] = self.category
        return context

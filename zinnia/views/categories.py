"""Views for Zinnia categories"""
from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.list import BaseListView

from zinnia.models.category import Category
from zinnia.settings import PAGINATION
from zinnia.views.mixins.templates import EntryQuerysetTemplateResponseMixin
from zinnia.views.mixins.prefetch_related import PrefetchCategoriesAuthorsMixin


def get_category_or_404(path):
    """Retrieve a Category instance by a path"""
    path_bits = [p for p in path.split('/') if p]
    return get_object_or_404(Category, slug=path_bits[-1])


class CategoryList(ListView):
    """
    View returning a list of all the categories.
    """
    queryset = Category.objects.all()


class BaseCategoryDetail(object):
    """
    Mixin providing the behavior of the category detail view,
    by returning in the context the current category and a
    queryset containing the entries published under it.
    """

    def get_queryset(self):
        """
        Retrieve the category by his path and
        build a queryset of her published entries.
        """
        self.category = get_category_or_404(self.kwargs['path'])
        return self.category.entries_published()

    def get_context_data(self, **kwargs):
        """
        Add the current category in context.
        """
        context = super(BaseCategoryDetail, self).get_context_data(**kwargs)
        context['category'] = self.category
        return context


class CategoryDetail(EntryQuerysetTemplateResponseMixin,
                     PrefetchCategoriesAuthorsMixin,
                     BaseCategoryDetail,
                     BaseListView):
    """
    Detailed view for a Category combinating these mixins:

    - EntryQuerysetTemplateResponseMixin to provide custom templates
      for the category display page.
    - PrefetchCategoriesAuthorsMixin to prefetch related Categories
      and Authors to belonging the entry list.
    - BaseCategoryDetail to provide the behavior of the view.
    - BaseListView to implement the ListView.
    """
    model_type = 'category'
    paginate_by = PAGINATION

    def get_model_name(self):
        """
        The model name is the category's slug.
        """
        return self.category.slug

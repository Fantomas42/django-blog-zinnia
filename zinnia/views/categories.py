"""Views for zinnia categories"""
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list

from zinnia.models import Category
from zinnia.settings import PAGINATION


def get_category_or_404(path):
    """Retrieve a Category by a path"""
    path_bits = [p for p in path.split('/') if p]
    return get_object_or_404(Category, slug=path_bits[-1])

def category_detail(request, path, page=None):
    """Display the entries of a category"""
    category = get_category_or_404(path)

    return object_list(request, queryset=category.entries_published_set(),
                       paginate_by=PAGINATION, page=page,
                       extra_context={'category': category})

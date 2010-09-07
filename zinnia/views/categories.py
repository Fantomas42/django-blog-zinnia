"""Views for zinnia categories"""
from django.http import Http404
from django.shortcuts import get_list_or_404
from django.views.generic.list_detail import object_list

from zinnia.models import Category
from zinnia.settings import PAGINATION

def category_detail(request, path, page=None):
    """Display the entries of a category"""

    path_bits = [p for p in path.split('/') if p]

    category = None
    for cat in get_list_or_404(Category, slug=path_bits[-1]):
        if cat.tree_path in path:
            category = cat
    if not category:
        raise Http404

    return object_list(request, queryset=category.entries_published_set(),
                       paginate_by=PAGINATION, page=page,
                       extra_context={'category': category})

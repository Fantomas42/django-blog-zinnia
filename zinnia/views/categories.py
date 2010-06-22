"""Views for zinnia categories"""
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list

from zinnia.models import Category
from zinnia.settings import PAGINATION

def category_detail(request, slug, page=None):
    """Display the entries of a category"""
    category = get_object_or_404(Category, slug=slug)
    return object_list(request, queryset=category.entries_published_set(),
                       paginate_by=PAGINATION, page=page,
                       extra_context={'category': category})

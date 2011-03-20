"""Views for Zinnia categories"""
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list

from zinnia.models import Category
from zinnia.settings import PAGINATION
from zinnia.views.decorators import template_name_for_entry_queryset_filtered


def get_category_or_404(path):
    """Retrieve a Category by a path"""
    path_bits = [p for p in path.split('/') if p]
    return get_object_or_404(Category, slug=path_bits[-1])


def category_detail(request, path, page=None):
    """Display the entries of a category"""
    category = get_category_or_404(path)
    template_name = template_name_for_entry_queryset_filtered(
        'category', category.slug)

    return object_list(request, queryset=category.entries_published_set(),
                       paginate_by=PAGINATION, page=page,
                       template_name=template_name,
                       extra_context={'category': category})

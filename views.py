"""Views of the zinnia app"""
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list

from zinnia.models import Entry
from zinnia.models import Category
from zinnia.managers import entries_published


def author_detail(request, username):
    """Display the entries of an author"""
    author = get_object_or_404(User, username=username)
    return object_list(request, queryset=entries_published(author.entry_set),
                       extra_context={'author': author})


def category_detail(request, slug):
    """Display the entries of a category"""
    category = get_object_or_404(Category, slug=slug)
    return object_list(request, queryset=category.entries_published_set(),
                       extra_context={'category': category})


def search_list(request):
    """Search entries matching with a pattern"""
    error = None
    pattern = None
    entries = Entry.published.none()

    if request.GET:
        pattern = request.GET.get('q', '')
        if len(pattern) < 3:
            error = _('the pattern is too short')
        else:
            entries = Entry.published.search(pattern)
    else:
        error = _('no pattern to search found')

    return object_list(request, queryset=entries,
                        template_name='zinnia/entry_search.html',
                        extra_context={
                            'error': error,
                            'pattern': pattern,
                        })

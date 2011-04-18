"""Views for Zinnia authors"""
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list

from zinnia.models import Author
from zinnia.settings import PAGINATION
from zinnia.views.decorators import update_queryset
from zinnia.views.decorators import template_name_for_entry_queryset_filtered


author_list = update_queryset(object_list, Author.published.all)


def author_detail(request, username, page=None, **kwargs):
    """Display the entries of an author"""
    extra_context = kwargs.pop('extra_context', {})

    author = get_object_or_404(Author, username=username)
    if not kwargs.get('template_name'):
        # populate the template_name if not provided in kwargs.
        kwargs['template_name'] = template_name_for_entry_queryset_filtered(
                                  'author', author.username)

    extra_context.update({'author': author})
    kwargs['extra_context'] = extra_context

    return object_list(request, queryset=author.entries_published_set(),
                       paginate_by=PAGINATION, page=page,
                       **kwargs)

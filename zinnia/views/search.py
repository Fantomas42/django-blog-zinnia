"""Views for Zinnia entries search"""
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list

from zinnia.models import Entry
from zinnia.settings import PAGINATION


def entry_search(request, **kwargs):
    """Search entries matching with a pattern"""
    error = None
    pattern = None
    entries = Entry.published.none()
    extra_context = kwargs.pop('extra_context', {})

    if request.GET:
        pattern = request.GET.get('pattern', '')
        if len(pattern) < 3:
            error = _('The pattern is too short')
        else:
            entries = Entry.published.search(pattern)
    else:
        error = _('No pattern to search found')

    if not kwargs.get('template_name'):
        kwargs['template_name'] = 'zinnia/entry_search.html'

    extra_context.update({'error': error, 'pattern': pattern})
    kwargs['extra_context'] = extra_context

    return object_list(request, queryset=entries,
                       paginate_by=PAGINATION, **kwargs)

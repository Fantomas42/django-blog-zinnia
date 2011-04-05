"""Views for Zinnia entries search"""
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list

from zinnia.models import Entry
from zinnia.settings import PAGINATION


def entry_search(request):
    """Search entries matching with a pattern"""
    error = None
    pattern = None
    entries = Entry.published.none()

    if request.GET:
        pattern = request.GET.get('pattern', '')
        if len(pattern) < 3:
            error = _('The pattern is too short')
        else:
            entries = Entry.published.search(pattern)
    else:
        error = _('No pattern to search found')

    return object_list(request, queryset=entries,
                       paginate_by=PAGINATION,
                       template_name='zinnia/entry_search.html',
                       extra_context={'error': error,
                                      'pattern': pattern})

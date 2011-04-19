"""Views for Zinnia tags"""
from django.views.generic.list_detail import object_list

from tagging.views import tagged_object_list

from zinnia.models import Entry
from zinnia.settings import PAGINATION
from zinnia.managers import tags_published
from zinnia.views.decorators import update_queryset
from zinnia.views.decorators import template_name_for_entry_queryset_filtered


tag_list = update_queryset(object_list, tags_published)

def tag_detail(request, tag, page=None, **kwargs):
    """Display the entries of a tag"""
    if not kwargs.get('template_name'):
        # populate the template_name if not provided in kwargs.
        kwargs['template_name'] = template_name_for_entry_queryset_filtered(
                                'tag', tag)

    return tagged_object_list(request, tag=tag,
                              queryset_or_model=Entry.published.all(),
                              paginate_by=PAGINATION, page=page,
                              **kwargs)

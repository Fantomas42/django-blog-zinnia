"""Views for Zinnia tags"""
from django.views.generic.list_detail import object_list

from tagging.views import tagged_object_list

from zinnia.models import Entry
from zinnia.settings import PAGINATION
from zinnia.managers import tags_published
from zinnia.views.decorators import update_queryset
from zinnia.views.decorators import template_name_for_entry_queryset_filtered


tag_list = update_queryset(object_list, tags_published)


def tag_detail(request, tag, page=None):
    """Display the entries of a tag"""
    template_name = template_name_for_entry_queryset_filtered(
        'tag', tag)

    return tagged_object_list(request, tag=tag,
                              queryset_or_model=Entry.published.all(),
                              paginate_by=PAGINATION, page=page,
                              template_name=template_name)

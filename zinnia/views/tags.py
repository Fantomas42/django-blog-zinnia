"""Views for Zinnia tags"""
from django.http import Http404
from django.views.generic.list import ListView
from django.views.generic.list import BaseListView
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from tagging.utils import get_tag
from tagging.models import Tag
from tagging.models import TaggedItem

from zinnia.models.entry import Entry
from zinnia.settings import PAGINATION
from zinnia.views.mixins.templates import EntryQuerysetTemplateResponseMixin
from zinnia.views.mixins.prefetch_related import PrefetchCategoriesAuthorsMixin


class TagList(ListView):
    """
    View return a list of all published tags.
    """
    template_name = 'zinnia/tag_list.html'
    context_object_name = 'tag_list'

    def get_queryset(self):
        """
        Return a queryset of published tags,
        with a count of their entries published.
        """
        return Tag.objects.usage_for_queryset(
            Entry.published.all(), counts=True)


class BaseTagDetail(object):
    """
    Mixin providing the behavior of the tag detail view,
    by returning in the context the current tag and a
    queryset containing the entries published with the tag.
    """

    def get_queryset(self):
        """
        Retrieve the tag by his name and
        build a queryset of his published entries.
        """
        self.tag = get_tag(self.kwargs['tag'])
        if self.tag is None:
            raise Http404(_('No Tag found matching "%s".') %
                          self.kwargs['tag'])
        return TaggedItem.objects.get_by_model(
            Entry.published.all(), self.tag)

    def get_context_data(self, **kwargs):
        """
        Add the current tag in context.
        """
        context = super(BaseTagDetail, self).get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


class TagDetail(EntryQuerysetTemplateResponseMixin,
                PrefetchCategoriesAuthorsMixin,
                BaseTagDetail,
                BaseListView):
    """
    Detailed view for a Tag combinating these mixins:

    - EntryQuerysetTemplateResponseMixin to provide custom templates
      for the tag display page.
    - PrefetchCategoriesAuthorsMixin to prefetch related Categories
      and Authors to belonging the entry list.
    - BaseTagDetail to provide the behavior of the view.
    - BaseListView to implement the ListView.
    """
    model_type = 'tag'
    paginate_by = PAGINATION

    def get_model_name(self):
        """
        The model name is the tag slugified.
        """
        return slugify(self.tag)

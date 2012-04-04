"""Views for Zinnia tags"""
from django.http import Http404
from django.views.generic.list import ListView
from django.views.generic.list import BaseListView
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from tagging.utils import get_tag
from tagging.models import Tag
from tagging.models import TaggedItem

from zinnia.models import Entry
from zinnia.settings import PAGINATION
from zinnia.views.mixins import EntryQuerysetTemplateResponseMixin


class TagList(ListView):
    """View return a list of all published tags"""
    template_name = 'zinnia/tag_list.html'

    def get_queryset(self):
        """Override the get_queryset method to
        compute and return the published tags"""
        return Tag.objects.usage_for_queryset(
            Entry.published.all(), counts=True)


class TagDetail(EntryQuerysetTemplateResponseMixin, BaseListView):
    """View return a list of all the entries
    published under the current tag"""
    model_type = 'tag'
    paginate_by = PAGINATION

    def get_model_name(self):
        """The model name is the tag slugified"""
        return slugify(self.tag)

    def get_queryset(self):
        """Return a queryset of entries published
        belonging to the current tag"""
        self.tag = get_tag(self.kwargs['tag'])
        if self.tag is None:
            raise Http404(_('No Tag found matching "%s".') % self.tag)
        return TaggedItem.objects.get_by_model(
            Entry.published.all(), self.tag)

    def get_context_data(self, **kwargs):
        """Add the current tag in context"""
        context = super(TagDetail, self).get_context_data(**kwargs)
        context['tag'] = self.tag
        return context

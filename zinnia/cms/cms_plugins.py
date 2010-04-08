"""Plugins for CMS"""
from django.utils.translation import ugettext as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from zinnia.models import Entry
from zinnia.models import Category
from zinnia.cms.models import LatestEntriesPlugin
from zinnia.cms.models import SelectedEntriesPlugin


class CMSLatestEntriesPlugin(CMSPluginBase):
    model = LatestEntriesPlugin
    name = _('Latest entries')
    render_template = 'zinnia/cms/entries.html'

    def render(self, context, instance, placeholder):
        if instance.category:
            entries = instance.category.entries_published_set()
        else:
            entries = Entry.published.all()

        entries = entries[:instance.number_of_entries]
        context.update({'entries': entries,
                        'object': instance, 'placeholder': placeholder})

        return context

class CMSSelectedEntriesPlugin(CMSPluginBase):
    model = SelectedEntriesPlugin
    name = _('Selected entries')
    render_template = 'zinnia/cms/entries.html'
    filter_horizontal = ['entries',]

    def render(self, context, instance, placeholder):
        context.update({'entries': instance.entries.all(),
                        'object': instance, 'placeholder': placeholder})
        return context


plugin_pool.register_plugin(CMSLatestEntriesPlugin)
plugin_pool.register_plugin(CMSSelectedEntriesPlugin)

"""Plugins for CMS"""
from django.utils.translation import ugettext as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from zinnia.models import Entry
from zinnia.models import Category
from zinnia.managers import authors_published
from zinnia.plugins.models import LatestEntriesPlugin
from zinnia.plugins.models import SelectedEntriesPlugin
from zinnia.settings import MEDIA_URL

class CMSLatestEntriesPlugin(CMSPluginBase):
    module = _('entries')
    model = LatestEntriesPlugin
    name = _('Latest entries')
    render_template = 'zinnia/cms/entry_list.html'
    fields = ('number_of_entries', 'category',
              'author', 'template_to_render')
    text_enabled = True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'author':
            kwargs['queryset'] = authors_published()
            return db_field.formfield(**kwargs)
        return super(CMSLatestEntriesPlugin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

    def render(self, context, instance, placeholder):
        entries = Entry.published.all()

        if instance.category:
            entries = entries.filter(categories=instance.category)
        if instance.author:
            entries = entries.filter(authors=instance.author)

        entries = entries[:instance.number_of_entries]
        context.update({'entries': entries,
                        'object': instance,
                        'placeholder': placeholder})
        return context

    def icon_src(self, instance):
        return MEDIA_URL + u'img/plugin.png'

class CMSSelectedEntriesPlugin(CMSPluginBase):
    module = _('entries')
    model = SelectedEntriesPlugin
    name = _('Selected entries')
    render_template = 'zinnia/cms/entry_list.html'
    fields = ('entries', 'template_to_render')
    filter_horizontal = ['entries']
    text_enabled = True

    def render(self, context, instance, placeholder):
        context.update({'entries': instance.entries.all(),
                        'object': instance,
                        'placeholder': placeholder})
        return context

    def icon_src(self, instance):
        return MEDIA_URL + u'img/plugin.png'

plugin_pool.register_plugin(CMSLatestEntriesPlugin)
plugin_pool.register_plugin(CMSSelectedEntriesPlugin)

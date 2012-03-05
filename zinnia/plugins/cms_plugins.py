"""Plugins for CMS"""
import itertools

from django.conf import settings
from django.utils.translation import ugettext as _

from tagging.models import TaggedItem
from cms.plugin_base import CMSPluginBase
from cms.models.pluginmodel import CMSPlugin
from cms.plugin_pool import plugin_pool

from zinnia.models import Entry
from zinnia.models import Author
from zinnia.managers import tags_published
from zinnia.plugins.models import RandomEntriesPlugin
from zinnia.plugins.models import LatestEntriesPlugin
from zinnia.plugins.models import SelectedEntriesPlugin


class CMSLatestEntriesPlugin(CMSPluginBase):
    """Django-cms plugin for the latest entries filtered"""
    module = _('entries')
    model = LatestEntriesPlugin
    name = _('Latest entries')
    render_template = 'zinnia/cms/entry_list.html'
    filter_horizontal = ['categories', 'authors', 'tags']
    fieldsets = (
        (None, {
            'fields': (
                'number_of_entries',
                'template_to_render'
            )
        }),
        (_('Sorting'), {
            'fields': (
                'categories',
                'authors',
                'tags'
            ),
            'classes': (
                'collapse',
            )
        }),
        (_('Advanced'), {
            'fields': (
                'subcategories',
            ),
        }),
    )

    text_enabled = True

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Filtering manytomany field"""
        if db_field.name == 'authors':
            kwargs['queryset'] = Author.published.all()
        if db_field.name == 'tags':
            kwargs['queryset'] = tags_published()
        return super(CMSLatestEntriesPlugin, self).formfield_for_manytomany(
            db_field, request, **kwargs)

    def render(self, context, instance, placeholder):
        """Update the context with plugin's data"""
        entries = Entry.published.all()

        if instance.categories.count():
            cats = instance.categories.all()

            if instance.subcategories:
                cats = itertools.chain(cats, *[c.get_descendants()
                                               for c in cats])

            entries = entries.filter(categories__in=cats)
        if instance.authors.count():
            entries = entries.filter(authors__in=instance.authors.all())
        if instance.tags.count():
            entries = TaggedItem.objects.get_union_by_model(
                entries, instance.tags.all())

        entries = entries.distinct()[:instance.number_of_entries]
        context.update({'entries': entries,
                        'object': instance,
                        'placeholder': placeholder})
        return context

    def icon_src(self, instance):
        """Icon source of the plugin"""
        return settings.STATIC_URL + u'zinnia/img/plugin.png'


class CMSSelectedEntriesPlugin(CMSPluginBase):
    """Django-cms plugin for a selection of entries"""
    module = _('entries')
    model = SelectedEntriesPlugin
    name = _('Selected entries')
    render_template = 'zinnia/cms/entry_list.html'
    fields = ('entries', 'template_to_render')
    filter_horizontal = ['entries']
    text_enabled = True

    def render(self, context, instance, placeholder):
        """Update the context with plugin's data"""
        context.update({'entries': instance.entries.all(),
                        'object': instance,
                        'placeholder': placeholder})
        return context

    def icon_src(self, instance):
        """Icon source of the plugin"""
        return settings.STATIC_URL + u'zinnia/img/plugin.png'


class CMSRandomEntriesPlugin(CMSPluginBase):
    """Django-cms plugin for random entries"""
    module = _('entries')
    model = RandomEntriesPlugin
    name = _('Random entries')
    render_template = 'zinnia/cms/random_entries.html'
    fields = ('number_of_entries', 'template_to_render')
    text_enabled = True

    def render(self, context, instance, placeholder):
        """Update the context with plugin's data"""
        context.update(
            {'number_of_entries': instance.number_of_entries,
             'template_to_render': str(instance.template_to_render) or
             'zinnia/tags/random_entries.html'})
        return context

    def icon_src(self, instance):
        """Icon source of the plugin"""
        return settings.STATIC_URL + u'zinnia/img/plugin.png'
        
        
class CMSSearchPlugin(CMSPluginBase):
    model = CMSPlugin
    module = _('entries')
    name = _("Entries search plugin")
    render_template = "zinnia/cms/search.html"

    def render(self, context, instance, placeholder):
        return context

plugin_pool.register_plugin(CMSLatestEntriesPlugin)
plugin_pool.register_plugin(CMSSelectedEntriesPlugin)
plugin_pool.register_plugin(CMSRandomEntriesPlugin)
plugin_pool.register_plugin(CMSSearchPlugin)
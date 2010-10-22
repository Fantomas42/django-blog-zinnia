"""Models of Zinnia CMS Plugins"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from tagging.models import Tag
from cms.models import CMSPlugin

from zinnia.models import Entry
from zinnia.models import Category
from zinnia.plugins.settings import PLUGINS_TEMPLATES

TEMPLATES = [('zinnia/cms/entry_list.html', _('Entry list (default)')),
             ('zinnia/cms/entry_detail.html', _('Entry detailed'))] + PLUGINS_TEMPLATES


class LatestEntriesPlugin(CMSPlugin):
    """CMS Plugin for displaying latest entries"""
    categories = models.ManyToManyField(Category, verbose_name=_('categories'),
                                        blank=True, null=True)
    subcategories = models.BooleanField(default=True, verbose_name=_('include subcategories'))
    authors = models.ManyToManyField(User, verbose_name=_('authors'),
                                     blank=True, null=True)
    tags = models.ManyToManyField(Tag, verbose_name=_('tags'),
                                  blank=True, null=True)

    number_of_entries = models.IntegerField(_('number of entries'), default=5)
    template_to_render = models.CharField(_('template'), blank=True,
                                          max_length=250, choices=TEMPLATES,
                                          help_text=_('Template used to display the plugin'))

    @property
    def render_template(self):
        return self.template_to_render

    def __unicode__(self):
        return _('%s entries') % self.number_of_entries


class SelectedEntriesPlugin(CMSPlugin):
    """CMS Plugin for displaying custom entries"""
    entries = models.ManyToManyField(Entry, verbose_name=_('entries'))
    template_to_render = models.CharField(_('template'), blank=True,
                                          max_length=250, choices=TEMPLATES,
                                          help_text=_('Template used to display the plugin'))

    @property
    def render_template(self):
        return self.template_to_render

    def __unicode__(self):
        return _('%s entries') % self.entries.count()

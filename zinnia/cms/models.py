"""Models of Zinnia CMS Plugins"""
from django.db import models
from cms.models import CMSPlugin
from django.utils.translation import ugettext_lazy as _

from zinnia.models import Entry
from zinnia.models import Category

class LatestEntriesPlugin(CMSPlugin):
    """CMS Plugin for displaying latest entries"""
    category = models.ForeignKey(Category, verbose_name=_('category'),
                                 blank=True, null=True)
    number_of_entries = models.IntegerField(_('number of entries'), default=5)

    def __unicode__(self):
        if self.category:
            return _('The %s latest news of %s') % (self.number_of_entries, self.category.__unicode__())
        else:
            return _('The %s latest news') % self.number_of_entries

class SelectedEntriesPlugin(CMSPlugin):
    """CMS Plugin for displaying custom entries"""
    entries = models.ManyToManyField(Entry, verbose_name=_('entries'))

    def __unicode__(self):
        return _('%s news') % self.entries.count()
    

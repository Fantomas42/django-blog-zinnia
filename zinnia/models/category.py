"""Category model for Zinnia"""
from django.db import models
from django.utils.translation import ugettext_lazy as _

from mptt.models import MPTTModel
from mptt.models import TreeForeignKey
from mptt.managers import TreeManager

from zinnia.managers import entries_published
from zinnia.managers import EntryRelatedPublishedManager


class Category(MPTTModel):
    """Category model for Entry"""

    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(help_text=_('used for publication'),
                            unique=True, max_length=255)
    description = models.TextField(_('description'), blank=True)

    parent = TreeForeignKey('self', null=True, blank=True,
                            verbose_name=_('parent category'),
                            related_name='children')

    objects = TreeManager()
    published = EntryRelatedPublishedManager()

    def entries_published(self):
        """Return only the entries published"""
        return entries_published(self.entries)

    @property
    def tree_path(self):
        """Return category's tree path, by his ancestors"""
        if self.parent_id:
            return '/'.join(
                [ancestor.slug for ancestor in self.get_ancestors()] +
                [self.slug])
        return self.slug

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        """Return category's URL"""
        return ('zinnia_category_detail', (self.tree_path,))

    class Meta:
        """Category's Meta"""
        app_label = 'zinnia'
        ordering = ['title']
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    class MPTTMeta:
        """Category MPTT's Meta"""
        order_insertion_by = ['title']

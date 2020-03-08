"""Category model for Zinnia"""
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from mptt.managers import TreeManager
from mptt.models import MPTTModel
from mptt.models import TreeForeignKey

from zinnia.managers import EntryRelatedPublishedManager
from zinnia.managers import entries_published


class Category(MPTTModel):
    """
    Simple model for categorizing entries.
    """

    title = models.CharField(
        _('title'), max_length=255)

    slug = models.SlugField(
        _('slug'), unique=True, max_length=255,
        help_text=_("Used to build the category's URL."))

    description = models.TextField(
        _('description'), blank=True)

    parent = TreeForeignKey(
        'self',
        related_name='children',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('parent category'))

    objects = TreeManager()
    published = EntryRelatedPublishedManager()

    def entries_published(self):
        """
        Returns category's published entries.
        """
        return entries_published(self.entries)

    @property
    def tree_path(self):
        """
        Returns category's tree path
        by concatening the slug of his ancestors.
        """
        if self.parent_id:
            return '/'.join(
                [ancestor.slug for ancestor in self.get_ancestors()] +
                [self.slug])
        return self.slug

    def get_absolute_url(self):
        """
        Builds and returns the category's URL
        based on his tree path.
        """
        return reverse('zinnia:category_detail', args=(self.tree_path,))

    def __str__(self):
        return self.title

    class Meta:
        """
        Category's meta informations.
        """
        ordering = ['title']
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    class MPTTMeta:
        """
        Category MPTT's meta informations.
        """
        order_insertion_by = ['title']

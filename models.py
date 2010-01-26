"""Models of Zinnia"""
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.template.defaultfilters import linebreaks
from django.utils.translation import ugettext, ugettext_lazy as _

from tagging.fields import TagField

from zinnia.moderator import moderator
from zinnia.moderator import EntryCommentModerator
from zinnia.managers import entries_published
from zinnia.managers import EntryPublishedManager
from zinnia.managers import DRAFT, HIDDEN, PUBLISHED


class Category(models.Model):
    """Category object for Entry"""

    title = models.CharField(_('title'), max_length=50)
    slug = models.SlugField(help_text=_('used for publication'))
    description = models.TextField(_('description'), blank=True)

    def entries_published_set(self):
        """Return only the entries published"""
        return entries_published(self.entry_set)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('zinnia:category_detail', (self.slug, ))

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['title']


class Entry(models.Model):
    """Base design for publishing entry"""
    STATUS_CHOICES = ((DRAFT, _('draft')),
                      (HIDDEN, _('hidden')),
                      (PUBLISHED, _('published')))

    title = models.CharField(_('title'), max_length=100)
    content = models.TextField(_('content'))
    excerpt = models.TextField(_('excerpt'), blank=True,
                                help_text=_('optional element'))

    tags = TagField()
    categories = models.ManyToManyField(Category, verbose_name=_('categories'))

    slug = models.SlugField(help_text=_('used for publication'))
    authors = models.ManyToManyField(User, verbose_name=_('authors'),
                                    blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=DRAFT)
    comment_enabled = models.BooleanField(_('comment enabled'), default=True)

    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)
    last_update = models.DateTimeField(_('last update'), auto_now=True)
    start_publication = models.DateTimeField(_('start publication'),
                                             help_text=_('date start publish'),
                                             default=datetime.now)
    end_publication = models.DateTimeField(_('end publication'),
                                           help_text=_('date end publish'),
                                           default=datetime(2042, 3, 15))

    sites = models.ManyToManyField(Site, verbose_name=_('sites publication'))

    objects = models.Manager()
    published = EntryPublishedManager()

    def get_content(self):
        """Return the content correctly formatted"""
        if not '</p>' in self.content:
            return linebreaks(self.content)
        return self.content

    def get_n_comments(self):
        """Return the number of comments and if enabled"""
        from django.contrib.comments.models import Comment
        return Comment.objects.for_model(self).filter(is_public=True).count()

    def is_actual(self):
        """Define is an entry is between the date of publication"""
        now = datetime.now()
        return now >= self.start_publication and now < self.end_publication
    is_actual.boolean = True
    is_actual.short_description = _('is_actual')

    def is_visible(self):
        """Define if an entry is visible on site"""
        return self.is_actual() and self.status == PUBLISHED
    is_visible.boolean = True
    is_visible.short_description = _('is_visible')

    def __unicode__(self):
        return '%s: %s' % (self.title, self.get_status_display())

    @models.permalink
    def get_absolute_url(self):
        return ('zinnia:entry_detail', (), {
                            'year': self.creation_date.strftime('%Y'),
                            'month': self.creation_date.strftime('%m').lower(),
                            'day': self.creation_date.strftime('%d'),
                            'slug': self.slug})

    class Meta:
        ordering = ['-creation_date']
        verbose_name = _('entry')
        verbose_name_plural = _('entries')
        permissions = (('can_view_all', 'Can view all'),
                       ('can_change_author', 'Can change author'), )

moderator.register(Entry, EntryCommentModerator)

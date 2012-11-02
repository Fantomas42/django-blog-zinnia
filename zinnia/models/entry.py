"""Entry model for Zinnia"""
import warnings

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.html import linebreaks
from django.contrib.sites.models import Site
from django.db.models.signals import post_save
from django.utils.importlib import import_module
from django.contrib import comments
from django.contrib.comments.models import CommentFlag
from django.contrib.comments.moderation import moderator
from django.utils.translation import ugettext_lazy as _

from django.contrib.markup.templatetags.markup import markdown
from django.contrib.markup.templatetags.markup import textile
from django.contrib.markup.templatetags.markup import restructuredtext

from tagging.fields import TagField

from zinnia.models.author import Author
from zinnia.models.category import Category
from zinnia.flags import PINGBACK, TRACKBACK
from zinnia.settings import UPLOAD_TO
from zinnia.settings import MARKUP_LANGUAGE
from zinnia.settings import ENTRY_TEMPLATES
from zinnia.settings import ENTRY_BASE_MODEL
from zinnia.settings import MARKDOWN_EXTENSIONS
from zinnia.settings import AUTO_CLOSE_COMMENTS_AFTER
from zinnia.managers import entries_published
from zinnia.managers import EntryPublishedManager
from zinnia.managers import DRAFT, HIDDEN, PUBLISHED
from zinnia.moderator import EntryCommentModerator
from zinnia.url_shortener import get_url_shortener
from zinnia.signals import ping_directories_handler
from zinnia.signals import ping_external_urls_handler


class EntryAbstractClass(models.Model):
    """Base Model design for publishing entries"""
    STATUS_CHOICES = ((DRAFT, _('draft')),
                      (HIDDEN, _('hidden')),
                      (PUBLISHED, _('published')))

    title = models.CharField(_('title'), max_length=255)

    image = models.ImageField(_('image'), upload_to=UPLOAD_TO,
                              blank=True, help_text=_('used for illustration'))
    content = models.TextField(_('content'))
    excerpt = models.TextField(_('excerpt'), blank=True,
                                help_text=_('optional element'))

    tags = TagField(_('tags'))
    categories = models.ManyToManyField(Category, verbose_name=_('categories'),
                                        related_name='entries',
                                        blank=True, null=True)
    related = models.ManyToManyField('self', verbose_name=_('related entries'),
                                     blank=True, null=True)

    slug = models.SlugField(help_text=_("used to build the entry's URL"),
                            unique_for_date='creation_date',
                            max_length=255)

    authors = models.ManyToManyField(Author, verbose_name=_('authors'),
                                     related_name='entries',
                                     blank=True, null=False)

    status = models.IntegerField(choices=STATUS_CHOICES, default=DRAFT)
    featured = models.BooleanField(_('featured'), default=False)
    comment_enabled = models.BooleanField(_('comment enabled'), default=True)
    pingback_enabled = models.BooleanField(_('linkback enabled'), default=True)

    creation_date = models.DateTimeField(
        _('creation date'), default=timezone.now,
        help_text=_("used to build the entry's URL"))
    last_update = models.DateTimeField(_('last update'), default=timezone.now)
    start_publication = models.DateTimeField(_('start publication'),
                                             blank=True, null=True,
                                             help_text=_('date start publish'))
    end_publication = models.DateTimeField(_('end publication'),
                                           blank=True, null=True,
                                           help_text=_('date end publish'))

    sites = models.ManyToManyField(Site, verbose_name=_('sites publication'),
                                   related_name='entries')

    login_required = models.BooleanField(
        _('login required'), default=False,
        help_text=_('only authenticated users can view the entry'))
    password = models.CharField(
        _('password'), max_length=50, blank=True,
        help_text=_('protect the entry with a password'))

    template = models.CharField(
        _('template'), max_length=250,
        default='entry_detail.html',
        choices=[('entry_detail.html', _('Default template'))] + \
        ENTRY_TEMPLATES,
        help_text=_('template used to display the entry'))

    objects = models.Manager()
    published = EntryPublishedManager()

    @property
    def html_content(self):
        """Return the Entry.content attribute formatted in HTML"""
        if MARKUP_LANGUAGE == 'markdown':
            return markdown(self.content, MARKDOWN_EXTENSIONS)
        elif MARKUP_LANGUAGE == 'textile':
            return textile(self.content)
        elif MARKUP_LANGUAGE == 'restructuredtext':
            return restructuredtext(self.content)
        elif not '</p>' in self.content:
            return linebreaks(self.content)
        return self.content

    @property
    def previous_entry(self):
        """Return the previous entry"""
        entries = Entry.published.filter(
            creation_date__lt=self.creation_date)[:1]
        if entries:
            return entries[0]

    @property
    def next_entry(self):
        """Return the next entry"""
        entries = Entry.published.filter(
            creation_date__gt=self.creation_date).order_by('creation_date')[:1]
        if entries:
            return entries[0]

    @property
    def word_count(self):
        """Count the words of an entry"""
        return len(strip_tags(self.html_content).split())

    @property
    def is_actual(self):
        """Check if an entry is within publication period"""
        now = timezone.now()
        if self.start_publication and now < self.start_publication:
            return False

        if self.end_publication and now >= self.end_publication:
            return False
        return True

    @property
    def is_visible(self):
        """Check if an entry is visible on site"""
        return self.is_actual and self.status == PUBLISHED

    @property
    def related_published(self):
        """Return only related entries published"""
        return entries_published(self.related)

    @property
    def discussions(self):
        """Return published discussions"""
        return comments.get_model().objects.for_model(
            self).filter(is_public=True)

    @property
    def comments(self):
        """Return published comments"""
        return self.discussions.filter(Q(flags=None) | Q(
            flags__flag=CommentFlag.MODERATOR_APPROVAL))

    @property
    def pingbacks(self):
        """Return published pingbacks"""
        return self.discussions.filter(flags__flag=PINGBACK)

    @property
    def trackbacks(self):
        """Return published trackbacks"""
        return self.discussions.filter(flags__flag=TRACKBACK)

    @property
    def comments_are_open(self):
        """Check if comments are open"""
        if AUTO_CLOSE_COMMENTS_AFTER and self.comment_enabled:
            return (timezone.now() - self.start_publication).days < \
                   AUTO_CLOSE_COMMENTS_AFTER
        return self.comment_enabled

    @property
    def short_url(self):
        """Return the entry's short url"""
        return get_url_shortener()(self)

    def __unicode__(self):
        return u'%s: %s' % (self.title, self.get_status_display())

    @models.permalink
    def get_absolute_url(self):
        """Return entry's URL"""
        creation_date = timezone.localtime(self.creation_date)
        return ('zinnia_entry_detail', (), {
            'year': creation_date.strftime('%Y'),
            'month': creation_date.strftime('%m'),
            'day': creation_date.strftime('%d'),
            'slug': self.slug})

    class Meta:
        """Entry's Meta"""
        abstract = True
        app_label = 'zinnia'
        ordering = ['-creation_date']
        get_latest_by = 'creation_date'
        verbose_name = _('entry')
        verbose_name_plural = _('entries')
        permissions = (('can_view_all', 'Can view all entries'),
                       ('can_change_status', 'Can change status'),
                       ('can_change_author', 'Can change author(s)'), )


def get_base_model():
    """Determine the base Model to inherit in the
    Entry Model, this allow to overload it."""
    if not ENTRY_BASE_MODEL:
        return EntryAbstractClass

    dot = ENTRY_BASE_MODEL.rindex('.')
    module_name = ENTRY_BASE_MODEL[:dot]
    class_name = ENTRY_BASE_MODEL[dot + 1:]
    try:
        _class = getattr(import_module(module_name), class_name)
        return _class
    except (ImportError, AttributeError):
        warnings.warn('%s cannot be imported' % ENTRY_BASE_MODEL,
                      RuntimeWarning)
    return EntryAbstractClass


class Entry(get_base_model()):
    """
    The final Entry model based on inheritence.
    Check this out for customizing the Entry Model class:
    http://django-blog-zinnia.rtfd.org/extending-entry
    """


moderator.register(Entry, EntryCommentModerator)
post_save.connect(ping_directories_handler, sender=Entry,
                  dispatch_uid='zinnia.entry.post_save.ping_directories')
post_save.connect(ping_external_urls_handler, sender=Entry,
                  dispatch_uid='zinnia.entry.post_save.ping_external_urls')

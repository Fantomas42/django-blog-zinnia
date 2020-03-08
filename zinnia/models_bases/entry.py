"""Base entry models for Zinnia"""
import os

from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _

import django_comments as comments
from django_comments.models import CommentFlag

from tagging.fields import TagField
from tagging.utils import parse_tag_input

from zinnia.flags import PINGBACK
from zinnia.flags import TRACKBACK
from zinnia.managers import DRAFT, HIDDEN, PUBLISHED
from zinnia.managers import EntryPublishedManager
from zinnia.managers import entries_published
from zinnia.markups import html_format
from zinnia.preview import HTMLPreview
from zinnia.settings import AUTO_CLOSE_COMMENTS_AFTER
from zinnia.settings import AUTO_CLOSE_PINGBACKS_AFTER
from zinnia.settings import AUTO_CLOSE_TRACKBACKS_AFTER
from zinnia.settings import ENTRY_CONTENT_TEMPLATES
from zinnia.settings import ENTRY_DETAIL_TEMPLATES
from zinnia.settings import UPLOAD_TO
from zinnia.url_shortener import get_url_shortener


class CoreEntry(models.Model):
    """
    Abstract core entry model class providing
    the fields and methods required for publishing
    content over time.
    """
    STATUS_CHOICES = ((DRAFT, _('draft')),
                      (HIDDEN, _('hidden')),
                      (PUBLISHED, _('published')))

    title = models.CharField(
        _('title'), max_length=255)

    slug = models.SlugField(
        _('slug'), max_length=255,
        unique_for_date='publication_date',
        help_text=_("Used to build the entry's URL."))

    status = models.IntegerField(
        _('status'), db_index=True,
        choices=STATUS_CHOICES, default=DRAFT)

    publication_date = models.DateTimeField(
        _('publication date'),
        db_index=True, default=timezone.now,
        help_text=_("Used to build the entry's URL."))

    start_publication = models.DateTimeField(
        _('start publication'),
        db_index=True, blank=True, null=True,
        help_text=_('Start date of publication.'))

    end_publication = models.DateTimeField(
        _('end publication'),
        db_index=True, blank=True, null=True,
        help_text=_('End date of publication.'))

    sites = models.ManyToManyField(
        Site,
        related_name='entries',
        verbose_name=_('sites'),
        help_text=_('Sites where the entry will be published.'))

    creation_date = models.DateTimeField(
        _('creation date'),
        default=timezone.now)

    last_update = models.DateTimeField(
        _('last update'), default=timezone.now)

    objects = models.Manager()
    published = EntryPublishedManager()

    @property
    def is_actual(self):
        """
        Checks if an entry is within his publication period.
        """
        now = timezone.now()
        if self.start_publication and now < self.start_publication:
            return False

        if self.end_publication and now >= self.end_publication:
            return False
        return True

    @property
    def is_visible(self):
        """
        Checks if an entry is visible and published.
        """
        return self.is_actual and self.status == PUBLISHED

    @property
    def previous_entry(self):
        """
        Returns the previous published entry if exists.
        """
        return self.previous_next_entries[0]

    @property
    def next_entry(self):
        """
        Returns the next published entry if exists.
        """
        return self.previous_next_entries[1]

    @property
    def previous_next_entries(self):
        """
        Returns and caches a tuple containing the next
        and previous published entries.
        Only available if the entry instance is published.
        """
        previous_next = getattr(self, 'previous_next', None)

        if previous_next is None:
            if not self.is_visible:
                previous_next = (None, None)
                setattr(self, 'previous_next', previous_next)
                return previous_next

            entries = list(self.__class__.published.all())
            index = entries.index(self)
            try:
                previous = entries[index + 1]
            except IndexError:
                previous = None

            if index:
                _next = entries[index - 1]
            else:
                _next = None
            previous_next = (previous, _next)
            setattr(self, 'previous_next', previous_next)
        return previous_next

    @property
    def short_url(self):
        """
        Returns the entry's short url.
        """
        return get_url_shortener()(self)

    def save(self, *args, **kwargs):
        """
        Overrides the save method to update the
        the last_update field.
        """
        self.last_update = timezone.now()
        super(CoreEntry, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Builds and returns the entry's URL based on
        the slug and the creation date.
        """
        publication_date = self.publication_date
        if timezone.is_aware(publication_date):
            publication_date = timezone.localtime(publication_date)
        return reverse('zinnia:entry_detail', kwargs={
            'year': publication_date.strftime('%Y'),
            'month': publication_date.strftime('%m'),
            'day': publication_date.strftime('%d'),
            'slug': self.slug})

    def __str__(self):
        return '%s: %s' % (self.title, self.get_status_display())

    class Meta:
        """
        CoreEntry's meta informations.
        """
        abstract = True
        ordering = ['-publication_date']
        get_latest_by = 'publication_date'
        verbose_name = _('entry')
        verbose_name_plural = _('entries')
        index_together = [['slug', 'publication_date'],
                          ['status', 'publication_date',
                           'start_publication', 'end_publication']]
        permissions = (('can_view_all', 'Can view all entries'),
                       ('can_change_status', 'Can change status'),
                       ('can_change_author', 'Can change author(s)'), )


class ContentEntry(models.Model):
    """
    Abstract content model class providing field
    and methods to write content inside an entry.
    """
    content = models.TextField(_('content'), blank=True)

    @property
    def html_content(self):
        """
        Returns the "content" field formatted in HTML.
        """
        return html_format(self.content)

    @property
    def html_preview(self):
        """
        Returns a preview of the "content" field or
        the "lead" field if defined, formatted in HTML.
        """
        return HTMLPreview(self.html_content,
                           getattr(self, 'html_lead', ''))

    @property
    def word_count(self):
        """
        Counts the number of words used in the content.
        """
        return len(strip_tags(self.html_content).split())

    class Meta:
        abstract = True


class DiscussionsEntry(models.Model):
    """
    Abstract discussion model class providing
    the fields and methods to manage the discussions
    (comments, pingbacks, trackbacks).
    """
    comment_enabled = models.BooleanField(
        _('comments enabled'), default=True,
        help_text=_('Allows comments if checked.'))
    pingback_enabled = models.BooleanField(
        _('pingbacks enabled'), default=True,
        help_text=_('Allows pingbacks if checked.'))
    trackback_enabled = models.BooleanField(
        _('trackbacks enabled'), default=True,
        help_text=_('Allows trackbacks if checked.'))

    comment_count = models.IntegerField(
        _('comment count'), default=0)
    pingback_count = models.IntegerField(
        _('pingback count'), default=0)
    trackback_count = models.IntegerField(
        _('trackback count'), default=0)

    @property
    def discussions(self):
        """
        Returns a queryset of the published discussions.
        """
        return comments.get_model().objects.for_model(
            self).filter(is_public=True, is_removed=False)

    @property
    def comments(self):
        """
        Returns a queryset of the published comments.
        """
        return self.discussions.filter(Q(flags=None) | Q(
            flags__flag=CommentFlag.MODERATOR_APPROVAL))

    @property
    def pingbacks(self):
        """
        Returns a queryset of the published pingbacks.
        """
        return self.discussions.filter(flags__flag=PINGBACK)

    @property
    def trackbacks(self):
        """
        Return a queryset of the published trackbacks.
        """
        return self.discussions.filter(flags__flag=TRACKBACK)

    def discussion_is_still_open(self, discussion_type, auto_close_after):
        """
        Checks if a type of discussion is still open
        are a certain number of days.
        """
        discussion_enabled = getattr(self, discussion_type)
        if (discussion_enabled and isinstance(auto_close_after, int) and
                auto_close_after >= 0):
            return (timezone.now() - (
                self.start_publication or self.publication_date)).days < \
                auto_close_after
        return discussion_enabled

    @property
    def comments_are_open(self):
        """
        Checks if the comments are open with the
        AUTO_CLOSE_COMMENTS_AFTER setting.
        """
        return self.discussion_is_still_open(
            'comment_enabled', AUTO_CLOSE_COMMENTS_AFTER)

    @property
    def pingbacks_are_open(self):
        """
        Checks if the pingbacks are open with the
        AUTO_CLOSE_PINGBACKS_AFTER setting.
        """
        return self.discussion_is_still_open(
            'pingback_enabled', AUTO_CLOSE_PINGBACKS_AFTER)

    @property
    def trackbacks_are_open(self):
        """
        Checks if the trackbacks are open with the
        AUTO_CLOSE_TRACKBACKS_AFTER setting.
        """
        return self.discussion_is_still_open(
            'trackback_enabled', AUTO_CLOSE_TRACKBACKS_AFTER)

    class Meta:
        abstract = True


class RelatedEntry(models.Model):
    """
    Abstract model class for making manual relations
    between the differents entries.
    """
    related = models.ManyToManyField(
        'self',
        blank=True,
        verbose_name=_('related entries'))

    @property
    def related_published(self):
        """
        Returns only related entries published.
        """
        return entries_published(self.related)

    class Meta:
        abstract = True


class LeadEntry(models.Model):
    """
    Abstract model class providing a lead content to the entries.
    """
    lead = models.TextField(
        _('lead'), blank=True,
        help_text=_('Lead paragraph'))

    @property
    def html_lead(self):
        """
        Returns the "lead" field formatted in HTML.
        """
        return html_format(self.lead)

    class Meta:
        abstract = True


class ExcerptEntry(models.Model):
    """
    Abstract model class to add an excerpt to the entries.
    """
    excerpt = models.TextField(
        _('excerpt'), blank=True,
        help_text=_('Used for SEO purposes.'))

    def save(self, *args, **kwargs):
        """
        Overrides the save method to create an excerpt
        from the content field if void.
        """
        if not self.excerpt and self.status == PUBLISHED:
            self.excerpt = Truncator(strip_tags(
                getattr(self, 'content', ''))).words(50)
        super(ExcerptEntry, self).save(*args, **kwargs)

    class Meta:
        abstract = True


def image_upload_to_dispatcher(entry, filename):
    """
    Dispatch function to allow overriding of ``image_upload_to`` method.

    Outside the model for fixing an issue with Django's migrations on Python 2.
    """
    return entry.image_upload_to(filename)


class ImageEntry(models.Model):
    """
    Abstract model class to add an image for illustrating the entries.
    """

    def image_upload_to(self, filename):
        """
        Compute the upload path for the image field.
        """
        now = timezone.now()
        filename, extension = os.path.splitext(filename)

        return os.path.join(
            UPLOAD_TO,
            now.strftime('%Y'),
            now.strftime('%m'),
            now.strftime('%d'),
            '%s%s' % (slugify(filename), extension))

    image = models.ImageField(
        _('image'), blank=True,
        upload_to=image_upload_to_dispatcher,
        help_text=_('Used for illustration.'))

    image_caption = models.TextField(
        _('caption'), blank=True,
        help_text=_("Image's caption."))

    class Meta:
        abstract = True


class FeaturedEntry(models.Model):
    """
    Abstract model class to mark entries as featured.
    """
    featured = models.BooleanField(
        _('featured'), default=False)

    class Meta:
        abstract = True


class AuthorsEntry(models.Model):
    """
    Abstract model class to add relationship
    between the entries and their authors.
    """
    authors = models.ManyToManyField(
        'zinnia.Author',
        blank=True,
        related_name='entries',
        verbose_name=_('authors'))

    class Meta:
        abstract = True


class CategoriesEntry(models.Model):
    """
    Abstract model class to categorize the entries.
    """
    categories = models.ManyToManyField(
        'zinnia.Category',
        blank=True,
        related_name='entries',
        verbose_name=_('categories'))

    class Meta:
        abstract = True


class TagsEntry(models.Model):
    """
    Abstract model class to add tags to the entries.
    """
    tags = TagField(_('tags'))

    @property
    def tags_list(self):
        """
        Return iterable list of tags.
        """
        return parse_tag_input(self.tags)

    class Meta:
        abstract = True


class LoginRequiredEntry(models.Model):
    """
    Abstract model class to restrcit the display
    of the entry on authenticated users.
    """
    login_required = models.BooleanField(
        _('login required'), default=False,
        help_text=_('Only authenticated users can view the entry.'))

    class Meta:
        abstract = True


class PasswordRequiredEntry(models.Model):
    """
    Abstract model class to restrict the display
    of the entry to users knowing the password.
    """
    password = models.CharField(
        _('password'), max_length=50, blank=True,
        help_text=_('Protects the entry with a password.'))

    class Meta:
        abstract = True


class ContentTemplateEntry(models.Model):
    """
    Abstract model class to display entry's content
    with a custom template.
    """
    content_template = models.CharField(
        _('content template'), max_length=250,
        default='zinnia/_entry_detail.html',
        choices=[('zinnia/_entry_detail.html', _('Default template'))] +
        ENTRY_CONTENT_TEMPLATES,
        help_text=_("Template used to display the entry's content."))

    class Meta:
        abstract = True


class DetailTemplateEntry(models.Model):
    """
    Abstract model class to display entries with a
    custom template if needed on the detail page.
    """
    detail_template = models.CharField(
        _('detail template'), max_length=250,
        default='entry_detail.html',
        choices=[('entry_detail.html', _('Default template'))] +
        ENTRY_DETAIL_TEMPLATES,
        help_text=_("Template used to display the entry's detail page."))

    class Meta:
        abstract = True


class AbstractEntry(
        CoreEntry,
        ContentEntry,
        DiscussionsEntry,
        RelatedEntry,
        LeadEntry,
        ExcerptEntry,
        ImageEntry,
        FeaturedEntry,
        AuthorsEntry,
        CategoriesEntry,
        TagsEntry,
        LoginRequiredEntry,
        PasswordRequiredEntry,
        ContentTemplateEntry,
        DetailTemplateEntry):
    """
    Final abstract entry model class assembling
    all the abstract entry model classes into a single one.

    In this manner we can override some fields without
    reimplemting all the AbstractEntry.
    """

    class Meta(CoreEntry.Meta):
        abstract = True

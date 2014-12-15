"""EntryAdmin for Zinnia"""
from django.forms import Media
from django.contrib import admin
from django.db.models import Q
from django.conf.urls import url
from django.conf.urls import patterns
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.html import strip_tags
from django.core.urlresolvers import reverse
from django.core.urlresolvers import NoReverseMatch
from django.template.response import TemplateResponse
from django.utils.translation import ungettext_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.contrib.staticfiles.storage import staticfiles_storage

from zinnia import settings
from zinnia.managers import HIDDEN
from zinnia.managers import PUBLISHED
from zinnia.settings import PROTOCOL
from zinnia.models.author import Author
from zinnia.ping import DirectoryPinger
from zinnia.admin.forms import EntryAdminForm
from zinnia.admin.filters import AuthorListFilter
from zinnia.admin.filters import CategoryListFilter


class EntryAdmin(admin.ModelAdmin):
    """
    Admin for Entry model.
    """
    form = EntryAdminForm
    date_hierarchy = 'creation_date'
    fieldsets = (
        (_('Content'), {
            'fields': (('title', 'status'), 'content', 'image')}),
        (_('Publication'), {
            'fields': (('start_publication', 'end_publication'),
                       'creation_date', 'sites'),
            'classes': ('collapse', 'collapse-closed')}),
        (_('Discussions'), {
            'fields': ('comment_enabled', 'pingback_enabled',
                       'trackback_enabled'),
            'classes': ('collapse', 'collapse-closed')}),
        (_('Privacy'), {
            'fields': ('login_required', 'password'),
            'classes': ('collapse', 'collapse-closed')}),
        (_('Templates'), {
            'fields': ('content_template', 'detail_template'),
            'classes': ('collapse', 'collapse-closed')}),
        (_('Metadatas'), {
            'fields': ('featured', 'excerpt', 'authors', 'related'),
            'classes': ('collapse', 'collapse-closed')}),
        (None, {'fields': ('categories', 'tags', 'slug')}))
    list_filter = (CategoryListFilter, AuthorListFilter, 'status', 'featured',
                   'login_required', 'comment_enabled', 'pingback_enabled',
                   'trackback_enabled', 'creation_date', 'start_publication',
                   'end_publication', 'sites')
    list_display = ('get_title', 'get_authors', 'get_categories',
                    'get_tags', 'get_sites', 'get_is_visible', 'featured',
                    'get_short_url', 'creation_date')
    radio_fields = {'content_template': admin.VERTICAL,
                    'detail_template': admin.VERTICAL}
    filter_horizontal = ('categories', 'authors', 'related')
    prepopulated_fields = {'slug': ('title', )}
    search_fields = ('title', 'excerpt', 'content', 'tags')
    actions = ['make_mine', 'make_published', 'make_hidden',
               'close_comments', 'close_pingbacks', 'close_trackbacks',
               'ping_directories', 'put_on_top',
               'mark_featured', 'unmark_featured']
    actions_on_top = True
    actions_on_bottom = True

    def __init__(self, model, admin_site):
        self.form.admin_site = admin_site
        super(EntryAdmin, self).__init__(model, admin_site)

    # Custom Display
    def get_title(self, entry):
        """
        Return the title with word count and number of comments.
        """
        title = _('%(title)s (%(word_count)i words)') % \
            {'title': entry.title, 'word_count': entry.word_count}
        reaction_count = int(entry.comment_count +
                             entry.pingback_count +
                             entry.trackback_count)
        if reaction_count:
            return ungettext_lazy(
                '%(title)s (%(reactions)i reaction)',
                '%(title)s (%(reactions)i reactions)', reaction_count) % \
                {'title': title,
                 'reactions': reaction_count}
        return title
    get_title.short_description = _('title')

    def get_authors(self, entry):
        """
        Return the authors in HTML.
        """
        try:
            authors = ['<a href="%s" target="blank">%s</a>' %
                       (author.get_absolute_url(),
                        getattr(author, author.USERNAME_FIELD))
                       for author in entry.authors.all()]
        except NoReverseMatch:
            authors = [getattr(author, author.USERNAME_FIELD)
                       for author in entry.authors.all()]
        return ', '.join(authors)
    get_authors.allow_tags = True
    get_authors.short_description = _('author(s)')

    def get_categories(self, entry):
        """
        Return the categories linked in HTML.
        """
        try:
            categories = ['<a href="%s" target="blank">%s</a>' %
                          (category.get_absolute_url(), category.title)
                          for category in entry.categories.all()]
        except NoReverseMatch:
            categories = [category.title for category in
                          entry.categories.all()]
        return ', '.join(categories)
    get_categories.allow_tags = True
    get_categories.short_description = _('category(s)')

    def get_tags(self, entry):
        """
        Return the tags linked in HTML.
        """
        try:
            return ', '.join(['<a href="%s" target="blank">%s</a>' %
                              (reverse('zinnia:tag_detail', args=[tag]), tag)
                              for tag in entry.tags_list])
        except NoReverseMatch:
            return entry.tags
    get_tags.allow_tags = True
    get_tags.short_description = _('tag(s)')

    def get_sites(self, entry):
        """
        Return the sites linked in HTML.
        """
        try:
            index_url = reverse('zinnia:entry_archive_index')
        except NoReverseMatch:
            index_url = ''
        return ', '.join(
            ['<a href="%s://%s%s" target="blank">%s</a>' %
             (PROTOCOL, site.domain, index_url, site.name)
             for site in entry.sites.all()])
    get_sites.allow_tags = True
    get_sites.short_description = _('site(s)')

    def get_short_url(self, entry):
        """
        Return the short url in HTML.
        """
        try:
            short_url = entry.short_url
        except NoReverseMatch:
            short_url = entry.get_absolute_url()
        return '<a href="%(url)s" target="blank">%(url)s</a>' % \
               {'url': short_url}
    get_short_url.allow_tags = True
    get_short_url.short_description = _('short url')

    def get_is_visible(self, entry):
        """
        Admin wrapper for entry.is_visible.
        """
        return entry.is_visible
    get_is_visible.boolean = True
    get_is_visible.short_description = _('is visible')

    # Custom Methods
    def save_model(self, request, entry, form, change):
        """
        Save the authors, update time, make an excerpt.
        """
        if not entry.excerpt and entry.status == PUBLISHED:
            entry.excerpt = Truncator(strip_tags(entry.content)).words(50)

        entry.last_update = timezone.now()
        entry.save()

    def get_queryset(self, request):
        """
        Make special filtering by user's permissions.
        """
        if not request.user.has_perm('zinnia.can_view_all'):
            queryset = self.model.objects.filter(authors__pk=request.user.pk)
        else:
            queryset = super(EntryAdmin, self).get_queryset(request)
        return queryset.prefetch_related('categories', 'authors', 'sites')

    def get_changeform_initial_data(self, request):
        """
        Provide initial datas when creating an entry.
        """
        get_data = super(EntryAdmin, self).get_changeform_initial_data(request)
        return get_data or {
            'sites': [Site.objects.get_current()],
            'authors': Author.objects.filter(pk=request.user.pk)
        }

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Filter the disposable authors.
        """
        if db_field.name == 'authors':
            kwargs['queryset'] = Author.objects.filter(
                Q(is_staff=True) | Q(entries__isnull=False)
                ).distinct()

        return super(EntryAdmin, self).formfield_for_manytomany(
            db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        """
        Return readonly fields by user's permissions.
        """
        readonly_fields = list(super(EntryAdmin, self).get_readonly_fields(
            request, obj))

        if not request.user.has_perm('zinnia.can_change_status'):
            readonly_fields.append('status')

        if not request.user.has_perm('zinnia.can_change_author'):
            readonly_fields.append('authors')

        return readonly_fields

    def get_actions(self, request):
        """
        Define actions by user's permissions.
        """
        actions = super(EntryAdmin, self).get_actions(request)
        if not actions:
            return actions
        if (not request.user.has_perm('zinnia.can_change_author') or
                not request.user.has_perm('zinnia.can_view_all')):
            del actions['make_mine']
        if not request.user.has_perm('zinnia.can_change_status'):
            del actions['make_hidden']
            del actions['make_published']
        if not settings.PING_DIRECTORIES:
            del actions['ping_directories']

        return actions

    # Custom Actions
    def make_mine(self, request, queryset):
        """
        Set the entries to the current user.
        """
        author = Author.objects.get(pk=request.user.pk)
        for entry in queryset:
            if author not in entry.authors.all():
                entry.authors.add(author)
        self.message_user(
            request, _('The selected entries now belong to you.'))
    make_mine.short_description = _('Set the entries to the user')

    def make_published(self, request, queryset):
        """
        Set entries selected as published.
        """
        queryset.update(status=PUBLISHED)
        self.ping_directories(request, queryset, messages=False)
        self.message_user(
            request, _('The selected entries are now marked as published.'))
    make_published.short_description = _('Set entries selected as published')

    def make_hidden(self, request, queryset):
        """
        Set entries selected as hidden.
        """
        queryset.update(status=HIDDEN)
        self.message_user(
            request, _('The selected entries are now marked as hidden.'))
    make_hidden.short_description = _('Set entries selected as hidden')

    def close_comments(self, request, queryset):
        """
        Close the comments for selected entries.
        """
        queryset.update(comment_enabled=False)
        self.message_user(
            request, _('Comments are now closed for selected entries.'))
    close_comments.short_description = _('Close the comments for '
                                         'selected entries')

    def close_pingbacks(self, request, queryset):
        """
        Close the pingbacks for selected entries.
        """
        queryset.update(pingback_enabled=False)
        self.message_user(
            request, _('Pingbacks are now closed for selected entries.'))
    close_pingbacks.short_description = _(
        'Close the pingbacks for selected entries')

    def close_trackbacks(self, request, queryset):
        """
        Close the trackbacks for selected entries.
        """
        queryset.update(trackback_enabled=False)
        self.message_user(
            request, _('Trackbacks are now closed for selected entries.'))
    close_trackbacks.short_description = _(
        'Close the trackbacks for selected entries')

    def put_on_top(self, request, queryset):
        """
        Put the selected entries on top at the current date.
        """
        queryset.update(creation_date=timezone.now())
        self.ping_directories(request, queryset, messages=False)
        self.message_user(request, _(
            'The selected entries are now set at the current date.'))
    put_on_top.short_description = _(
        'Put the selected entries on top at the current date')

    def mark_featured(self, request, queryset):
        """
        Mark selected as featured post.
        """
        queryset.update(featured=True)
        self.message_user(
            request, _('Selected entries are now marked as featured.'))
    mark_featured.short_description = _('Mark selected entries as featured')

    def unmark_featured(self, request, queryset):
        """
        Un-Mark selected featured posts.
        """
        queryset.update(featured=False)
        self.message_user(
            request, _('Selected entries are no longer marked as featured.'))
    unmark_featured.short_description = _(
        'Unmark selected entries as featured')

    def ping_directories(self, request, queryset, messages=True):
        """
        Ping web directories for selected entries.
        """
        for directory in settings.PING_DIRECTORIES:
            pinger = DirectoryPinger(directory, queryset)
            pinger.join()
            if messages:
                success = 0
                for result in pinger.results:
                    if not result.get('flerror', True):
                        success += 1
                    else:
                        self.message_user(request,
                                          '%s : %s' % (directory,
                                                       result['message']))
                if success:
                    self.message_user(
                        request,
                        _('%(directory)s directory succesfully '
                          'pinged %(success)d entries.') %
                        {'directory': directory, 'success': success})
    ping_directories.short_description = _(
        'Ping Directories for selected entries')

    def get_urls(self):
        """
        Overload the admin's urls for tag auto-completion.
        """
        entry_admin_urls = super(EntryAdmin, self).get_urls()
        urls = patterns(
            '',
            url(r'^autocomplete_tags/$',
                self.admin_site.admin_view(self.autocomplete_tags),
                name='zinnia_entry_autocomplete_tags'),
        )
        return urls + entry_admin_urls

    def autocomplete_tags(self, request):
        """
        View for tag auto-completion.
        """
        return TemplateResponse(
            request, 'admin/zinnia/entry/autocomplete_tags.js',
            content_type='application/javascript')

    def _media(self):
        """
        The medias needed to enhance the admin page.
        """
        def static_url(url):
            return staticfiles_storage.url('zinnia/%s' % url)

        media = super(EntryAdmin, self).media + Media(
            css={'all': (
                static_url('css/jquery.autocomplete.css'),)},
            js=(static_url('js/jquery.js'),
                static_url('js/jquery.bgiframe.js'),
                static_url('js/jquery.autocomplete.js'),
                reverse('admin:zinnia_entry_autocomplete_tags')))

        return media
    media = property(_media)

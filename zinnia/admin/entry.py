"""EntryAdmin for Zinnia"""
from django.forms import Media
from django.contrib import admin
from django.conf.urls import url
from django.conf.urls import patterns
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.html import strip_tags
from django.core.urlresolvers import reverse
from django.core.urlresolvers import NoReverseMatch
from django.conf import settings as project_settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import get_language
from django.template.response import TemplateResponse
from django.utils.translation import ungettext_lazy
from django.utils.translation import ugettext_lazy as _

from zinnia import settings
from zinnia.managers import HIDDEN
from zinnia.managers import PUBLISHED
from zinnia.models.author import Author
from zinnia.ping import DirectoryPinger
from zinnia.admin.forms import EntryAdminForm
from zinnia.admin.filters import AuthorListFilter
from zinnia.admin.filters import CategoryListFilter


class EntryAdmin(admin.ModelAdmin):
    """Admin for Entry model"""
    form = EntryAdminForm
    date_hierarchy = 'creation_date'
    fieldsets = ((_('Content'), {'fields': ('title', 'content',
                                            'image', 'status')}),
                 (_('Options'), {'fields': ('featured', 'excerpt',
                                            'content_template',
                                            'detail_template',
                                            'related', 'authors',
                                            'creation_date',
                                            'start_publication',
                                            'end_publication'),
                                 'classes': ('collapse', 'collapse-closed')}),
                 (_('Privacy'), {'fields': ('password', 'login_required',),
                                 'classes': ('collapse', 'collapse-closed')}),
                 (_('Discussions'), {'fields': ('comment_enabled',
                                                'pingback_enabled',
                                                'trackback_enabled'),
                                     'classes': ('collapse',
                                                 'collapse-closed')}),
                 (_('Publication'), {'fields': ('categories', 'tags',
                                                'sites', 'slug')}))
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
               'ping_directories', 'make_tweet', 'put_on_top',
               'mark_featured', 'unmark_featured']
    actions_on_top = True
    actions_on_bottom = True

    def __init__(self, model, admin_site):
        self.form.admin_site = admin_site
        super(EntryAdmin, self).__init__(model, admin_site)

    # Custom Display
    def get_title(self, entry):
        """Return the title with word count and number of comments"""
        title = _('%(title)s (%(word_count)i words)') % \
            {'title': entry.title, 'word_count': entry.word_count}
        reaction_count = (entry.comment_count +
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
        """Return the authors in HTML"""
        try:
            authors = ['<a href="%s" target="blank">%s</a>' %
                       (reverse('zinnia_author_detail',
                                args=[author.username]),
                        author.username) for author in entry.authors.all()]
        except NoReverseMatch:
            authors = [author.username for author in entry.authors.all()]
        return ', '.join(authors)
    get_authors.allow_tags = True
    get_authors.short_description = _('author(s)')

    def get_categories(self, entry):
        """Return the categories linked in HTML"""
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
        """Return the tags linked in HTML"""
        try:
            return ', '.join(['<a href="%s" target="blank">%s</a>' %
                              (reverse('zinnia_tag_detail', args=[tag]), tag)
                              for tag in entry.tags_list])
        except NoReverseMatch:
            return entry.tags
    get_tags.allow_tags = True
    get_tags.short_description = _('tag(s)')

    def get_sites(self, entry):
        """Return the sites linked in HTML"""
        return ', '.join(
            ['<a href="http://%(domain)s" target="blank">%(name)s</a>' %
             site.__dict__ for site in entry.sites.all()])
    get_sites.allow_tags = True
    get_sites.short_description = _('site(s)')

    def get_is_visible(self, entry):
        """Admin wrapper for entry.is_visible"""
        return entry.is_visible
    get_is_visible.boolean = True
    get_is_visible.short_description = _('is visible')

    def get_short_url(self, entry):
        """Return the short url in HTML"""
        return '<a href="%(url)s" target="blank">%(url)s</a>' % \
               {'url': entry.short_url}
    get_short_url.allow_tags = True
    get_short_url.short_description = _('short url')

    # Custom Methods
    def save_model(self, request, entry, form, change):
        """Save the authors, update time, make an excerpt"""
        if not entry.excerpt and entry.status == PUBLISHED:
            entry.excerpt = Truncator(strip_tags(entry.content)).words(50)

        if entry.pk and not request.user.has_perm('zinnia.can_change_author'):
            form.cleaned_data['authors'] = entry.authors.all()

        if not form.cleaned_data.get('authors'):
            form.cleaned_data['authors'] = Author.objects.filter(
                pk=request.user.pk)

        entry.last_update = timezone.now()
        entry.save()

    def queryset(self, request):
        """Make special filtering by user permissions"""
        if not request.user.has_perm('zinnia.can_view_all'):
            queryset = request.user.entries.all()
        else:
            queryset = super(EntryAdmin, self).queryset(request)
        return queryset.prefetch_related('categories', 'authors', 'sites')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Filters the disposable authors"""
        if db_field.name == 'authors':
            if request.user.has_perm('zinnia.can_change_author'):
                kwargs['queryset'] = Author.objects.filter(is_staff=True)
            else:
                kwargs['queryset'] = Author.objects.filter(pk=request.user.pk)

        return super(EntryAdmin, self).formfield_for_manytomany(
            db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(EntryAdmin, self).get_readonly_fields(
            request, obj)
        if not request.user.has_perm('zinnia.can_change_status'):
            readonly_fields = list(readonly_fields)
            readonly_fields.append('status')
        return readonly_fields

    def get_actions(self, request):
        """Define user actions by permissions"""
        actions = super(EntryAdmin, self).get_actions(request)
        if (not request.user.has_perm('zinnia.can_change_author') or
                not request.user.has_perm('zinnia.can_view_all')):
            del actions['make_mine']
        if not request.user.has_perm('zinnia.can_change_status'):
            del actions['make_hidden']
            del actions['make_published']
        if not settings.PING_DIRECTORIES:
            del actions['ping_directories']
        if not settings.USE_TWITTER:
            del actions['make_tweet']

        return actions

    # Custom Actions
    def make_mine(self, request, queryset):
        """Set the entries to the user"""
        for entry in queryset:
            if request.user not in entry.authors.all():
                entry.authors.add(request.user)
        self.message_user(
            request, _('The selected entries now belong to you.'))
    make_mine.short_description = _('Set the entries to the user')

    def make_published(self, request, queryset):
        """Set entries selected as published"""
        queryset.update(status=PUBLISHED)
        self.ping_directories(request, queryset, messages=False)
        self.message_user(
            request, _('The selected entries are now marked as published.'))
    make_published.short_description = _('Set entries selected as published')

    def make_hidden(self, request, queryset):
        """Set entries selected as hidden"""
        queryset.update(status=HIDDEN)
        self.message_user(
            request, _('The selected entries are now marked as hidden.'))
    make_hidden.short_description = _('Set entries selected as hidden')

    def make_tweet(self, request, queryset):
        """Post an update on Twitter"""
        import tweepy
        auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY,
                                   settings.TWITTER_CONSUMER_SECRET)
        auth.set_access_token(settings.TWITTER_ACCESS_KEY,
                              settings.TWITTER_ACCESS_SECRET)
        api = tweepy.API(auth)
        for entry in queryset:
            short_url = entry.short_url
            message = '%s %s' % (entry.title[:139 - len(short_url)], short_url)
            api.update_status(message)
        self.message_user(
            request, _('The selected entries have been tweeted.'))
    make_tweet.short_description = _('Tweet entries selected')

    def close_comments(self, request, queryset):
        """Close the comments for selected entries"""
        queryset.update(comment_enabled=False)
        self.message_user(
            request, _('Comments are now closed for selected entries.'))
    close_comments.short_description = _('Close the comments for '
                                         'selected entries')

    def close_pingbacks(self, request, queryset):
        """Close the pingbacks for selected entries"""
        queryset.update(pingback_enabled=False)
        self.message_user(
            request, _('Pingbacks are now closed for selected entries.'))
    close_pingbacks.short_description = _(
        'Close the pingbacks for selected entries')

    def close_trackbacks(self, request, queryset):
        """Close the trackbacks for selected entries"""
        queryset.update(trackback_enabled=False)
        self.message_user(
            request, _('Trackbacks are now closed for selected entries.'))
    close_trackbacks.short_description = _(
        'Close the trackbacks for selected entries')

    def put_on_top(self, request, queryset):
        """Put the selected entries on top at the current date"""
        queryset.update(creation_date=timezone.now())
        self.ping_directories(request, queryset, messages=False)
        self.message_user(request, _(
            'The selected entries are now set at the current date.'))
    put_on_top.short_description = _(
        'Put the selected entries on top at the current date')

    def ping_directories(self, request, queryset, messages=True):
        """Ping Directories for selected entries"""
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

    def mark_featured(self, request, queryset):
        """Mark selected as featured post."""
        queryset.update(featured=True)
        self.message_user(
            request, _('Selected entries are now marked as featured.'))
    mark_featured.short_description = _('Mark selected entries as featured')

    def unmark_featured(self, request, queryset):
        """Un-Mark selected featured posts"""
        queryset.update(featured=False)
        self.message_user(
            request, _('Selected entries are no longer marked as featured.'))
    unmark_featured.short_description = _(
        'Unmark selected entries as featured')

    def get_urls(self):
        entry_admin_urls = super(EntryAdmin, self).get_urls()
        urls = patterns(
            '',
            url(r'^autocomplete_tags/$',
                self.admin_site.admin_view(self.autocomplete_tags),
                name='zinnia_entry_autocomplete_tags'),
            url(r'^wymeditor/$',
                self.admin_site.admin_view(self.wymeditor),
                name='zinnia_entry_wymeditor'),
            url(r'^markitup/$',
                self.admin_site.admin_view(self.markitup),
                name='zinnia_entry_markitup'),
            url(r'^markitup/preview/$',
                self.admin_site.admin_view(self.content_preview),
                name='zinnia_entry_markitup_preview'),)
        return urls + entry_admin_urls

    def autocomplete_tags(self, request):
        """View for tag autocompletion"""
        return TemplateResponse(
            request, 'admin/zinnia/entry/autocomplete_tags.js',
            mimetype='application/javascript')

    def wymeditor(self, request):
        """View for serving the config of WYMEditor"""
        return TemplateResponse(
            request, 'admin/zinnia/entry/wymeditor.js',
            {'lang': get_language().split('-')[0]},
            'application/javascript')

    def markitup(self, request):
        """View for serving the config of MarkItUp"""
        return TemplateResponse(
            request, 'admin/zinnia/entry/markitup.js',
            mimetype='application/javascript')

    @csrf_exempt
    def content_preview(self, request):
        """Admin view to preview Entry.content in HTML,
        useful when using markups to write entries"""
        data = request.POST.get('data', '')
        entry = self.model(content=data)
        return TemplateResponse(
            request, 'admin/zinnia/entry/preview.html',
            {'preview': entry.html_content})

    def _media(self):
        STATIC_URL = '%szinnia/' % project_settings.STATIC_URL
        media = super(EntryAdmin, self).media + Media(
            css={'all': ('%scss/jquery.autocomplete.css' % STATIC_URL,)},
            js=('%sjs/jquery.js' % STATIC_URL,
                '%sjs/jquery.bgiframe.js' % STATIC_URL,
                '%sjs/jquery.autocomplete.js' % STATIC_URL,
                reverse('admin:zinnia_entry_autocomplete_tags'),))

        if settings.WYSIWYG == 'wymeditor':
            media += Media(
                js=('%sjs/wymeditor/jquery.wymeditor.pack.js' % STATIC_URL,
                    '%sjs/wymeditor/plugins/hovertools/'
                    'jquery.wymeditor.hovertools.js' % STATIC_URL,
                    reverse('admin:zinnia_entry_wymeditor')))
        elif settings.WYSIWYG == 'tinymce':
            from tinymce.widgets import TinyMCE
            media += TinyMCE().media + Media(
                js=(reverse('tinymce-js', args=('admin/zinnia/entry',)),))
        elif settings.WYSIWYG == 'markitup':
            media += Media(
                js=('%sjs/markitup/jquery.markitup.js' % STATIC_URL,
                    '%sjs/markitup/sets/%s/set.js' % (
                        STATIC_URL, settings.MARKUP_LANGUAGE),
                    reverse('admin:zinnia_entry_markitup')),
                css={'all': (
                    '%sjs/markitup/skins/django/style.css' % STATIC_URL,
                    '%sjs/markitup/sets/%s/style.css' % (
                        STATIC_URL, settings.MARKUP_LANGUAGE))})
        return media
    media = property(_media)

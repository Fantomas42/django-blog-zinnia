"""EntryAdmin for Zinnia"""
from datetime import datetime

from django.forms import Media
from django.contrib import admin
from django.conf.urls.defaults import *
from django.contrib.auth.models import User
from django.utils.html import strip_tags
from django.utils.text import truncate_words
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.urlresolvers import reverse, NoReverseMatch

from tagging.models import Tag

from zinnia import settings
from zinnia.managers import HIDDEN
from zinnia.managers import PUBLISHED
from zinnia.ping import DirectoryPinger
from zinnia.admin.forms import EntryAdminForm


class EntryAdmin(admin.ModelAdmin):
    form = EntryAdminForm
    date_hierarchy = 'creation_date'
    fieldsets = ((_('Content'), {'fields': ('title', 'content', 'image', 'status')}),
                 (_('Options'), {'fields': ('excerpt', 'related',
                                            'authors', 'creation_date',
                                            'start_publication', 'end_publication'),
                                 'classes': ('collapse', 'collapse-closed')}),
                 (_('Privacy'), {'fields': ('password', 'login_required',),
                                 'classes': ('collapse', 'collapse-closed')}),
                 (_('Discussion'), {'fields': ('comment_enabled', 'pingback_enabled')}),
                 (_('Publication'), {'fields': ('sites', 'categories', 'tags', 'slug')}))
    list_filter = ('categories', 'authors', 'status', 'login_required',
                   'comment_enabled', 'pingback_enabled',
                   'creation_date', 'start_publication', 'end_publication', 'sites')
    list_display = ('get_title', 'get_authors', 'get_categories',
                    'get_tags', 'get_sites',
                    'comment_enabled', 'pingback_enabled',
                    'get_is_actual', 'get_is_visible', 'get_link',
                    'get_short_url', 'creation_date')
    filter_horizontal = ('categories', 'authors', 'related')
    prepopulated_fields = {'slug': ('title', )}
    search_fields = ('title', 'excerpt', 'content', 'tags')
    actions = ['make_mine', 'make_published', 'make_hidden',
               'close_comments', 'close_pingbacks',
               'ping_directories', 'make_tweet']
    actions_on_top = True
    actions_on_bottom = True

    # Custom Display
    def get_title(self, entry):
        """Return the title with word count and number of comments"""
        title = _('%(title)s (%(word_count)i words)') % \
                {'title': entry.title, 'word_count': entry.word_count}
        comments = entry.comments.count()
        if comments:
            return _('%(title)s (%(comments)i comments)') % \
                   {'title': title, 'comments': comments}
        return title
    get_title.short_description = _('title')

    def get_authors(self, entry):
        """Return the authors in HTML"""
        try:
            authors = ['<a href="%s" target="blank">%s</a>' %
                       (reverse('zinnia_author_detail', args=[author.username]),
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
            categories = [category.title for category in entry.categories.all()]
        return ', '.join(categories)
    get_categories.allow_tags = True
    get_categories.short_description = _('category(s)')

    def get_tags(self, entry):
        """Return the tags linked in HTML"""
        try:
            return ', '.join(['<a href="%s" target="blank">%s</a>' %
                              (reverse('zinnia_tag_detail', args=[tag.name]), tag.name)
                              for tag in Tag.objects.get_for_object(entry)])
        except NoReverseMatch:
            return entry.tags
    get_tags.allow_tags = True
    get_tags.short_description = _('tag(s)')

    def get_sites(self, entry):
        """Return the sites linked in HTML"""
        return ', '.join(['<a href="http://%(domain)s" target="blank">%(name)s</a>' %
                          site.__dict__ for site in entry.sites.all()])
    get_sites.allow_tags = True
    get_sites.short_description = _('site(s)')

    def get_is_actual(self, entry):
        """Admin wrapper for entry.is_actual"""
        return entry.is_actual
    get_is_actual.boolean = True
    get_is_actual.short_description = _('is actual')

    def get_is_visible(self, entry):
        """Admin wrapper for entry.is_visible"""
        return entry.is_visible
    get_is_visible.boolean = True
    get_is_visible.short_description = _('is visible')

    def get_link(self, entry):
        """Return a formated link to the entry"""
        return _('<a href="%s" target="blank">View</a>') % entry.get_absolute_url()
    get_link.allow_tags = True
    get_link.short_description = _('View on site')

    def get_short_url(self, entry):
        url = entry.short_url
        if not url:
            return _('Unavailable')
        return '<a href="%(url)s" target="blank">%(url)s</a>' % \
               {'url': url}
    get_short_url.allow_tags = True
    get_short_url.short_description = _('short url')

    # Custom Methods
    def save_model(self, request, entry, form, change):
        """Save the authors, update time, make an excerpt"""
        if not form.cleaned_data.get('excerpt') and entry.status == PUBLISHED:
            entry.excerpt = truncate_words(strip_tags(entry.content), 50)

        if entry.pk and not request.user.has_perm('zinnia.can_change_author'):
            form.cleaned_data['authors'] = entry.authors.all()

        if not form.cleaned_data.get('authors'):
            form.cleaned_data['authors'].append(request.user)

        entry.last_update = datetime.now()
        entry.save()

    def queryset(self, request):
        """Make special filtering by user permissions"""
        queryset = super(EntryAdmin, self).queryset(request)
        if request.user.has_perm('zinnia.can_view_all'):
            return queryset
        return request.user.entry_set.all()

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Filters the disposable authors"""
        if db_field.name == 'authors':
            if request.user.has_perm('zinnia.can_change_author'):
                kwargs['queryset'] = User.objects.filter(is_staff=True)
            else:
                kwargs['queryset'] = User.objects.filter(pk=request.user.pk)

        return super(EntryAdmin, self).formfield_for_manytomany(
            db_field, request, **kwargs)

    def get_actions(self, request):
        """Define user actions by permissions"""
        actions = super(EntryAdmin, self).get_actions(request)
        if not request.user.has_perm('zinnia.can_change_author') \
           or not request.user.has_perm('zinnia.can_view_all'):
            del actions['make_mine']
        if not settings.PING_DIRECTORIES:
            del actions['ping_directories']
        if not settings.USE_TWITTER or not settings.USE_BITLY:
            del actions['make_tweet']

        return actions

    # Custom Actions
    def make_mine(self, request, queryset):
        """Set the entries to the user"""
        for entry in queryset:
            if request.user not in entry.authors.all():
                entry.authors.add(request.user)
    make_mine.short_description = _('Set the entries to the user')

    def make_published(self, request, queryset):
        """Set entries selected as published"""
        queryset.update(status=PUBLISHED)
    make_published.short_description = _('Set entries selected as published')

    def make_hidden(self, request, queryset):
        """Set entries selected as hidden"""
        queryset.update(status=HIDDEN)
    make_hidden.short_description = _('Set entries selected as hidden')

    def make_tweet(self, request, queryset):
        """Post an update on Twitter"""
        import twitter
        api = twitter.Api(username=settings.TWITTER_USER,
                          password=settings.TWITTER_PASSWORD)
        for entry in queryset:
            message = '%s %s' % (entry.title[:119], entry.short_url)
            api.PostUpdate(message)
    make_tweet.short_description = _('Tweet entries selected')

    def close_comments(self, request, queryset):
        """Close the comments for selected entries"""
        queryset.update(comment_enabled=False)
    close_comments.short_description = _('Close the comments for selected entries')

    def close_pingbacks(self, request, queryset):
        """Close the pingbacks for selected entries"""
        queryset.update(pingback_enabled=False)
    close_pingbacks.short_description = _('Close the linkbacks for selected entries')

    def ping_directories(self, request, queryset):
        """Ping Directories for selected entries"""
        for directory in settings.PING_DIRECTORIES:
            pinger = DirectoryPinger(directory, queryset)
            pinger.join()
            success = 0
            for result in pinger.results:
                if not result.get('flerror', True):
                    success += 1
                else:
                    self.message_user(request, '%s : %s' % (directory, result['message']))
            if success:
                self.message_user(request, _('%(directory)s directory succesfully pinged %(success)d entries.') %
                                  {'directory': directory, 'success': success})
    ping_directories.short_description = _('Ping Directories for selected entries')

    def get_urls(self):
        entry_admin_urls = super(EntryAdmin, self).get_urls()
        urls = patterns('django.views.generic.simple',
                        url(r'^autocomplete_tags/$', 'direct_to_template',
                            {'template': 'admin/zinnia/entry/autocomplete_tags.js',
                             'mimetype': 'application/javascript'},
                            name='zinnia_entry_autocomplete_tags'),
                        url(r'^wymeditor/$', 'direct_to_template',
                            {'template': 'admin/zinnia/entry/wymeditor.js',
                             'mimetype': 'application/javascript'},
                            name='zinnia_entry_wymeditor'),)
        return urls + entry_admin_urls

    def _media(self):
        MEDIA_URL = settings.MEDIA_URL
        media = super(EntryAdmin, self).media + \
                Media(css={'all': ('%scss/jquery.autocomplete.css' % MEDIA_URL,),},
                      js=('%sjs/jquery.js' % MEDIA_URL,
                          '%sjs/jquery.bgiframe.js' % MEDIA_URL,
                          '%sjs/jquery.autocomplete.js' % MEDIA_URL,
                          reverse('admin:zinnia_entry_autocomplete_tags'),))

        if settings.WYSIWYG == 'wymeditor':
            media += Media(js=('%sjs/wymeditor/jquery.wymeditor.pack.js' % MEDIA_URL,
                               reverse('admin:zinnia_entry_wymeditor')))
        elif settings.WYSIWYG == 'tinymce':
            from tinymce.widgets import TinyMCE
            media += TinyMCE().media + Media(
                js=(reverse('tinymce-js', args=('admin/zinnia/entry',)),))
        return media
    media = property(_media)



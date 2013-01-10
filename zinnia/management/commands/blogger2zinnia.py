"""Blogger to Zinnia command module
Based on Elijah Rutschman's code"""
import sys
from getpass import getpass
from datetime import datetime
from optparse import make_option

from django.conf import settings
from django.utils import timezone
from django.utils.encoding import smart_str
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.core.management.base import CommandError
from django.core.management.base import NoArgsCommand
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments import get_model as get_comment_model

from zinnia import __version__
from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.models.category import Category
from zinnia.managers import DRAFT, PUBLISHED
from zinnia.signals import disconnect_entry_signals
from zinnia.signals import disconnect_discussion_signals

gdata_service = None
Comment = get_comment_model()


class Command(NoArgsCommand):
    """Command object for importing a Blogger blog
    into Zinnia via Google's gdata API."""
    help = 'Import a Blogger blog into Zinnia.'

    option_list = NoArgsCommand.option_list + (
        make_option('--blogger-username', dest='blogger_username', default='',
                    help='The username to login to Blogger with'),
        make_option('--category-title', dest='category_title', default='',
                    help='The Zinnia category to import Blogger posts to'),
        make_option('--blogger-blog-id', dest='blogger_blog_id', default='',
                    help='The id of the Blogger blog to import'),
        make_option('--blogger-limit', dest='blogger_limit', default=25,
                    help='Specify a limit for posts to be imported'),
        make_option('--author', dest='author', default='',
                    help='All imported entries belong to specified author'))

    SITE = Site.objects.get_current()

    def __init__(self):
        """Init the Command and add custom styles"""
        super(Command, self).__init__()
        self.style.TITLE = self.style.SQL_FIELD
        self.style.STEP = self.style.SQL_COLTYPE
        self.style.ITEM = self.style.HTTP_INFO
        disconnect_entry_signals()
        disconnect_discussion_signals()

    def write_out(self, message, verbosity_level=1):
        """Convenient method for outputing"""
        if self.verbosity and self.verbosity >= verbosity_level:
            sys.stdout.write(smart_str(message))
            sys.stdout.flush()

    def handle_noargs(self, **options):
        global gdata_service
        try:
            from gdata import service
            gdata_service = service
        except ImportError:
            raise CommandError('You need to install the gdata '
                               'module to run this command.')

        self.verbosity = int(options.get('verbosity', 1))
        self.blogger_username = options.get('blogger_username')
        self.blogger_blog_id = options.get('blogger_blog_id')
        self.blogger_limit = int(options.get('blogger_limit'))
        self.category_title = options.get('category_title')

        self.write_out(self.style.TITLE(
            'Starting migration from Blogger to Zinnia %s\n' % __version__))

        if not self.blogger_username:
            self.blogger_username = raw_input('Blogger username: ')
            if not self.blogger_username:
                raise CommandError('Invalid Blogger username')

        self.blogger_password = getpass('Blogger password: ')
        try:
            self.blogger_manager = BloggerManager(self.blogger_username,
                                                  self.blogger_password)
        except gdata_service.BadAuthentication:
            raise CommandError('Incorrect Blogger username or password')

        default_author = options.get('author')
        if default_author:
            try:
                self.default_author = Author.objects.get(
                    username=default_author)
            except Author.DoesNotExist:
                raise CommandError(
                    'Invalid Zinnia username for default author "%s"' %
                    default_author)
        else:
            self.default_author = Author.objects.all()[0]

        if not self.blogger_blog_id:
            self.select_blog_id()

        if not self.category_title:
            self.category_title = raw_input(
                'Category title for imported entries: ')
            if not self.category_title:
                raise CommandError('Invalid category title')

        self.import_posts()

    def select_blog_id(self):
        self.write_out(self.style.STEP('- Requesting your weblogs\n'))
        blogs_list = [blog for blog in self.blogger_manager.get_blogs()]
        while True:
            i = 0
            blogs = {}
            for blog in blogs_list:
                i += 1
                blogs[i] = blog
                self.write_out('%s. %s (%s)' % (i, blog.title.text,
                                                get_blog_id(blog)))
            try:
                blog_index = int(raw_input('\nSelect a blog to import: '))
                blog = blogs[blog_index]
                break
            except (ValueError, KeyError):
                self.write_out(self.style.ERROR(
                    'Please enter a valid blog number\n'))

        self.blogger_blog_id = get_blog_id(blog)

    def get_category(self):
        category, created = Category.objects.get_or_create(
            title=self.category_title,
            slug=slugify(self.category_title)[:255])

        if created:
            category.save()

        return category

    def import_posts(self):
        category = self.get_category()
        self.write_out(self.style.STEP('- Importing entries\n'))
        for post in self.blogger_manager.get_posts(self.blogger_blog_id,
                                                   self.blogger_limit):
            creation_date = convert_blogger_timestamp(post.published.text)
            status = DRAFT if is_draft(post) else PUBLISHED
            title = post.title.text or ''
            content = post.content.text or ''
            slug = slugify(post.title.text or get_post_id(post))[:255]
            try:
                entry = Entry.objects.get(creation_date=creation_date,
                                          slug=slug)
                output = self.style.NOTICE('> Skipped %s (already migrated)\n'
                                           % entry)
            except Entry.DoesNotExist:
                entry = Entry(status=status, title=title, content=content,
                              creation_date=creation_date, slug=slug)
                if self.default_author:
                    entry.author = self.default_author
                entry.tags = ','.join([slugify(cat.term) for
                                       cat in post.category])
                entry.last_update = convert_blogger_timestamp(
                    post.updated.text)
                entry.save()
                entry.sites.add(self.SITE)
                entry.categories.add(category)
                entry.authors.add(self.default_author)
                try:
                    self.import_comments(entry, post)
                except gdata_service.RequestError:
                    # comments not available for this post
                    pass
                entry.comment_count = entry.comments.count()
                entry.save(force_update=True)
                output = self.style.ITEM('> Migrated %s + %s comments\n'
                                         % (entry.title, entry.comment_count))

            self.write_out(output)

    def import_comments(self, entry, post):
        blog_id = self.blogger_blog_id
        post_id = get_post_id(post)
        comments = self.blogger_manager.get_comments(blog_id, post_id)
        entry_content_type = ContentType.objects.get_for_model(Entry)

        for comment in comments:
            submit_date = convert_blogger_timestamp(comment.published.text)
            content = comment.content.text

            author = comment.author[0]
            if author:
                user_name = author.name.text if author.name else ''
                user_email = author.email.text if author.email else ''
                user_url = author.uri.text if author.uri else ''

            else:
                user_name = ''
                user_email = ''
                user_url = ''

            com, created = Comment.objects.get_or_create(
                content_type=entry_content_type,
                object_pk=entry.pk,
                comment=content,
                submit_date=submit_date,
                site=self.SITE,
                user_name=user_name,
                user_email=user_email,
                user_url=user_url)

            if created:
                com.save()


def convert_blogger_timestamp(timestamp):
    # parse 2010-12-19T15:37:00.003
    date_string = timestamp[:-6]
    dt = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%f')
    if settings.USE_TZ:
        dt = timezone.make_aware(dt, timezone.utc)
    return dt


def is_draft(post):
    if post.control:
        if post.control.draft:
            if post.control.draft.text == 'yes':
                return True
    return False


def get_blog_id(blog):
    return blog.GetSelfLink().href.split('/')[-1]


def get_post_id(post):
    return post.GetSelfLink().href.split('/')[-1]


class BloggerManager(object):

    def __init__(self, username, password):
        self.service = gdata_service.GDataService(username, password)
        self.service.server = 'www.blogger.com'
        self.service.service = 'blogger'
        self.service.ProgrammaticLogin()

    def get_blogs(self):
        feed = self.service.Get('/feeds/default/blogs')
        for blog in feed.entry:
            yield blog

    def get_posts(self, blog_id, limit):
        feed = self.service.Get('/feeds/%s/posts/default/?max-results=%d' %
                                (blog_id, limit))
        for post in feed.entry:
            yield post

    def get_comments(self, blog_id, post_id):
        feed = self.service.Get('/feeds/%s/%s/comments/default' %
                                (blog_id, post_id))
        for comment in feed.entry:
            yield comment

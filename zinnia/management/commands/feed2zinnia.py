"""Feed to Zinnia command module"""
import sys
from datetime import datetime
from optparse import make_option

from django.utils.html import strip_tags
from django.db.utils import IntegrityError
from django.utils.encoding import smart_str
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.text import truncate_words
from django.template.defaultfilters import slugify
from django.core.management.base import CommandError
from django.core.management.base import LabelCommand

from zinnia import __version__
from zinnia.models import Entry
from zinnia.models import Category
from zinnia.managers import PUBLISHED
from zinnia.signals import disconnect_zinnia_signals


class Command(LabelCommand):
    """Command object for importing a RSS or Atom
    feed into Zinnia."""
    help = 'Import a RSS or Atom feed into Zinnia.'
    label = 'feed url'
    args = 'url'

    option_list = LabelCommand.option_list + (
        make_option('--noautoexcerpt', action='store_false', dest='auto_excerpt',
                    default=True, help='Do NOT generate an excerpt if not present.'),
        make_option('--author', dest='author', default='',
                    help='All imported entries belong to specified author'),
        make_option('--category-is-tag', action='store_true', dest='category-tag',
                    default=False, help='Store categories as tags'),
        )
    SITE = Site.objects.get_current()

    def __init__(self):
        """Init the Command and add custom styles"""
        super(Command, self).__init__()
        self.style.TITLE = self.style.SQL_FIELD
        self.style.STEP = self.style.SQL_COLTYPE
        self.style.ITEM = self.style.HTTP_INFO
        disconnect_zinnia_signals()

    def write_out(self, message, verbosity_level=1):
        """Convenient method for outputing"""
        if self.verbosity and self.verbosity >= verbosity_level:
            sys.stdout.write(smart_str(message))
            sys.stdout.flush()

    def handle_label(self, url, **options):
        try:
            import feedparser
        except ImportError:
            raise CommandError('You need to install the feedparser module to run this command.')

        self.verbosity = int(options.get('verbosity', 1))
        self.auto_excerpt = options.get('auto_excerpt', True)
        self.default_author = options.get('author')
        self.category_tag = options.get('category-tag', False)
        if self.default_author:
            try:
                self.default_author = User.objects.get(username=self.default_author)
            except User.DoesNotExist:
                raise CommandError('Invalid username for default author')

        self.write_out(self.style.TITLE('Starting importation of %s to Zinnia %s:\n' % (url, __version__)))

        feed = feedparser.parse(url)
        self.import_entries(feed.entries)

    def import_entries(self, feed_entries):
        """Import entries"""
        for feed_entry in feed_entries:
            self.write_out('> %s... ' % feed_entry.title)
            creation_date = datetime(*feed_entry.date_parsed[:6])
            slug = slugify(feed_entry.title)[:255]

            if Entry.objects.filter(creation_date__year=creation_date.year,
                                    creation_date__month=creation_date.month,
                                    creation_date__day=creation_date.day,
                                    slug=slug):
                self.write_out(self.style.NOTICE('SKIPPED (already imported)\n'))
                continue

            categories = self.import_categories(feed_entry)
            entry_dict = {'title': feed_entry.title[:255],
                          'content': feed_entry.description,
                          'excerpt': feed_entry.get('summary'),
                          'status': PUBLISHED,
                          'creation_date': creation_date,
                          'start_publication': creation_date,
                          'last_update': datetime.now(),
                          'slug': slug}

            if not entry_dict['excerpt'] and self.auto_excerpt:
                entry_dict['excerpt'] = truncate_words(strip_tags(feed_entry.description), 50)
            if self.category_tag:
                entry_dict['tags'] = self.import_tags(categories)

            entry = Entry(**entry_dict)
            entry.save()
            entry.categories.add(*categories)
            entry.sites.add(self.SITE)

            if self.default_author:
                entry.authors.add(self.default_author)
            elif feed_entry.get('author_detail'):
                try:
                    user = User.objects.create_user(slugify(feed_entry.author_detail.get('name')),
                                                    feed_entry.author_detail.get('email', ''))
                except IntegrityError:
                    user = User.objects.get(username=slugify(feed_entry.author_detail.get('name')))
                entry.authors.add(user)

            self.write_out(self.style.ITEM('OK\n'))

    def import_categories(self, feed_entry):
        categories = []
        for cat in feed_entry.get('tags', ''):
            category, created = Category.objects.get_or_create(
                slug=slugify(cat.term), defaults={'title': cat.term})
            categories.append(category)
        return categories

    def import_tags(self, categories):
        tags = []
        for cat in categories:
            if len(cat.title.split()) > 1:
                tags.append('"%s"' % slugify(cat.title).replace('-', ' '))
            else:
                tags.append(slugify(cat.title).replace('-', ' '))
        return ', '.join(tags)

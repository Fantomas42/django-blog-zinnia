"""WordPress to Zinnia command module"""
import sys
from datetime import datetime
from optparse import make_option
from xml.etree import ElementTree as ET

from django.utils.html import strip_tags
from django.db.utils import IntegrityError
from django.utils.encoding import smart_str
from django.utils.text import truncate_words
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.contrib.comments.models import Comment
from django.core.management.base import CommandError
from django.core.management.base import LabelCommand

from tagging.models import Tag

from zinnia import __version__
from zinnia.models import Entry
from zinnia.models import Category
from zinnia.managers import DRAFT, HIDDEN, PUBLISHED


class Command(LabelCommand):
    """Command object for importing a WordPress blog
    into Zinnia via a WordPress eXtended RSS (WXR) file."""
    help = 'Import a Wordpress blog into Zinnia.'
    label = 'WXR file'
    args = 'wordpress.xml'

    option_list = LabelCommand.option_list + (
        make_option('--noautoexcerpt', action='store_false', dest='auto_excerpt',
                    default=True, help='Do NOT generate an excerpt if not present.'),
        make_option('--author', dest='author', default='',
                    help='All imported entries belong to specified author'),
        )

    SITE = Site.objects.get_current()
    REVERSE_STATUS = {'pending': DRAFT,
                      'draft': DRAFT,
                      'auto-draft': DRAFT,
                      'inherit': DRAFT,
                      'publish': PUBLISHED,
                      'future': PUBLISHED,
                      'trash': HIDDEN,
                      'private': HIDDEN}

    def __init__(self):
        """Init the Command and add custom styles"""
        super(Command, self).__init__()
        self.style.TITLE = self.style.SQL_FIELD
        self.style.STEP = self.style.SQL_COLTYPE
        self.style.ITEM = self.style.HTTP_INFO

    def write_out(self, message, verbosity_level=1):
        """Convenient method for outputing"""
        if self.verbosity and self.verbosity >= verbosity_level:
            sys.stdout.write(smart_str(message))
            sys.stdout.flush()

    def handle_label(self, wxr_file, **options):
        self.verbosity = int(options.get('verbosity', 1))
        self.auto_excerpt = options.get('auto_excerpt', True)
        self.default_author = options.get('author')
        if self.default_author:
            try:
                self.default_author = User.objects.get(username=self.default_author)
            except User.DoesNotExist:
                raise CommandError('Invalid username for default author')

        self.write_out(self.style.TITLE('Starting migration from Wordpress to Zinnia %s:\n' % __version__))
        tree = ET.parse(wxr_file)

        self.authors = self.import_authors(tree)

        self.categories = self.import_categories(
            tree.findall('channel/{http://wordpress.org/export/1.0/}category'))

        self.import_tags(
            tree.findall('channel/{http://wordpress.org/export/1.0/}tag'))

        self.import_entries(tree.findall('channel/item'))


    def import_authors(self, tree):
        """Retrieve all the authors used in posts
        and convert it to new or existing user, and
        return the convertion"""
        self.write_out(self.style.STEP('- Importing authors\n'))

        post_authors = set()
        for item in tree.findall('channel/item'):
            post_type = item.find('{http://wordpress.org/export/1.0/}post_type').text
            if post_type == 'post':
                post_authors.add(item.find('{http://purl.org/dc/elements/1.1/}creator').text)

        self.write_out('%i authors found.\n' % len(post_authors))

        authors = {}
        for post_author in post_authors:
            if self.default_author:
                authors[post_author] = self.default_author
            else:
                authors[post_author] = self.migrate_author(post_author)
        return authors

    def migrate_author(self, author_name):
        """Handle actions for migrating the users"""
        select_action_text = "The author '%s' need to be migrated to an User:\n"\
                             "1. Use an existing user ?\n"\
                             "2. Create a new user ?\n"\
                             "Please select a choice: " % author_name
        while 42:
            selection = raw_input(select_action_text)
            if selection in '12':
                break
        if selection == '1':
            users = User.objects.all()
            usernames = [user.username for user in users]
            while 42:
                select_user_text = "1. Select your user, by typing one of theses usernames:\n"\
                                   "[%s]\n"\
                                   "Please select a choice: " % ', '.join(usernames)
                user_selected = raw_input(select_user_text)
                if user_selected in usernames:
                    break
            return users.get(username=user_selected)
        else:
            create_user_text = "2. Please type the email of the '%s' user: " % author_name
            author_mail = raw_input(create_user_text)
            try:
                return User.objects.create_user(author_name, author_mail)
            except IntegrityError:
                return User.objects.get(username=author_name)

    def import_categories(self, category_nodes):
        """Import all the categories from 'wp:category' nodes,
        because categories in 'item' nodes are not necessarily
        all the categories and returning it in a dict for
        database optimizations."""
        self.write_out(self.style.STEP('- Importing categories\n'))

        categories = {}
        for category_node in category_nodes:
            title = category_node.find('{http://wordpress.org/export/1.0/}cat_name').text[:50]
            slug = category_node.find('{http://wordpress.org/export/1.0/}category_nicename').text[:50]
            self.write_out('> %s... ' % title)
            category, created = Category.objects.get_or_create(
                title=title, slug=slug)
            categories[title] = category
            self.write_out(self.style.ITEM('OK\n'))
        return categories

    def import_tags(self, tag_nodes):
        """Import all the tags form 'wp:tag' nodes,
        because tags in 'item' nodes are not necessarily
        all the tags, then use only the nicename, because it's like
        a slug and the true tag name may be not valid for url usage."""
        self.write_out(self.style.STEP('- Importing tags\n'))
        for tag_node in tag_nodes:
            tag_name = tag_node.find('{http://wordpress.org/export/1.0/}tag_slug').text[:50]
            self.write_out('> %s... ' % tag_name)
            tag, created = Tag.objects.get_or_create(name=tag_name)
            self.write_out(self.style.ITEM('OK\n'))

    def get_entry_tags(self, categories):
        """Return a list of entry's tags,
        by using the nicename for url compatibility"""
        tags = []
        for category in categories:
            domain = category.attrib.get('domain', 'category')
            if domain == 'tag' and category.attrib.get('nicename'):
                tags.append(category.attrib.get('nicename'))
        return tags

    def get_entry_categories(self, category_nodes):
        """Return a list of entry's categories
        based of imported categories"""
        categories = []
        for category_node in category_nodes:
            domain = category_node.attrib.get('domain')
            if domain == 'category':
                categories.append(self.categories[category_node.text])
        return categories

    def import_entry(self, title, content, item_node):
        """Importing an entry but some data are missing like
        the image, related entries, start_publication and end_publication.
        start_publication and creation_date will use the same value,
        wich is always in Wordpress $post->post_date"""
        creation_date = datetime.strptime(
            item_node.find('{http://wordpress.org/export/1.0/}post_date').text,
            '%Y-%m-%d %H:%M:%S')

        excerpt = item_node.find('{http://wordpress.org/export/1.0/excerpt/}encoded').text
        if not excerpt:
            if self.auto_excerpt:
                excerpt = truncate_words(strip_tags(content), 50)
            else:
                excerpt = ''
        # Prefer use this function than
        # item_node.find('{http://wordpress.org/export/1.0/}post_name').text
        # Because slug can be not well formated
        # maximum length of the slug field == 50 chars
        slug = slugify(title)[0:50]
        entry_dict = {'content': content,
                      'excerpt': excerpt,
                      'slug': slug,
                      'tags': ', '.join(self.get_entry_tags(item_node.findall('category'))),
                      'status': self.REVERSE_STATUS[item_node.find('{http://wordpress.org/export/1.0/}status').text],
                      'comment_enabled': item_node.find('{http://wordpress.org/export/1.0/}comment_status').text == 'open',
                      'pingback_enabled': item_node.find('{http://wordpress.org/export/1.0/}ping_status').text == 'open',
                      'creation_date': creation_date,
                      'last_update': datetime.now(),
                      'start_publication': creation_date,}
        entry, created = Entry.objects.get_or_create(title=title,
                                                     defaults=entry_dict)
        entry.categories.add(*self.get_entry_categories(item_node.findall('category')))
        entry.authors.add(self.authors[item_node.find('{http://purl.org/dc/elements/1.1/}creator').text])
        entry.sites.add(self.SITE)
        #current_id = item_node.find('{http://wordpress.org/export/1.0/}post_id').text
        #parent_id = item_node.find('{http://wordpress.org/export/1.0/}post_parent').text

        return entry

    def import_entries(self, items):
        """Loops over items and find entry to import,
        an entry need to have 'post_type' set to 'post' and
        have content."""
        self.write_out(self.style.STEP('- Importing entries\n'))

        for item_node in items:
            title = (item_node.find('title').text or '')[:100]
            post_type = item_node.find('{http://wordpress.org/export/1.0/}post_type').text
            content = item_node.find('{http://purl.org/rss/1.0/modules/content/}encoded').text

            if post_type == 'post' and content and title:
                self.write_out('> %s... ' % title)
                entry = self.import_entry(title, content, item_node)
                self.write_out(self.style.ITEM('OK\n'))
                self.import_comments(entry, item_node.findall(
                    '{http://wordpress.org/export/1.0/}comment/'))
            else:
                self.write_out('> %s... ' % title, 2)
                self.write_out(self.style.NOTICE('SKIPPED (not a post)\n'), 2)

    def import_comments(self, entry, comment_nodes):
        """Loops over comments nodes and import then
        in django.contrib.comments"""
        for comment_node in comment_nodes:
            is_pingback = comment_node.find(
                '{http://wordpress.org/export/1.0/}comment_type').text == 'pingback'
            is_trackback = comment_node.find(
                '{http://wordpress.org/export/1.0/}comment_type').text == 'trackback'

            title = 'Comment #%s' % (comment_node.find(
                '{http://wordpress.org/export/1.0/}comment_id/').text)
            self.write_out(' > %s... ' % title)

            content = comment_node.find(
                '{http://wordpress.org/export/1.0/}comment_content/').text
            if not content:
                self.write_out(self.style.NOTICE('SKIPPED (unfilled)\n'))
                return

            submit_date = datetime.strptime(
                comment_node.find('{http://wordpress.org/export/1.0/}comment_date').text,
                '%Y-%m-%d %H:%M:%S')

            approvation = comment_node.find('{http://wordpress.org/export/1.0/}comment_approved').text
            is_public = True
            is_removed = False
            if approvation != '1':
                is_removed = True
            if approvation == 'spam':
                is_public = False
            # maximum length of user_name == 50 chars
            comment_author = comment_node.find('{http://wordpress.org/export/1.0/}comment_author/').text[0:50]
            comment_dict = {'content_object': entry,
                            'site': self.SITE,
                            'user_name': comment_author,
                            'user_email': comment_node.find(
                                '{http://wordpress.org/export/1.0/}comment_author_email/').text or '',
                            'user_url': comment_node.find(
                                '{http://wordpress.org/export/1.0/}comment_author_url/').text or '',
                            'comment': content,
                            'submit_date': submit_date,
                            'ip_address': comment_node.find(
                                '{http://wordpress.org/export/1.0/}comment_author_IP/').text or '',
                            'is_public': is_public,
                            'is_removed': is_removed, }
            comment = Comment(**comment_dict)
            comment.save()
            if approvation == 'spam':
                comment.flags.create(user=entry.authors.all()[0], flag='spam')
            if is_pingback:
                comment.flags.create(user=entry.authors.all()[0], flag='pingback')
            if is_trackback:
                comment.flags.create(user=entry.authors.all()[0], flag='trackback')

            self.write_out(self.style.ITEM('OK\n'))

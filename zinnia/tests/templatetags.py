"""Test cases for Zinnia's templatetags"""
from django.test import TestCase
from django.utils import timezone
from django.template import Context
from django.template import Template
from django.template import TemplateSyntaxError
from django.contrib import comments
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.contrib.comments.models import CommentFlag
from django.contrib.auth.tests.utils import skipIfCustomUser

from tagging.models import Tag

from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.models.category import Category
from zinnia.managers import DRAFT
from zinnia.managers import PUBLISHED
from zinnia.flags import PINGBACK, TRACKBACK
from zinnia.tests.utils import datetime, urlEqual
from zinnia.templatetags.zinnia_tags import widont
from zinnia.templatetags.zinnia_tags import get_authors
from zinnia.templatetags.zinnia_tags import get_gravatar
from zinnia.templatetags.zinnia_tags import get_tag_cloud
from zinnia.templatetags.zinnia_tags import get_categories
from zinnia.templatetags.zinnia_tags import get_categories_tree
from zinnia.templatetags.zinnia_tags import zinnia_pagination
from zinnia.templatetags.zinnia_tags import zinnia_statistics
from zinnia.templatetags.zinnia_tags import get_draft_entries
from zinnia.templatetags.zinnia_tags import get_recent_entries
from zinnia.templatetags.zinnia_tags import get_random_entries
from zinnia.templatetags.zinnia_tags import zinnia_breadcrumbs
from zinnia.templatetags.zinnia_tags import get_popular_entries
from zinnia.templatetags.zinnia_tags import get_similar_entries
from zinnia.templatetags.zinnia_tags import get_recent_comments
from zinnia.templatetags.zinnia_tags import get_recent_linkbacks
from zinnia.templatetags.zinnia_tags import get_calendar_entries
from zinnia.templatetags.zinnia_tags import get_archives_entries
from zinnia.templatetags.zinnia_tags import get_featured_entries
from zinnia.templatetags.zinnia_tags import get_archives_entries_tree


class TemplateTagsTestCase(TestCase):
    """Test cases for Template tags"""

    def setUp(self):
        params = {'title': 'My entry',
                  'content': 'My content',
                  'tags': 'zinnia, test',
                  'creation_date': datetime(2010, 1, 1),
                  'slug': 'my-entry'}
        self.entry = Entry.objects.create(**params)

    def publish_entry(self):
        self.entry.status = PUBLISHED
        self.entry.featured = True
        self.entry.sites.add(Site.objects.get_current())
        self.entry.save()

    def test_get_categories(self):
        source_context = Context({})
        with self.assertNumQueries(1):
            context = get_categories(source_context)
        self.assertEqual(len(context['categories']), 0)
        self.assertEqual(context['template'], 'zinnia/tags/categories.html')
        self.assertEqual(context['context_category'], None)
        category = Category.objects.create(title='Category 1',
                                           slug='category-1')
        self.entry.categories.add(category)
        self.publish_entry()
        source_context = Context({'category': category})
        with self.assertNumQueries(0):
            context = get_categories(source_context, 'custom_template.html')
        self.assertEqual(len(context['categories']), 1)
        self.assertEqual(context['categories'][0].count_entries_published, 1)
        self.assertEqual(context['template'], 'custom_template.html')
        self.assertEqual(context['context_category'], category)

    def test_get_categories_tree(self):
        source_context = Context({})
        with self.assertNumQueries(0):
            context = get_categories_tree(source_context)
        self.assertEqual(len(context['categories']), 0)
        self.assertEqual(context['template'],
                         'zinnia/tags/categories_tree.html')
        self.assertEqual(context['context_category'], None)

        category = Category.objects.create(title='Category 1',
                                           slug='category-1')
        source_context = Context({'category': category})
        with self.assertNumQueries(0):
            context = get_categories_tree(
                source_context, 'custom_template.html')
        self.assertEqual(len(context['categories']), 1)
        self.assertEqual(context['template'], 'custom_template.html')
        self.assertEqual(context['context_category'], category)

    @skipIfCustomUser
    def test_get_authors(self):
        source_context = Context({})
        with self.assertNumQueries(1):
            context = get_authors(source_context)
        self.assertEqual(len(context['authors']), 0)
        self.assertEqual(context['template'], 'zinnia/tags/authors.html')
        self.assertEqual(context['context_author'], None)
        author = Author.objects.create_user(username='webmaster',
                                            email='webmaster@example.com')
        self.entry.authors.add(author)
        self.publish_entry()
        source_context = Context({'author': author})
        with self.assertNumQueries(0):
            context = get_authors(source_context, 'custom_template.html')
        self.assertEqual(len(context['authors']), 1)
        self.assertEqual(context['authors'][0].count_entries_published, 1)
        self.assertEqual(context['template'], 'custom_template.html')
        self.assertEqual(context['context_author'], author)

    def test_get_recent_entries(self):
        with self.assertNumQueries(1):
            context = get_recent_entries()
        self.assertEqual(len(context['entries']), 0)
        self.assertEqual(context['template'],
                         'zinnia/tags/recent_entries.html')

        self.publish_entry()
        with self.assertNumQueries(0):
            context = get_recent_entries(3, 'custom_template.html')
        self.assertEqual(len(context['entries']), 1)
        self.assertEqual(context['template'], 'custom_template.html')
        with self.assertNumQueries(0):
            context = get_recent_entries(0)
        self.assertEqual(len(context['entries']), 0)

    def test_get_featured_entries(self):
        with self.assertNumQueries(1):
            context = get_featured_entries()
        self.assertEqual(len(context['entries']), 0)
        self.assertEqual(context['template'],
                         'zinnia/tags/featured_entries.html')

        self.publish_entry()
        with self.assertNumQueries(0):
            context = get_featured_entries(3, 'custom_template.html')
        self.assertEqual(len(context['entries']), 1)
        self.assertEqual(context['template'], 'custom_template.html')
        with self.assertNumQueries(0):
            context = get_featured_entries(0)
        self.assertEqual(len(context['entries']), 0)

    def test_draft_entries(self):
        with self.assertNumQueries(0):
            context = get_draft_entries()
        self.assertEqual(len(context['entries']), 1)
        self.assertEqual(context['template'],
                         'zinnia/tags/draft_entries.html')

        self.publish_entry()
        with self.assertNumQueries(0):
            context = get_draft_entries(3, 'custom_template.html')
        self.assertEqual(len(context['entries']), 0)
        self.assertEqual(context['template'], 'custom_template.html')
        with self.assertNumQueries(0):
            context = get_draft_entries(0)
        self.assertEqual(len(context['entries']), 0)

    def test_get_random_entries(self):
        with self.assertNumQueries(1):
            context = get_random_entries()
        self.assertEqual(len(context['entries']), 0)
        self.assertEqual(context['template'],
                         'zinnia/tags/random_entries.html')

        self.publish_entry()
        with self.assertNumQueries(0):
            context = get_random_entries(3, 'custom_template.html')
        self.assertEqual(len(context['entries']), 1)
        self.assertEqual(context['template'], 'custom_template.html')
        with self.assertNumQueries(0):
            context = get_random_entries(0)
        self.assertEqual(len(context['entries']), 0)

    def test_get_popular_entries(self):
        with self.assertNumQueries(1):
            context = get_popular_entries()
        self.assertEqual(len(context['entries']), 0)
        self.assertEqual(context['template'],
                         'zinnia/tags/popular_entries.html')

        self.publish_entry()
        with self.assertNumQueries(0):
            context = get_popular_entries(3, 'custom_template.html')
        self.assertEqual(len(context['entries']), 0)
        self.assertEqual(context['template'], 'custom_template.html')

        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'tags': 'zinnia, test',
                  'status': PUBLISHED,
                  'comment_count': 2,
                  'slug': 'my-second-entry'}
        site = Site.objects.get_current()
        second_entry = Entry.objects.create(**params)
        second_entry.sites.add(site)
        self.entry.comment_count = 1
        self.entry.save()
        with self.assertNumQueries(0):
            context = get_popular_entries(3)
        self.assertEqual(list(context['entries']), [second_entry, self.entry])

        self.entry.comment_count = 2
        self.entry.save()
        with self.assertNumQueries(0):
            context = get_popular_entries(3)
        self.assertEqual(list(context['entries']), [self.entry, second_entry])

        self.entry.status = DRAFT
        self.entry.save()
        with self.assertNumQueries(0):
            context = get_popular_entries(3)
        self.assertEqual(list(context['entries']), [second_entry])

    def test_get_similar_entries(self):
        self.publish_entry()
        source_context = Context({'object': self.entry})
        with self.assertNumQueries(3):
            context = get_similar_entries(source_context)
        self.assertEqual(len(context['entries']), 0)
        self.assertEqual(context['template'],
                         'zinnia/tags/similar_entries.html')

        params = {'title': 'My second entry',
                  'content': 'This is the second entry of my tests.',
                  'tags': 'zinnia, test',
                  'status': PUBLISHED,
                  'slug': 'my-second-entry'}
        site = Site.objects.get_current()
        second_entry = Entry.objects.create(**params)
        second_entry.sites.add(site)

        source_context = Context({'object': second_entry})
        with self.assertNumQueries(3):
            context = get_similar_entries(source_context, 3,
                                          'custom_template.html',
                                          flush=True)
        self.assertEqual(len(context['entries']), 1)
        self.assertEqual(context['template'], 'custom_template.html')

    def test_get_archives_entries(self):
        with self.assertNumQueries(1):
            context = get_archives_entries()
        self.assertEqual(len(context['archives']), 0)
        self.assertEqual(context['template'],
                         'zinnia/tags/archives_entries.html')

        self.publish_entry()
        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'tags': 'zinnia, test',
                  'status': PUBLISHED,
                  'creation_date': datetime(2009, 1, 1),
                  'slug': 'my-second-entry'}
        site = Site.objects.get_current()
        second_entry = Entry.objects.create(**params)
        second_entry.sites.add(site)

        with self.assertNumQueries(0):
            context = get_archives_entries('custom_template.html')
        self.assertEqual(len(context['archives']), 2)
        self.assertEqual(context['archives'][0], datetime(2010, 1, 1))
        self.assertEqual(context['archives'][1], datetime(2009, 1, 1))
        self.assertEqual(context['template'], 'custom_template.html')

    def test_get_archives_tree(self):
        with self.assertNumQueries(1):
            context = get_archives_entries_tree()
        self.assertEqual(len(context['archives']), 0)
        self.assertEqual(context['template'],
                         'zinnia/tags/archives_entries_tree.html')

        self.publish_entry()
        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'tags': 'zinnia, test',
                  'status': PUBLISHED,
                  'creation_date': datetime(2009, 1, 10),
                  'slug': 'my-second-entry'}
        site = Site.objects.get_current()
        second_entry = Entry.objects.create(**params)
        second_entry.sites.add(site)

        with self.assertNumQueries(0):
            context = get_archives_entries_tree('custom_template.html')
        self.assertEqual(len(context['archives']), 2)
        self.assertEqual(context['archives'][0], datetime(2009, 1, 10))
        self.assertEqual(context['archives'][1], datetime(2010, 1, 1))
        self.assertEqual(context['template'], 'custom_template.html')

    def test_get_calendar_entries(self):
        source_context = Context()
        with self.assertNumQueries(3):
            context = get_calendar_entries(source_context)
        self.assertEqual(context['previous_month'], None)
        self.assertEqual(context['next_month'], None)
        self.assertEqual(context['template'], 'zinnia/tags/calendar.html')

        self.publish_entry()
        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context,
                                           template='custom_template.html')
        self.assertEqual(context['previous_month'], datetime(2010, 1, 1))
        self.assertEqual(context['next_month'], None)
        self.assertEqual(context['template'], 'custom_template.html')

        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context, 2009, 1)
        self.assertEqual(context['previous_month'], None)
        self.assertEqual(context['next_month'], datetime(2010, 1, 1))

        source_context = Context({'month': datetime(2009, 1, 1)})
        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context)
        self.assertEqual(context['previous_month'], None)
        self.assertEqual(context['next_month'], datetime(2010, 1, 1))

        source_context = Context({'month': datetime(2010, 1, 1)})
        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context)
        self.assertEqual(context['previous_month'], None)
        self.assertEqual(context['next_month'], None)

        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'tags': 'zinnia, test',
                  'status': PUBLISHED,
                  'creation_date': datetime(2008, 1, 1),
                  'slug': 'my-second-entry'}
        site = Site.objects.get_current()
        second_entry = Entry.objects.create(**params)
        second_entry.sites.add(site)

        source_context = Context()
        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context, 2009, 1)
        self.assertEqual(context['previous_month'], datetime(2008, 1, 1))
        self.assertEqual(context['next_month'], datetime(2010, 1, 1))
        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context)
        self.assertEqual(context['previous_month'], datetime(2010, 1, 1))
        self.assertEqual(context['next_month'], None)

    @skipIfCustomUser
    def test_get_recent_comments(self):
        site = Site.objects.get_current()
        with self.assertNumQueries(1):
            context = get_recent_comments()
        self.assertEqual(len(context['comments']), 0)
        self.assertEqual(context['template'],
                         'zinnia/tags/recent_comments.html')

        comment_1 = comments.get_model().objects.create(
            comment='My Comment 1', site=site,
            content_object=self.entry, submit_date=timezone.now())
        with self.assertNumQueries(1):
            context = get_recent_comments(3, 'custom_template.html')
        self.assertEqual(len(context['comments']), 0)
        self.assertEqual(context['template'], 'custom_template.html')

        self.publish_entry()
        with self.assertNumQueries(3):
            context = get_recent_comments()
            self.assertEqual(len(context['comments']), 1)
            self.assertEqual(context['comments'][0].content_object,
                             self.entry)

        author = Author.objects.create_user(username='webmaster',
                                            email='webmaster@example.com')
        comment_2 = comments.get_model().objects.create(
            comment='My Comment 2', site=site,
            content_object=self.entry, submit_date=timezone.now())
        comment_2.flags.create(user=author,
                               flag=CommentFlag.MODERATOR_APPROVAL)
        with self.assertNumQueries(3):
            context = get_recent_comments()
            self.assertEqual(list(context['comments']),
                             [comment_2, comment_1])
            self.assertEqual(context['comments'][0].content_object,
                             self.entry)
            self.assertEqual(context['comments'][1].content_object,
                             self.entry)

    @skipIfCustomUser
    def test_get_recent_linkbacks(self):
        user = Author.objects.create_user(username='webmaster',
                                          email='webmaster@example.com')
        site = Site.objects.get_current()
        with self.assertNumQueries(1):
            context = get_recent_linkbacks()
        self.assertEqual(len(context['linkbacks']), 0)
        self.assertEqual(context['template'],
                         'zinnia/tags/recent_linkbacks.html')

        linkback_1 = comments.get_model().objects.create(
            comment='My Linkback 1', site=site,
            content_object=self.entry, submit_date=timezone.now())
        linkback_1.flags.create(user=user, flag=PINGBACK)
        with self.assertNumQueries(1):
            context = get_recent_linkbacks(3, 'custom_template.html')
        self.assertEqual(len(context['linkbacks']), 0)
        self.assertEqual(context['template'], 'custom_template.html')

        self.publish_entry()
        with self.assertNumQueries(3):
            context = get_recent_linkbacks()
            self.assertEqual(len(context['linkbacks']), 1)
            self.assertEqual(context['linkbacks'][0].content_object,
                             self.entry)

        linkback_2 = comments.get_model().objects.create(
            comment='My Linkback 2', site=site,
            content_object=self.entry, submit_date=timezone.now())
        linkback_2.flags.create(user=user, flag=TRACKBACK)
        with self.assertNumQueries(3):
            context = get_recent_linkbacks()
            self.assertEqual(list(context['linkbacks']),
                             [linkback_2, linkback_1])
            self.assertEqual(context['linkbacks'][0].content_object,
                             self.entry)
            self.assertEqual(context['linkbacks'][1].content_object,
                             self.entry)

    def test_zinnia_pagination(self):
        class FakeRequest(object):
            def __init__(self, get_dict):
                self.GET = get_dict

        source_context = Context({'request': FakeRequest(
            {'page': '1', 'key': 'val'})})
        paginator = Paginator(range(200), 10)

        with self.assertNumQueries(0):
            context = zinnia_pagination(source_context, paginator.page(1))
        self.assertEqual(context['page'].number, 1)
        self.assertEqual(list(context['begin']), [1, 2, 3])
        self.assertEqual(list(context['middle']), [])
        self.assertEqual(list(context['end']), [18, 19, 20])
        self.assertEqual(context['GET_string'], '&key=val')
        self.assertEqual(context['template'], 'zinnia/tags/pagination.html')

        source_context = Context({'request': FakeRequest({})})
        with self.assertNumQueries(0):
            context = zinnia_pagination(source_context, paginator.page(2))
        self.assertEqual(context['page'].number, 2)
        self.assertEqual(list(context['begin']), [1, 2, 3, 4])
        self.assertEqual(list(context['middle']), [])
        self.assertEqual(list(context['end']), [18, 19, 20])
        self.assertEqual(context['GET_string'], '')

        with self.assertNumQueries(0):
            context = zinnia_pagination(source_context, paginator.page(3))
        self.assertEqual(list(context['begin']), [1, 2, 3, 4, 5])
        self.assertEqual(list(context['middle']), [])
        self.assertEqual(list(context['end']), [18, 19, 20])

        with self.assertNumQueries(0):
            context = zinnia_pagination(source_context, paginator.page(6))
        self.assertEqual(list(context['begin']), [1, 2, 3, 4, 5, 6, 7, 8])
        self.assertEqual(list(context['middle']), [])
        self.assertEqual(list(context['end']), [18, 19, 20])

        with self.assertNumQueries(0):
            context = zinnia_pagination(source_context, paginator.page(11))
        self.assertEqual(list(context['begin']), [1, 2, 3])
        self.assertEqual(list(context['middle']), [9, 10, 11, 12, 13])
        self.assertEqual(list(context['end']), [18, 19, 20])

        with self.assertNumQueries(0):
            context = zinnia_pagination(source_context, paginator.page(15))
        self.assertEqual(list(context['begin']), [1, 2, 3])
        self.assertEqual(list(context['middle']), [])
        self.assertEqual(list(context['end']),
                         [13, 14, 15, 16, 17, 18, 19, 20])

        with self.assertNumQueries(0):
            context = zinnia_pagination(source_context, paginator.page(18))
        self.assertEqual(list(context['begin']), [1, 2, 3])
        self.assertEqual(list(context['middle']), [])
        self.assertEqual(list(context['end']), [16, 17, 18, 19, 20])

        with self.assertNumQueries(0):
            context = zinnia_pagination(source_context, paginator.page(19))
        self.assertEqual(list(context['begin']), [1, 2, 3])
        self.assertEqual(list(context['middle']), [])
        self.assertEqual(list(context['end']), [17, 18, 19, 20])

        with self.assertNumQueries(0):
            context = zinnia_pagination(source_context, paginator.page(20))
        self.assertEqual(list(context['begin']), [1, 2, 3])
        self.assertEqual(list(context['middle']), [])
        self.assertEqual(list(context['end']), [18, 19, 20])

        with self.assertNumQueries(0):
            context = zinnia_pagination(source_context, paginator.page(10),
                                        begin_pages=1, end_pages=3,
                                        before_pages=4, after_pages=3,
                                        template='custom_template.html')
        self.assertEqual(list(context['begin']), [1])
        self.assertEqual(list(context['middle']), [6, 7, 8, 9, 10, 11, 12, 13])
        self.assertEqual(list(context['end']), [18, 19, 20])
        self.assertEqual(context['template'], 'custom_template.html')

        paginator = Paginator(range(50), 10)
        with self.assertNumQueries(0):
            context = zinnia_pagination(source_context, paginator.page(1))
        self.assertEqual(list(context['begin']), [1, 2, 3, 4, 5])
        self.assertEqual(list(context['middle']), [])
        self.assertEqual(list(context['end']), [])

        paginator = Paginator(range(60), 10)
        with self.assertNumQueries(0):
            context = zinnia_pagination(source_context, paginator.page(1))
        self.assertEqual(list(context['begin']), [1, 2, 3, 4, 5, 6])
        self.assertEqual(list(context['middle']), [])
        self.assertEqual(list(context['end']), [])

        paginator = Paginator(range(70), 10)
        with self.assertNumQueries(0):
            context = zinnia_pagination(source_context, paginator.page(1))
        self.assertEqual(list(context['begin']), [1, 2, 3])
        self.assertEqual(list(context['middle']), [])
        self.assertEqual(list(context['end']), [5, 6, 7])

    @skipIfCustomUser
    def test_zinnia_breadcrumbs(self):
        class FakeRequest(object):
            def __init__(self, path):
                self.path = path

        class FakePage(object):
            def __init__(self, number):
                self.number = number

        def check_only_last_have_no_url(crumb_list):
            size = len(crumb_list) - 1
            for i, crumb in enumerate(crumb_list):
                if i != size:
                    self.assertNotEqual(crumb.url, None)
                else:
                    self.assertEqual(crumb.url, None)

        source_context = Context({'request': FakeRequest('/')})
        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 1)
        self.assertEqual(context['breadcrumbs'][0].name, 'Blog')
        self.assertEqual(context['breadcrumbs'][0].url,
                         reverse('zinnia_entry_archive_index'))
        self.assertEqual(context['template'], 'zinnia/tags/breadcrumbs.html')

        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context,
                                         'Weblog', 'custom_template.html')
        self.assertEqual(len(context['breadcrumbs']), 1)
        self.assertEqual(context['breadcrumbs'][0].name, 'Weblog')
        self.assertEqual(context['template'], 'custom_template.html')

        source_context = Context(
            {'request': FakeRequest(self.entry.get_absolute_url()),
             'object': self.entry})
        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 5)
        check_only_last_have_no_url(context['breadcrumbs'])

        cat_1 = Category.objects.create(title='Category 1', slug='category-1')
        source_context = Context(
            {'request': FakeRequest(cat_1.get_absolute_url()),
             'object': cat_1})
        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 3)
        check_only_last_have_no_url(context['breadcrumbs'])
        cat_2 = Category.objects.create(title='Category 2', slug='category-2',
                                        parent=cat_1)
        source_context = Context(
            {'request': FakeRequest(cat_2.get_absolute_url()),
             'object': cat_2})
        with self.assertNumQueries(1):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 4)
        check_only_last_have_no_url(context['breadcrumbs'])

        tag = Tag.objects.get(name='test')
        source_context = Context(
            {'request': FakeRequest(reverse('zinnia_tag_detail',
                                            args=['test'])),
             'object': tag})
        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 3)
        check_only_last_have_no_url(context['breadcrumbs'])

        author = Author.objects.create_user(username='webmaster',
                                            email='webmaster@example.com')
        source_context = Context(
            {'request': FakeRequest(author.get_absolute_url()),
             'object': author})
        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 3)
        check_only_last_have_no_url(context['breadcrumbs'])

        source_context = Context(
            {'request': FakeRequest(reverse(
                'zinnia_entry_archive_year', args=[2011]))})
        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 2)
        check_only_last_have_no_url(context['breadcrumbs'])

        source_context = Context({'request': FakeRequest(reverse(
            'zinnia_entry_archive_month', args=[2011, '03']))})
        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 3)
        check_only_last_have_no_url(context['breadcrumbs'])

        source_context = Context({'request': FakeRequest(reverse(
            'zinnia_entry_archive_week', args=[2011, 15]))})
        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 3)
        check_only_last_have_no_url(context['breadcrumbs'])

        source_context = Context({'request': FakeRequest(reverse(
            'zinnia_entry_archive_day', args=[2011, '03', 15]))})
        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 4)
        check_only_last_have_no_url(context['breadcrumbs'])

        source_context = Context({'request': FakeRequest('%s?page=2' % reverse(
            'zinnia_entry_archive_day', args=[2011, '03', 15])),
            'page_obj': FakePage(2)})
        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 5)
        check_only_last_have_no_url(context['breadcrumbs'])

        source_context = Context({'request': FakeRequest(reverse(
            'zinnia_entry_archive_day_paginated', args=[2011, '03', 15, 2])),
            'page_obj': FakePage(2)})
        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 5)
        check_only_last_have_no_url(context['breadcrumbs'])
        # More tests can be done here, for testing path and objects in context

    def test_get_gravatar(self):
        self.assertTrue(urlEqual(
            get_gravatar('webmaster@example.com'),
            'http://www.gravatar.com/avatar/86d4fd4a22de452'
            'a9228298731a0b592?s=80&amp;r=g'))
        self.assertTrue(urlEqual(
            get_gravatar('  WEBMASTER@example.com  ', 15, 'x', '404'),
            'http://www.gravatar.com/avatar/86d4fd4a22de452'
            'a9228298731a0b592?s=15&amp;r=x&amp;d=404'))
        self.assertTrue(urlEqual(
            get_gravatar('  WEBMASTER@example.com  ', 15, 'x', '404', 'https'),
            'https://secure.gravatar.com/avatar/86d4fd4a22de452'
            'a9228298731a0b592?s=15&amp;r=x&amp;d=404'))

    def test_get_tags(self):
        Tag.objects.create(name='tag')
        t = Template("""
        {% load zinnia_tags %}
        {% get_tags as entry_tags %}
        {{ entry_tags|join:", " }}
        """)
        with self.assertNumQueries(2):
            html = t.render(Context())
        self.assertEqual(html.strip(), '')
        self.publish_entry()
        html = t.render(Context())
        self.assertEqual(html.strip(), 'test, zinnia')

        template_error_as = """
        {% load zinnia_tags %}
        {% get_tags a_s entry_tags %}"""
        self.assertRaises(TemplateSyntaxError, Template, template_error_as)

        template_error_args = """
        {% load zinnia_tags %}
        {% get_tags as entry tags %}"""
        self.assertRaises(TemplateSyntaxError, Template, template_error_args)

    def test_get_tag_cloud(self):
        source_context = Context({})
        with self.assertNumQueries(2):
            context = get_tag_cloud(source_context)
        self.assertEqual(len(context['tags']), 0)
        self.assertEqual(context['template'], 'zinnia/tags/tag_cloud.html')
        self.assertEqual(context['context_tag'], None)
        self.publish_entry()
        tag = Tag.objects.get(name='test')
        source_context = Context({'tag': tag})
        with self.assertNumQueries(1):
            context = get_tag_cloud(source_context, 6, 1,
                                    'custom_template.html')
        self.assertEqual(len(context['tags']), 2)
        self.assertEqual(context['template'], 'custom_template.html')
        self.assertEqual(context['context_tag'], tag)

    def test_widont(self):
        self.assertEqual(
            widont('Word'), 'Word')
        self.assertEqual(
            widont('A complete string'),
            'A complete&nbsp;string')
        self.assertEqual(
            widont('A complete\tstring'),
            'A complete&nbsp;string')
        self.assertEqual(
            widont('A  complete  string'),
            'A  complete&nbsp;string')
        self.assertEqual(
            widont('A complete string with trailing spaces  '),
            'A complete string with trailing&nbsp;spaces  ')
        self.assertEqual(
            widont('A complete string with <markup>', autoescape=False),
            'A complete string with&nbsp;<markup>')
        self.assertEqual(
            widont('A complete string with <markup>', autoescape=True),
            'A complete string with&nbsp;&lt;markup&gt;')

    @skipIfCustomUser
    def test_zinnia_statistics(self):
        with self.assertNumQueries(9):
            context = zinnia_statistics()
        self.assertEqual(context['template'], 'zinnia/tags/statistics.html')
        self.assertEqual(context['entries'], 0)
        self.assertEqual(context['categories'], 0)
        self.assertEqual(context['tags'], 0)
        self.assertEqual(context['authors'], 0)
        self.assertEqual(context['comments'], 0)
        self.assertEqual(context['pingbacks'], 0)
        self.assertEqual(context['trackbacks'], 0)
        self.assertEqual(context['rejects'], 0)
        self.assertEqual(context['words_per_entry'], 0)
        self.assertEqual(context['words_per_comment'], 0)
        self.assertEqual(context['entries_per_month'], 0)
        self.assertEqual(context['comments_per_entry'], 0)
        self.assertEqual(context['linkbacks_per_entry'], 0)

        site = Site.objects.get_current()
        Category.objects.create(title='Category 1', slug='category-1')
        author = Author.objects.create_user(username='webmaster',
                                            email='webmaster@example.com')
        comments.get_model().objects.create(
            comment='My Comment 1', site=site,
            content_object=self.entry,
            submit_date=timezone.now())
        self.entry.authors.add(author)
        self.publish_entry()

        with self.assertNumQueries(13):
            context = zinnia_statistics('custom_template.html')
        self.assertEqual(context['template'], 'custom_template.html')
        self.assertEqual(context['entries'], 1)
        self.assertEqual(context['categories'], 1)
        self.assertEqual(context['tags'], 2)
        self.assertEqual(context['authors'], 1)
        self.assertEqual(context['comments'], 1)
        self.assertEqual(context['pingbacks'], 0)
        self.assertEqual(context['trackbacks'], 0)
        self.assertEqual(context['rejects'], 0)
        self.assertEqual(context['words_per_entry'], 2)
        self.assertEqual(context['words_per_comment'], 3)
        self.assertEqual(context['entries_per_month'], 1)
        self.assertEqual(context['comments_per_entry'], 1)
        self.assertEqual(context['linkbacks_per_entry'], 0)

"""Test cases for Zinnia's templatetags"""
from datetime import date

from django.contrib.sites.models import Site
from django.core.paginator import Paginator
from django.db.models.signals import post_save
from django.template import Context
from django.template import Template
from django.template import TemplateDoesNotExist
from django.template import TemplateSyntaxError
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils import timezone

import django_comments as comments
from django_comments.models import CommentFlag

from tagging.models import Tag

from zinnia.flags import PINGBACK, TRACKBACK
from zinnia.managers import DRAFT
from zinnia.managers import PUBLISHED
from zinnia.models.author import Author
from zinnia.models.category import Category
from zinnia.models.entry import Entry
from zinnia.signals import disconnect_discussion_signals
from zinnia.signals import disconnect_entry_signals
from zinnia.signals import flush_similar_cache_handler
from zinnia.templatetags import zinnia as ztemplatetags
from zinnia.templatetags.zinnia import comment_admin_urlname
from zinnia.templatetags.zinnia import get_archives_entries
from zinnia.templatetags.zinnia import get_archives_entries_tree
from zinnia.templatetags.zinnia import get_authors
from zinnia.templatetags.zinnia import get_calendar_entries
from zinnia.templatetags.zinnia import get_categories
from zinnia.templatetags.zinnia import get_categories_tree
from zinnia.templatetags.zinnia import get_draft_entries
from zinnia.templatetags.zinnia import get_featured_entries
from zinnia.templatetags.zinnia import get_gravatar
from zinnia.templatetags.zinnia import get_popular_entries
from zinnia.templatetags.zinnia import get_random_entries
from zinnia.templatetags.zinnia import get_recent_comments
from zinnia.templatetags.zinnia import get_recent_entries
from zinnia.templatetags.zinnia import get_recent_linkbacks
from zinnia.templatetags.zinnia import get_similar_entries
from zinnia.templatetags.zinnia import get_tag_cloud
from zinnia.templatetags.zinnia import user_admin_urlname
from zinnia.templatetags.zinnia import week_number
from zinnia.templatetags.zinnia import widont
from zinnia.templatetags.zinnia import zinnia_breadcrumbs
from zinnia.templatetags.zinnia import zinnia_loop_template
from zinnia.templatetags.zinnia import zinnia_pagination
from zinnia.templatetags.zinnia import zinnia_statistics
from zinnia.tests.utils import datetime
from zinnia.tests.utils import skip_if_custom_user
from zinnia.tests.utils import url_equal


class TemplateTagsTestCase(TestCase):
    """Test cases for Template tags"""

    def setUp(self):
        disconnect_entry_signals()
        disconnect_discussion_signals()
        params = {'title': 'My entry',
                  'content': 'My content',
                  'tags': 'zinnia, test',
                  'publication_date': datetime(2010, 1, 1, 12),
                  'slug': 'my-entry'}
        self.entry = Entry.objects.create(**params)
        self.site = Site.objects.get_current()

    def publish_entry(self):
        self.entry.status = PUBLISHED
        self.entry.featured = True
        self.entry.sites.add(self.site)
        self.entry.save()

    def make_local(self, date_time):
        """
        Convert aware datetime to local datetime.
        """
        if timezone.is_aware(date_time):
            return timezone.localtime(date_time)
        return date_time

    def test_get_categories(self):
        source_context = Context()
        with self.assertNumQueries(0):
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
        source_context = Context()
        with self.assertNumQueries(0):
            context = get_categories_tree(source_context)
        self.assertEqual(len(context['categories']), 0)
        self.assertEqual(context['template'],
                         'zinnia/tags/categories_tree.html')
        self.assertEqual(context['context_category'], None)

        category = Category.objects.create(title='Category 1',
                                           slug='category-1')
        self.entry.categories.add(category)
        self.publish_entry()
        source_context = Context({'category': category})
        with self.assertNumQueries(0):
            context = get_categories_tree(
                source_context, 'custom_template.html')
        self.assertEqual(len(context['categories']), 1)
        self.assertEqual(context['categories'][0].count_entries, 1)
        self.assertEqual(context['template'], 'custom_template.html')
        self.assertEqual(context['context_category'], category)

    @skip_if_custom_user
    def test_get_authors(self):
        source_context = Context()
        with self.assertNumQueries(0):
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
        with self.assertNumQueries(0):
            context = get_recent_entries()
        self.assertEqual(len(context['entries']), 0)
        self.assertEqual(context['template'],
                         'zinnia/tags/entries_recent.html')

        self.publish_entry()
        with self.assertNumQueries(0):
            context = get_recent_entries(3, 'custom_template.html')
        self.assertEqual(len(context['entries']), 1)
        self.assertEqual(context['template'], 'custom_template.html')
        with self.assertNumQueries(0):
            context = get_recent_entries(0)
        self.assertEqual(len(context['entries']), 0)

    def test_get_featured_entries(self):
        with self.assertNumQueries(0):
            context = get_featured_entries()
        self.assertEqual(len(context['entries']), 0)
        self.assertEqual(context['template'],
                         'zinnia/tags/entries_featured.html')

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
                         'zinnia/tags/entries_draft.html')

        self.publish_entry()
        with self.assertNumQueries(0):
            context = get_draft_entries(3, 'custom_template.html')
        self.assertEqual(len(context['entries']), 0)
        self.assertEqual(context['template'], 'custom_template.html')
        with self.assertNumQueries(0):
            context = get_draft_entries(0)
        self.assertEqual(len(context['entries']), 0)

    def test_get_random_entries(self):
        with self.assertNumQueries(0):
            context = get_random_entries()
        self.assertEqual(len(context['entries']), 0)
        self.assertEqual(context['template'],
                         'zinnia/tags/entries_random.html')

        self.publish_entry()
        with self.assertNumQueries(0):
            context = get_random_entries(3, 'custom_template.html')
        self.assertEqual(len(context['entries']), 1)
        self.assertEqual(context['template'], 'custom_template.html')
        with self.assertNumQueries(0):
            context = get_random_entries(0)
        self.assertEqual(len(context['entries']), 0)

    def test_get_popular_entries(self):
        with self.assertNumQueries(0):
            context = get_popular_entries()
        self.assertEqual(len(context['entries']), 0)
        self.assertEqual(context['template'],
                         'zinnia/tags/entries_popular.html')

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
        second_entry = Entry.objects.create(**params)
        second_entry.sites.add(self.site)
        self.entry.comment_count = 1
        self.entry.save()
        with self.assertNumQueries(0):
            context = get_popular_entries(3)
        self.assertEqual(list(context['entries']), [second_entry, self.entry])

        self.entry.comment_count = 2
        self.entry.save()
        with self.assertNumQueries(0):
            context = get_popular_entries(3)
        self.assertEqual(list(context['entries']), [second_entry, self.entry])

        self.entry.comment_count = 3
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
        post_save.connect(
            flush_similar_cache_handler, sender=Entry,
            dispatch_uid='flush_cache')
        self.publish_entry()
        source_context = Context({'object': self.entry})
        with self.assertNumQueries(0):
            context = get_similar_entries(source_context)
        self.assertEqual(len(context['entries']), 0)
        self.assertEqual(context['template'],
                         'zinnia/tags/entries_similar.html')

        source_context = Context({'entry': self.entry})
        with self.assertNumQueries(1):
            context = get_similar_entries(source_context)
        self.assertEqual(len(context['entries']), 0)
        self.assertEqual(context['template'],
                         'zinnia/tags/entries_similar.html')

        params = {'title': 'My second entry',
                  'content': 'This is the second content of my testing',
                  'excerpt': 'Similarity testing',
                  'status': PUBLISHED,
                  'slug': 'my-second-entry'}
        second_entry = Entry.objects.create(**params)
        second_entry.sites.add(self.site)

        params = {'title': 'My third entry',
                  'content': 'This is the third content for testing',
                  'excerpt': 'Similarity testing',
                  'status': PUBLISHED,
                  'slug': 'my-third-entry'}
        third_entry = Entry.objects.create(**params)
        third_entry.sites.add(self.site)

        with self.assertNumQueries(2):
            context = get_similar_entries(source_context, 3,
                                          'custom_template.html')
        self.assertEqual(len(context['entries']), 2)
        self.assertEqual(context['entries'][0].pk, third_entry.pk)
        self.assertEqual(context['template'], 'custom_template.html')
        with self.assertNumQueries(0):
            context = get_similar_entries(source_context, 3)

        second_site = Site.objects.create(domain='second', name='second')
        second_entry.sites.add(second_site)
        with override_settings(SITE_ID=second_site.pk):
            with self.assertNumQueries(2):
                context = get_similar_entries(source_context, 3)
        self.assertEqual(len(context['entries']), 0)

        source_context = Context({'entry': second_entry})
        with self.assertNumQueries(1):
            context = get_similar_entries(source_context)
        self.assertEqual(len(context['entries']), 2)

        post_save.disconnect(
            sender=Entry, dispatch_uid='flush_cache')

    def test_get_archives_entries(self):
        with self.assertNumQueries(0):
            context = get_archives_entries()
        self.assertEqual(len(context['archives']), 0)
        self.assertEqual(context['template'],
                         'zinnia/tags/entries_archives.html')

        self.publish_entry()
        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'tags': 'zinnia, test',
                  'status': PUBLISHED,
                  'publication_date': datetime(2009, 1, 1),
                  'slug': 'my-second-entry'}
        second_entry = Entry.objects.create(**params)
        second_entry.sites.add(self.site)

        with self.assertNumQueries(0):
            context = get_archives_entries('custom_template.html')
        self.assertEqual(len(context['archives']), 2)

        self.assertEqual(
            context['archives'][0],
            self.make_local(self.entry.publication_date).replace(
                day=1, hour=0))
        self.assertEqual(
            context['archives'][1],
            self.make_local(second_entry.publication_date).replace(
                day=1, hour=0))
        self.assertEqual(context['template'], 'custom_template.html')

    def test_get_archives_tree(self):
        with self.assertNumQueries(0):
            context = get_archives_entries_tree()
        self.assertEqual(len(context['archives']), 0)
        self.assertEqual(context['template'],
                         'zinnia/tags/entries_archives_tree.html')

        self.publish_entry()
        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'tags': 'zinnia, test',
                  'status': PUBLISHED,
                  'publication_date': datetime(2009, 1, 10),
                  'slug': 'my-second-entry'}
        second_entry = Entry.objects.create(**params)
        second_entry.sites.add(self.site)

        with self.assertNumQueries(0):
            context = get_archives_entries_tree('custom_template.html')
        self.assertEqual(len(context['archives']), 2)
        self.assertEqual(
            context['archives'][0],
            self.make_local(
                second_entry.publication_date).replace(hour=0))
        self.assertEqual(
            context['archives'][1],
            self.make_local(
                self.entry.publication_date).replace(hour=0))
        self.assertEqual(context['template'], 'custom_template.html')

    def test_get_calendar_entries_no_params(self):
        source_context = Context()
        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context)
        self.assertEqual(context['previous_month'], None)
        self.assertEqual(context['next_month'], None)
        self.assertEqual(context['template'],
                         'zinnia/tags/entries_calendar.html')

        self.publish_entry()
        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context)
        self.assertEqual(
            context['previous_month'],
            self.make_local(self.entry.publication_date).date().replace(day=1))
        self.assertEqual(context['next_month'], None)

    def test_get_calendar_entries_incomplete_year_month(self):
        self.publish_entry()
        source_context = Context()
        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context, year=2009)
        self.assertEqual(
            context['previous_month'],
            self.make_local(self.entry.publication_date).date().replace(day=1))
        self.assertEqual(context['next_month'], None)

        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context, month=1)
        self.assertEqual(
            context['previous_month'],
            self.make_local(self.entry.publication_date).date().replace(day=1))
        self.assertEqual(context['next_month'], None)

    def test_get_calendar_entries_full_params(self):
        self.publish_entry()
        source_context = Context()
        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context, 2009, 1,
                                           template='custom_template.html')
        self.assertEqual(context['previous_month'], None)
        self.assertEqual(
            context['next_month'],
            self.make_local(self.entry.publication_date).date().replace(day=1))
        self.assertEqual(context['template'], 'custom_template.html')

    def test_get_calendar_entries_no_prev_next(self):
        self.publish_entry()
        source_context = Context()
        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context, 2010, 1)
        self.assertEqual(context['previous_month'], None)
        self.assertEqual(context['next_month'], None)

    def test_get_calendar_entries_month_context(self):
        self.publish_entry()
        source_context = Context({'month': date(2009, 1, 1)})
        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context)
        self.assertEqual(context['previous_month'], None)
        self.assertEqual(
            context['next_month'],
            self.make_local(self.entry.publication_date).date().replace(day=1))

        source_context = Context({'month': date(2010, 6, 1)})
        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context)
        self.assertEqual(
            context['previous_month'],
            self.make_local(self.entry.publication_date).date().replace(day=1))
        self.assertEqual(context['next_month'], None)

        source_context = Context({'month': date(2010, 1, 1)})
        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context)
        self.assertEqual(context['previous_month'], None)
        self.assertEqual(context['next_month'], None)

    def test_get_calendar_entries_week_context(self):
        self.publish_entry()
        source_context = Context({'week': date(2009, 1, 5)})
        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context)
        self.assertEqual(context['previous_month'], None)
        self.assertEqual(
            context['next_month'],
            self.make_local(self.entry.publication_date).date().replace(day=1))

        source_context = Context({'week': date(2010, 5, 31)})
        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context)
        self.assertEqual(
            context['previous_month'],
            self.make_local(self.entry.publication_date).date().replace(day=1))
        self.assertEqual(context['next_month'], None)

        source_context = Context({'week': date(2010, 1, 4)})
        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context)
        self.assertEqual(context['previous_month'], None)
        self.assertEqual(context['next_month'], None)

    def test_get_calendar_entries_day_context(self):
        self.publish_entry()
        source_context = Context({'day': date(2009, 1, 15)})
        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context)
        self.assertEqual(context['previous_month'], None)
        self.assertEqual(
            context['next_month'],
            self.make_local(self.entry.publication_date).date().replace(day=1))

        source_context = Context({'day': date(2010, 6, 15)})
        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context)
        self.assertEqual(
            context['previous_month'],
            self.make_local(self.entry.publication_date).date().replace(day=1))
        self.assertEqual(context['next_month'], None)

        source_context = Context({'day': date(2010, 1, 15)})
        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context)
        self.assertEqual(context['previous_month'], None)
        self.assertEqual(context['next_month'], None)

    def test_get_calendar_entries_object_context(self):
        self.publish_entry()
        source_context = Context({'object': object()})
        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context)
        self.assertEqual(
            context['previous_month'],
            self.make_local(self.entry.publication_date).date().replace(day=1))
        self.assertEqual(context['next_month'], None)

        params = {'title': 'My second entry',
                  'content': 'My second content',
                  'tags': 'zinnia, test',
                  'status': PUBLISHED,
                  'publication_date': datetime(2008, 1, 15),
                  'slug': 'my-second-entry'}
        second_entry = Entry.objects.create(**params)
        second_entry.sites.add(self.site)

        source_context = Context({'object': self.entry})
        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context)
        self.assertEqual(
            context['previous_month'],
            self.make_local(second_entry.publication_date).date().replace(
                day=1))
        self.assertEqual(context['next_month'], None)

        source_context = Context({'object': second_entry})
        with self.assertNumQueries(2):
            context = get_calendar_entries(source_context)
        self.assertEqual(context['previous_month'], None)
        self.assertEqual(
            context['next_month'],
            self.make_local(self.entry.publication_date).date().replace(day=1))

    @skip_if_custom_user
    def test_get_recent_comments(self):
        with self.assertNumQueries(1):
            context = get_recent_comments()
        self.assertEqual(len(context['comments']), 0)
        self.assertEqual(context['template'],
                         'zinnia/tags/comments_recent.html')

        comment_1 = comments.get_model().objects.create(
            comment='My Comment 1', site=self.site,
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
            comment='My Comment 2', site=self.site,
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

    @skip_if_custom_user
    def test_get_recent_linkbacks(self):
        user = Author.objects.create_user(username='webmaster',
                                          email='webmaster@example.com')
        with self.assertNumQueries(1):
            context = get_recent_linkbacks()
        self.assertEqual(len(context['linkbacks']), 0)
        self.assertEqual(context['template'],
                         'zinnia/tags/linkbacks_recent.html')

        linkback_1 = comments.get_model().objects.create(
            comment='My Linkback 1', site=self.site,
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
            comment='My Linkback 2', site=self.site,
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
            context = zinnia_pagination(
                source_context, paginator.page(1),
                begin_pages=3, end_pages=3,
                before_pages=2, after_pages=2)
        self.assertEqual(context['page'].number, 1)
        self.assertEqual(list(context['begin']), [1, 2, 3])
        self.assertEqual(list(context['middle']), [])
        self.assertEqual(list(context['end']), [18, 19, 20])
        self.assertEqual(context['GET_string'], '&key=val')
        self.assertEqual(context['template'], 'zinnia/tags/pagination.html')

        source_context = Context({'request': FakeRequest({})})
        with self.assertNumQueries(0):
            context = zinnia_pagination(
                source_context, paginator.page(2),
                begin_pages=3, end_pages=3,
                before_pages=2, after_pages=2)
        self.assertEqual(context['page'].number, 2)
        self.assertEqual(list(context['begin']), [1, 2, 3, 4])
        self.assertEqual(list(context['middle']), [])
        self.assertEqual(list(context['end']), [18, 19, 20])
        self.assertEqual(context['GET_string'], '')

        with self.assertNumQueries(0):
            context = zinnia_pagination(
                source_context, paginator.page(3),
                begin_pages=3, end_pages=3,
                before_pages=2, after_pages=2)
        self.assertEqual(list(context['begin']), [1, 2, 3, 4, 5])
        self.assertEqual(list(context['middle']), [])
        self.assertEqual(list(context['end']), [18, 19, 20])

        with self.assertNumQueries(0):
            context = zinnia_pagination(
                source_context, paginator.page(6),
                begin_pages=3, end_pages=3,
                before_pages=2, after_pages=2)
        self.assertEqual(list(context['begin']), [1, 2, 3, 4, 5, 6, 7, 8])
        self.assertEqual(list(context['middle']), [])
        self.assertEqual(list(context['end']), [18, 19, 20])

        with self.assertNumQueries(0):
            context = zinnia_pagination(
                source_context, paginator.page(11),
                begin_pages=3, end_pages=3,
                before_pages=2, after_pages=2)
        self.assertEqual(list(context['begin']), [1, 2, 3])
        self.assertEqual(list(context['middle']), [9, 10, 11, 12, 13])
        self.assertEqual(list(context['end']), [18, 19, 20])

        with self.assertNumQueries(0):
            context = zinnia_pagination(
                source_context, paginator.page(15),
                begin_pages=3, end_pages=3,
                before_pages=2, after_pages=2)
        self.assertEqual(list(context['begin']), [1, 2, 3])
        self.assertEqual(list(context['middle']), [])
        self.assertEqual(list(context['end']),
                         [13, 14, 15, 16, 17, 18, 19, 20])

        with self.assertNumQueries(0):
            context = zinnia_pagination(
                source_context, paginator.page(18),
                begin_pages=3, end_pages=3,
                before_pages=2, after_pages=2)
        self.assertEqual(list(context['begin']), [1, 2, 3])
        self.assertEqual(list(context['middle']), [])
        self.assertEqual(list(context['end']), [16, 17, 18, 19, 20])

        with self.assertNumQueries(0):
            context = zinnia_pagination(
                source_context, paginator.page(19),
                begin_pages=3, end_pages=3,
                before_pages=2, after_pages=2)
        self.assertEqual(list(context['begin']), [1, 2, 3])
        self.assertEqual(list(context['middle']), [])
        self.assertEqual(list(context['end']), [17, 18, 19, 20])

        with self.assertNumQueries(0):
            context = zinnia_pagination(
                source_context, paginator.page(20),
                begin_pages=3, end_pages=3,
                before_pages=2, after_pages=2)
        self.assertEqual(list(context['begin']), [1, 2, 3])
        self.assertEqual(list(context['middle']), [])
        self.assertEqual(list(context['end']), [18, 19, 20])

        with self.assertNumQueries(0):
            context = zinnia_pagination(
                source_context, paginator.page(10),
                begin_pages=1, end_pages=3,
                before_pages=4, after_pages=3,
                template='custom_template.html')
        self.assertEqual(list(context['begin']), [1])
        self.assertEqual(list(context['middle']), [6, 7, 8, 9, 10, 11, 12, 13])
        self.assertEqual(list(context['end']), [18, 19, 20])
        self.assertEqual(context['template'], 'custom_template.html')

        paginator = Paginator(range(50), 10)
        with self.assertNumQueries(0):
            context = zinnia_pagination(
                source_context, paginator.page(1),
                begin_pages=3, end_pages=3,
                before_pages=2, after_pages=2)
        self.assertEqual(list(context['begin']), [1, 2, 3, 4, 5])
        self.assertEqual(list(context['middle']), [])
        self.assertEqual(list(context['end']), [])

        paginator = Paginator(range(60), 10)
        with self.assertNumQueries(0):
            context = zinnia_pagination(
                source_context, paginator.page(1),
                begin_pages=3, end_pages=3,
                before_pages=2, after_pages=2)
        self.assertEqual(list(context['begin']), [1, 2, 3, 4, 5, 6])
        self.assertEqual(list(context['middle']), [])
        self.assertEqual(list(context['end']), [])

        paginator = Paginator(range(70), 10)
        with self.assertNumQueries(0):
            context = zinnia_pagination(
                source_context, paginator.page(1),
                begin_pages=3, end_pages=3,
                before_pages=2, after_pages=2)
        self.assertEqual(list(context['begin']), [1, 2, 3])
        self.assertEqual(list(context['middle']), [])
        self.assertEqual(list(context['end']), [5, 6, 7])

    def test_zinnia_pagination_on_my_website(self):
        """
        Reproduce the issue encountred on my website,
        versus the expected result.
        """
        class FakeRequest(object):
            def __init__(self, get_dict={}):
                self.GET = get_dict

        source_context = Context({'request': FakeRequest()})
        paginator = Paginator(range(40), 10)

        with self.assertNumQueries(0):
            for i in range(1, 5):
                context = zinnia_pagination(
                    source_context, paginator.page(i),
                    begin_pages=1, end_pages=1,
                    before_pages=2, after_pages=2)
                self.assertEqual(context['page'].number, i)
                self.assertEqual(list(context['begin']), [1, 2, 3, 4])
                self.assertEqual(list(context['middle']), [])
                self.assertEqual(list(context['end']), [])

    @skip_if_custom_user
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
        self.assertEqual(len(context['breadcrumbs']), 0)
        self.assertEqual(context['template'], 'zinnia/tags/breadcrumbs.html')

        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context, 'Blog')
        self.assertEqual(len(context['breadcrumbs']), 1)
        self.assertEqual(context['breadcrumbs'][0].name, 'Blog')
        self.assertEqual(context['breadcrumbs'][0].url,
                         reverse('zinnia:entry_archive_index'))
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
        self.assertEqual(len(context['breadcrumbs']), 4)
        check_only_last_have_no_url(context['breadcrumbs'])

        cat_1 = Category.objects.create(title='Category 1', slug='category-1')
        source_context = Context(
            {'request': FakeRequest(cat_1.get_absolute_url()),
             'object': cat_1})
        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 2)
        check_only_last_have_no_url(context['breadcrumbs'])
        cat_2 = Category.objects.create(title='Category 2', slug='category-2',
                                        parent=cat_1)
        source_context = Context(
            {'request': FakeRequest(cat_2.get_absolute_url()),
             'object': cat_2})
        with self.assertNumQueries(1):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 3)
        check_only_last_have_no_url(context['breadcrumbs'])

        tag = Tag.objects.get(name='test')
        source_context = Context(
            {'request': FakeRequest(reverse('zinnia:tag_detail',
                                            args=['test'])),
             'object': tag})
        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 2)
        check_only_last_have_no_url(context['breadcrumbs'])

        author = Author.objects.create_user(username='webmaster',
                                            email='webmaster@example.com')
        source_context = Context(
            {'request': FakeRequest(author.get_absolute_url()),
             'object': author})
        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 2)
        check_only_last_have_no_url(context['breadcrumbs'])

        source_context = Context(
            {'request': FakeRequest(reverse(
                'zinnia:entry_archive_year', args=[2011]))})
        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 1)
        check_only_last_have_no_url(context['breadcrumbs'])

        source_context = Context({'request': FakeRequest(reverse(
            'zinnia:entry_archive_month', args=[2011, '03']))})
        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 2)
        check_only_last_have_no_url(context['breadcrumbs'])

        source_context = Context({'request': FakeRequest(reverse(
            'zinnia:entry_archive_week', args=[2011, 15]))})
        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 2)
        check_only_last_have_no_url(context['breadcrumbs'])

        source_context = Context({'request': FakeRequest(reverse(
            'zinnia:entry_archive_day', args=[2011, '03', 15]))})
        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 3)
        check_only_last_have_no_url(context['breadcrumbs'])

        source_context = Context({'request': FakeRequest('%s?page=2' % reverse(
            'zinnia:entry_archive_day', args=[2011, '03', 15])),
            'page_obj': FakePage(2)})
        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 4)
        check_only_last_have_no_url(context['breadcrumbs'])

        source_context = Context({'request': FakeRequest(reverse(
            'zinnia:entry_archive_day_paginated', args=[2011, '03', 15, 2])),
            'page_obj': FakePage(2)})
        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 4)
        check_only_last_have_no_url(context['breadcrumbs'])

        source_context = Context({'request': FakeRequest('/url/')})
        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 1)
        self.assertEqual(context['breadcrumbs'][0].name, 'Url')
        self.assertEqual(context['breadcrumbs'][0].url, None)

        source_context = Context({'request': FakeRequest('/url/path/')})
        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context)
        self.assertEqual(len(context['breadcrumbs']), 1)
        self.assertEqual(context['breadcrumbs'][0].name, 'Path')
        self.assertEqual(context['breadcrumbs'][0].url, None)

        with self.assertNumQueries(0):
            context = zinnia_breadcrumbs(source_context, 'Root')
        self.assertEqual(len(context['breadcrumbs']), 2)
        self.assertEqual(context['breadcrumbs'][0].name, 'Root')
        self.assertEqual(context['breadcrumbs'][0].url,
                         reverse('zinnia:entry_archive_index'))
        self.assertEqual(context['breadcrumbs'][1].name, 'Path')
        self.assertEqual(context['breadcrumbs'][1].url, None)
        # More tests can be done here, for testing path and objects in context

    def test_zinnia_loop_template(self):
        original_entry_loop_templates = ztemplatetags.ENTRY_LOOP_TEMPLATES
        paginator = Paginator(range(50), 10)
        context = Context()

        # Test simple
        template = zinnia_loop_template(
            context, 'zinnia/_entry_detail.html')
        self.assertEqual(template.template.name, 'zinnia/_entry_detail.html')
        self.assertRaisesRegex(
            TemplateDoesNotExist,
            'zinnia/_entry_custom-0.html, '
            'zinnia/_entry_custom_0.html, '
            'zinnia/_entry_custom.html',
            zinnia_loop_template, context, 'zinnia/_entry_custom.html')

        # Test with loop
        context = Context({'forloop': {'counter': 5}})
        self.assertRaisesRegex(
            TemplateDoesNotExist,
            'zinnia/_entry_custom-5.html, '
            'zinnia/_entry_custom_5.html, '
            'zinnia/_entry_custom.html',
            zinnia_loop_template, context, 'zinnia/_entry_custom.html')

        # Test with pagination
        context = Context({'forloop': {'counter': 5},
                           'page_obj': paginator.page(3)})
        self.assertRaisesRegex(
            TemplateDoesNotExist,
            'zinnia/_entry_custom-25.html, '
            'zinnia/_entry_custom_5.html, '
            'zinnia/_entry_custom.html',
            zinnia_loop_template, context, 'zinnia/_entry_custom.html')

        # Test with default key
        ztemplatetags.ENTRY_LOOP_TEMPLATES = {
            'default': {25: 'template.html'}}
        self.assertRaisesRegex(
            TemplateDoesNotExist,
            'template.html, '
            'zinnia/_entry_custom-25.html, '
            'zinnia/_entry_custom_5.html, '
            'zinnia/_entry_custom.html',
            zinnia_loop_template, context, 'zinnia/_entry_custom.html')

        # Test with context
        for context_object_name in ['category', 'tag', 'author',
                                    'year', 'month', 'day']:
            ztemplatetags.ENTRY_LOOP_TEMPLATES = {
                'slug': {25: 'template-slug.html'},
                context_object_name: {25: 'template-%s.html' %
                                      context_object_name},
                '%s-slug' % context_object_name:
                    {25: 'template-%s-slug.html' % context_object_name}}
            context = Context(
                {'forloop': {'counter': 5},
                 'page_obj': paginator.page(3),
                 context_object_name: 'slug'})
            self.assertRaisesRegex(
                TemplateDoesNotExist,
                'template-%s-slug.html, '
                'template-slug.html, '
                'template-%s.html, '
                'zinnia/_entry_custom-25.html, '
                'zinnia/_entry_custom_5.html, '
                'zinnia/_entry_custom.html' % (
                    context_object_name, context_object_name),
                zinnia_loop_template,
                context, 'zinnia/_entry_custom.html')
        ztemplatetags.ENTRY_LOOP_TEMPLATES = original_entry_loop_templates

    def test_get_gravatar(self):
        self.assertTrue(url_equal(
            get_gravatar('webmaster@example.com'),
            'http://www.gravatar.com/avatar/86d4fd4a22de452'
            'a9228298731a0b592?s=80&amp;r=g'))
        self.assertTrue(url_equal(
            get_gravatar('  WEBMASTER@example.com  ', 15, 'x', '404'),
            'http://www.gravatar.com/avatar/86d4fd4a22de452'
            'a9228298731a0b592?s=15&amp;r=x&amp;d=404'))
        self.assertTrue(url_equal(
            get_gravatar('  WEBMASTER@example.com  ', 15, 'x', '404', 'https'),
            'https://secure.gravatar.com/avatar/86d4fd4a22de452'
            'a9228298731a0b592?s=15&amp;r=x&amp;d=404'))

    def test_get_tags(self):
        Tag.objects.create(name='tag')
        t = Template("""
        {% load zinnia %}
        {% get_tags as entry_tags %}
        {{ entry_tags|join:", " }}
        """)
        with self.assertNumQueries(1):
            html = t.render(Context())
        self.assertEqual(html.strip(), '')
        self.publish_entry()
        html = t.render(Context())
        self.assertEqual(html.strip(), 'test, zinnia')

        template_error_as = """
        {% load zinnia %}
        {% get_tags a_s entry_tags %}"""
        self.assertRaises(TemplateSyntaxError, Template, template_error_as)

        template_error_args = """
        {% load zinnia %}
        {% get_tags as entry tags %}"""
        self.assertRaises(TemplateSyntaxError, Template, template_error_args)

    def test_get_tag_cloud(self):
        source_context = Context()
        with self.assertNumQueries(1):
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

    def test_widont_pre_punctuation(self):
        """
        In some languages like French, applying the widont filter
        before a punctuation sign preceded by a space, leads to
        ugly visual results, instead of a better visual results.
        """
        self.assertEqual(
            widont('Releases : django-blog-zinnia'),
            'Releases&nbsp;:&nbsp;django-blog-zinnia')
        self.assertEqual(
            widont('Releases ; django-blog-zinnia'),
            'Releases&nbsp;;&nbsp;django-blog-zinnia')
        self.assertEqual(
            widont('Releases ! django-blog-zinnia'),
            'Releases&nbsp;!&nbsp;django-blog-zinnia')
        self.assertEqual(
            widont('Releases ? django-blog-zinnia'),
            'Releases&nbsp;?&nbsp;django-blog-zinnia')
        self.assertEqual(
            widont('Releases - django-blog-zinnia'),
            'Releases&nbsp;-&nbsp;django-blog-zinnia')
        self.assertEqual(
            widont('Releases + django-blog-zinnia'),
            'Releases&nbsp;+&nbsp;django-blog-zinnia')
        self.assertEqual(
            widont('Releases * django-blog-zinnia'),
            'Releases&nbsp;*&nbsp;django-blog-zinnia')
        self.assertEqual(
            widont('Releases / django-blog-zinnia'),
            'Releases&nbsp;/&nbsp;django-blog-zinnia')
        self.assertEqual(
            widont('Releases % django-blog-zinnia'),
            'Releases&nbsp;%&nbsp;django-blog-zinnia')
        self.assertEqual(
            widont('Releases = django-blog-zinnia'),
            'Releases&nbsp;=&nbsp;django-blog-zinnia')
        self.assertEqual(
            widont('Releases   :   django-blog-zinnia  '),
            'Releases&nbsp;:&nbsp;django-blog-zinnia  ')
        self.assertEqual(
            widont('Releases :: django-blog-zinnia'),
            'Releases&nbsp;::&nbsp;django-blog-zinnia')
        self.assertEqual(
            widont('Releases :z django-blog-zinnia'),
            'Releases :z&nbsp;django-blog-zinnia')

    def test_widont_post_punctuation(self):
        """
        Sometimes applying the widont filter on just a punctuation sign,
        leads to ugly visual results, instead of better visual results.
        """
        self.assertEqual(
            widont('Move !'),
            'Move&nbsp;!')
        self.assertEqual(
            widont('Move it   !  '),
            'Move&nbsp;it&nbsp;!  ')
        self.assertEqual(
            widont('Move it ?'),
            'Move&nbsp;it&nbsp;?')
        self.assertEqual(
            widont('I like to move : it !'),
            'I like to move&nbsp;:&nbsp;it&nbsp;!')
        self.assertEqual(
            widont('I like to : move it !'),
            'I like to : move&nbsp;it&nbsp;!')

    def test_week_number(self):
        self.assertEqual(week_number(datetime(2013, 1, 1)), '0')
        self.assertEqual(week_number(datetime(2013, 12, 21)), '50')

    def test_comment_admin_urlname(self):
        comment_admin_url = comment_admin_urlname('action')
        self.assertTrue(comment_admin_url.startswith('admin:'))
        self.assertTrue(comment_admin_url.endswith('_action'))

    @skip_if_custom_user
    def test_user_admin_urlname(self):
        user_admin_url = user_admin_urlname('action')
        self.assertEqual(user_admin_url, 'admin:auth_user_action')

    @skip_if_custom_user
    def test_zinnia_statistics(self):
        with self.assertNumQueries(8):
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

        Category.objects.create(title='Category 1', slug='category-1')
        author = Author.objects.create_user(username='webmaster',
                                            email='webmaster@example.com')
        comments.get_model().objects.create(
            comment='My Comment 1', site=self.site,
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


class TemplateTagsTimezoneTestCase(TestCase):

    def create_published_entry_at(self, publication_date):
        params = {'title': 'My entry',
                  'content': 'My content',
                  'slug': 'my-entry',
                  'status': PUBLISHED,
                  'publication_date': publication_date}
        entry = Entry.objects.create(**params)
        entry.sites.add(Site.objects.get_current())
        return entry

    @override_settings(USE_TZ=False)
    def test_calendar_entries_no_timezone(self):
        template = Template('{% load zinnia %}'
                            '{% get_calendar_entries 2014 1 %}')
        self.create_published_entry_at(datetime(2014, 1, 1, 12, 0))
        self.create_published_entry_at(datetime(2014, 1, 1, 23, 0))
        self.create_published_entry_at(datetime(2012, 12, 31, 23, 0))
        self.create_published_entry_at(datetime(2014, 1, 31, 23, 0))
        output = template.render(Context())
        self.assertTrue('/2014/01/01/' in output)
        self.assertTrue('/2014/01/02/' not in output)
        self.assertTrue('/2012/12/' in output)
        self.assertTrue('/2014/02/' not in output)

    @override_settings(USE_TZ=True, TIME_ZONE='Europe/Paris')
    def test_calendar_entries_with_timezone(self):
        template = Template('{% load zinnia %}'
                            '{% get_calendar_entries 2014 1 %}')
        self.create_published_entry_at(datetime(2014, 1, 1, 12, 0))
        self.create_published_entry_at(datetime(2014, 1, 1, 23, 0))
        self.create_published_entry_at(datetime(2012, 12, 31, 23, 0))
        self.create_published_entry_at(datetime(2014, 1, 31, 23, 0))
        output = template.render(Context())
        self.assertTrue('/2014/01/01/' in output)
        self.assertTrue('/2014/01/02/' in output)
        self.assertTrue('/2013/01/' in output)
        self.assertTrue('/2014/02/' in output)

    @override_settings(USE_TZ=False)
    def test_archives_entries_no_timezone(self):
        template = Template('{% load zinnia %}'
                            '{% get_archives_entries %}')
        self.create_published_entry_at(datetime(2014, 1, 1, 12, 0))
        self.create_published_entry_at(datetime(2014, 1, 31, 23, 0))
        output = template.render(Context())
        self.assertTrue('/2014/01/' in output)
        self.assertTrue('/2014/02/' not in output)

    @override_settings(USE_TZ=True, TIME_ZONE='Europe/Paris')
    def test_archives_entries_with_timezone(self):
        template = Template('{% load zinnia %}'
                            '{% get_archives_entries %}')
        self.create_published_entry_at(datetime(2014, 1, 1, 12, 0))
        self.create_published_entry_at(datetime(2014, 1, 31, 23, 0))
        output = template.render(Context())
        self.assertTrue('/2014/01/' in output)
        self.assertTrue('/2014/02/' in output)

    @override_settings(USE_TZ=False)
    def test_archives_entries_tree_no_timezone(self):
        template = Template('{% load zinnia %}'
                            '{% get_archives_entries_tree %}')
        self.create_published_entry_at(datetime(2014, 1, 1, 12, 0))
        self.create_published_entry_at(datetime(2014, 1, 31, 23, 0))
        output = template.render(Context())
        self.assertTrue('/2014/01/01/' in output)
        self.assertTrue('/2014/02/01/' not in output)

    @override_settings(USE_TZ=True, TIME_ZONE='Europe/Paris')
    def test_archives_entries_tree_with_timezone(self):
        template = Template('{% load zinnia %}'
                            '{% get_archives_entries_tree %}')
        self.create_published_entry_at(datetime(2014, 1, 1, 12, 0))
        self.create_published_entry_at(datetime(2014, 1, 31, 23, 0))
        output = template.render(Context())
        self.assertTrue('/2014/01/01/' in output)
        self.assertTrue('/2014/02/01/' in output)

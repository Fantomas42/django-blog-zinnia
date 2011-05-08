"""Template tags and filters for Zinnia"""
from hashlib import md5
from random import sample
from urllib import urlencode
from datetime import datetime

from django.db.models import Q
from django.db import connection
from django.template import Library
from django.contrib.comments.models import Comment
from django.contrib.comments.models import CommentFlag
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_unicode

from zinnia.models import Entry
from zinnia.models import Author
from zinnia.models import Category
from zinnia.comparison import VectorBuilder
from zinnia.comparison import pearson_score
from zinnia.templatetags.zcalendar import ZinniaCalendar
from zinnia.templatetags.zbreadcrumbs import retrieve_breadcrumbs

register = Library()

VECTORS = None
VECTORS_FACTORY = lambda: VectorBuilder(Entry.published.all(),
                                        ['title', 'excerpt', 'content'])
CACHE_ENTRIES_RELATED = {}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_categories(template='zinnia/tags/categories.html'):
    """Return the categories"""
    return {'template': template,
            'categories': Category.tree.all()}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_authors(template='zinnia/tags/authors.html'):
    """Return the published authors"""
    return {'template': template,
            'authors': Author.published.all()}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_recent_entries(number=5, template='zinnia/tags/recent_entries.html'):
    """Return the most recent entries"""
    return {'template': template,
            'entries': Entry.published.all()[:number]}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_featured_entries(number=5,
                         template='zinnia/tags/featured_entries.html'):
    """Return the featured entries"""
    return {'template': template,
            'entries': Entry.published.filter(featured=True)[:number]}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_random_entries(number=5, template='zinnia/tags/random_entries.html'):
    """Return random entries"""
    entries = Entry.published.all()
    if number > len(entries):
        number = len(entries)
    return {'template': template,
            'entries': sample(entries, number)}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_popular_entries(number=5, template='zinnia/tags/popular_entries.html'):
    """Return popular  entries"""
    ctype = ContentType.objects.get_for_model(Entry)
    query = """SELECT object_pk, COUNT(*) AS score
    FROM %s
    WHERE content_type_id = %%s
    AND is_public = '1'
    GROUP BY object_pk
    ORDER BY score DESC""" % Comment._meta.db_table

    cursor = connection.cursor()
    cursor.execute(query, [ctype.id])
    object_ids = [int(row[0]) for row in cursor.fetchall()]

    # Use ``in_bulk`` here instead of an ``id__in`` filter, because ``id__in``
    # would clobber the ordering.
    object_dict = Entry.published.in_bulk(object_ids)

    return {'template': template,
            'entries': [object_dict[object_id]
                        for object_id in object_ids
                        if object_id in object_dict][:number]}


@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def get_similar_entries(context, number=5,
                        template='zinnia/tags/similar_entries.html',
                        flush=False):
    """Return similar entries"""
    global VECTORS
    global CACHE_ENTRIES_RELATED

    if VECTORS is None or flush:
        VECTORS = VECTORS_FACTORY()
        CACHE_ENTRIES_RELATED = {}

    def compute_related(object_id, dataset):
        """Compute related entries to an entry with a dataset"""
        object_vector = None
        for entry, e_vector in dataset.items():
            if entry.pk == object_id:
                object_vector = e_vector

        if not object_vector:
            return []

        entry_related = {}
        for entry, e_vector in dataset.items():
            if entry.pk != object_id:
                score = pearson_score(object_vector, e_vector)
                if score:
                    entry_related[entry] = score

        related = sorted(entry_related.items(), key=lambda(k, v): (v, k))
        return [rel[0] for rel in related]

    object_id = context['object'].pk
    columns, dataset = VECTORS()
    key = '%s-%s' % (object_id, VECTORS.key)
    if not key in CACHE_ENTRIES_RELATED.keys():
        CACHE_ENTRIES_RELATED[key] = compute_related(object_id, dataset)

    entries = CACHE_ENTRIES_RELATED[key][:number]
    return {'template': template,
            'entries': entries}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_archives_entries(template='zinnia/tags/archives_entries.html'):
    """Return archives entries"""
    return {'template': template,
            'archives': Entry.published.dates('creation_date', 'month',
                                              order='DESC')}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_archives_entries_tree(
    template='zinnia/tags/archives_entries_tree.html'):
    """Return archives entries as a Tree"""
    return {'template': template,
            'archives': Entry.published.dates('creation_date', 'day',
                                              order='ASC')}


@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def get_calendar_entries(context, year=None, month=None,
                         template='zinnia/tags/calendar.html'):
    """Return an HTML calendar of entries"""
    if not year or not month:
        date_month = context.get('month') or context.get('day') or \
                     getattr(context.get('object'), 'creation_date', None) or \
                     datetime.today()
        year, month = date_month.timetuple()[:2]

    calendar = ZinniaCalendar()
    current_month = datetime(year, month, 1)

    dates = list(Entry.published.dates('creation_date', 'month'))

    if not current_month in dates:
        dates.append(current_month)
        dates.sort()
    index = dates.index(current_month)

    previous_month = index > 0 and dates[index - 1] or None
    next_month = index != len(dates) - 1 and dates[index + 1] or None

    return {'template': template,
            'next_month': next_month,
            'previous_month': previous_month,
            'calendar': calendar.formatmonth(year, month)}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_recent_comments(number=5, template='zinnia/tags/recent_comments.html'):
    """Return the most recent comments"""
    # Using map(smart_unicode... fix bug related to issue #8554
    entry_published_pks = map(smart_unicode,
                              Entry.published.values_list('id', flat=True))
    content_type = ContentType.objects.get_for_model(Entry)

    comments = Comment.objects.filter(
        Q(flags=None) | Q(flags__flag=CommentFlag.MODERATOR_APPROVAL),
        content_type=content_type, object_pk__in=entry_published_pks,
        is_public=True).order_by('-submit_date')[:number]

    return {'template': template,
            'comments': comments}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_recent_linkbacks(number=5,
                         template='zinnia/tags/recent_linkbacks.html'):
    """Return the most recent linkbacks"""
    entry_published_pks = map(smart_unicode,
                              Entry.published.values_list('id', flat=True))
    content_type = ContentType.objects.get_for_model(Entry)

    linkbacks = Comment.objects.filter(
        content_type=content_type,
        object_pk__in=entry_published_pks,
        flags__flag__in=['pingback', 'trackback'],
        is_public=True).order_by(
        '-submit_date')[:number]

    return {'template': template,
            'linkbacks': linkbacks}


@register.inclusion_tag('zinnia/tags/dummy.html')
def zinnia_pagination(page, begin_pages=3, end_pages=3,
               before_pages=2, after_pages=2,
               template='zinnia/tags/pagination.html'):
    """Return a Digg-like pagination, by splitting long list of page
    into 3 blocks of pages"""
    begin = page.paginator.page_range[:begin_pages]
    end = page.paginator.page_range[-end_pages:]
    middle = page.paginator.page_range[max(page.number - before_pages - 1, 0):
                                       page.number + after_pages]

    if set(begin) & set(end):  # [1, 2, 3], [...], [2, 3, 4]
        begin = sorted(set(begin + end))  # [1, 2, 3, 4]
        middle, end = [], []
    elif set(begin) & set(middle):  # [1, 2, 3], [2, 3, 4]
        begin = sorted(set(begin + middle))  # [1, 2, 3, 4]
        middle = []
    elif begin[-1] + 1 == middle[0]:  # [1, 2, 3], [4, 5, 6]
        begin += middle  # [1, 2, 3, 4, 5, 6]
        middle = []
    elif end[0] - 1 == middle[-1]:  # [18, 19, 20], [15, 16, 17]
        end = middle + end  # [15, 16, 17, 18, 19, 20]
        middle = []
    elif set(middle) & set(end):  # [17, 18, 19], [18, 19, 20]
        end = sorted(set(middle + end))  # [17, 18, 19, 20]
        middle = []

    return {'template': template, 'page': page,
            'begin': begin, 'middle': middle, 'end': end}


@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def zinnia_breadcrumbs(context, separator='/', root_name='Blog',
                       template='zinnia/tags/breadcrumbs.html',):
    """Return a breadcrumb for the application"""
    path = context['request'].path
    page_object = context.get('object') or context.get('category') or \
                  context.get('tag') or context.get('author')
    breadcrumbs = retrieve_breadcrumbs(path, page_object, root_name)

    return {'template': template,
            'separator': separator,
            'breadcrumbs': breadcrumbs}


@register.simple_tag
def get_gravatar(email, size=80, rating='g', default=None):
    """Return url for a Gravatar"""
    url = 'http://www.gravatar.com/avatar/%s.jpg' % \
          md5(email.strip().lower()).hexdigest()
    options = {'s': size, 'r': rating}
    if default:
        options['d'] = default

    url = '%s?%s' % (url, urlencode(options))
    return url.replace('&', '&amp;')

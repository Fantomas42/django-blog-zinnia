"""Template tags for Zinnia"""
try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5

from random import sample
from urllib import urlencode
from datetime import datetime

from django.template import Library
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType

from zinnia.models import Entry
from zinnia.models import Category
from zinnia.settings import FIRST_WEEK_DAY
from zinnia.comparison import VectorBuilder
from zinnia.comparison import pearson_score

register = Library()

vectors = VectorBuilder({'queryset': Entry.published.all(),
                        'fields': ['title', 'excerpt', 'content']})
cache_entries_related = {}

@register.inclusion_tag('zinnia/tags/dummy.html')
def get_categories(template='zinnia/tags/categories.html'):
    """Return the categories"""
    return {'template': template,
            'categories': Category.tree.all()}

@register.inclusion_tag('zinnia/tags/dummy.html')
def get_recent_entries(number=5, template='zinnia/tags/recent_entries.html'):
    """Return the most recent entries"""
    return {'template': template,
            'entries': Entry.published.all()[:number]}

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
    from django.db import connection
    from django.contrib.comments.models import Comment
    from django.contrib.contenttypes.models import ContentType

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
            'entries': object_dict.values()[:number]}

@register.inclusion_tag('zinnia/tags/dummy.html',
                        takes_context=True)
def get_similar_entries(context, number=5, template='zinnia/tags/similar_entries.html'):
    """Return similar entries"""
    global vectors
    global cache_entries_related

    def compute_related(object_id, dataset):
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

        related = sorted(entry_related.items(), key=lambda(k,v):(v,k))
        return [i for i, s in related]

    object_id = context['object'].pk
    columns, dataset = vectors()
    key = '%s-%s' % (object_id, vectors.key)
    if not key in cache_entries_related.keys():
        cache_entries_related[key] = compute_related(object_id, dataset)

    entries = cache_entries_related[key][:number]
    return {'template': template,
            'entries': entries}

@register.inclusion_tag('zinnia/tags/dummy.html')
def get_archives_entries(template='zinnia/tags/archives_entries.html'):
    """Return archives entries"""
    return {'template': template,
            'archives': Entry.published.dates('creation_date', 'month',
                                              order='DESC'),}

@register.inclusion_tag('zinnia/tags/dummy.html',
                        takes_context=True)
def get_calendar_entries(context, year=None, month=None,
                         template='zinnia/tags/calendar.html'):
    """Return an HTML calendar of entries"""
    if not year or not month:
        date_month = context.get('month') or context.get('day') or datetime.today()
        year, month = date_month.timetuple()[:2]

    try:
        from zinnia.templatetags.zcalendar import ZinniaCalendar
    except ImportError:
        return {'calendar': '<p class="notice">Calendar is unavailable for Python<2.5.</p>'}

    calendar = ZinniaCalendar(firstweekday=FIRST_WEEK_DAY)
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
    entry_published_pks = Entry.published.values_list('id', flat=True)
    ct = ContentType.objects.get_for_model(Entry)

    comments = Comment.objects.filter(
        content_type=ct, object_pk__in=entry_published_pks,
        flags__flag=None, is_public=True).order_by(
        '-submit_date')[:number]

    return {'template': template,
            'comments': comments}

@register.inclusion_tag('zinnia/tags/dummy.html',
                        takes_context=True)
def zinnia_breadcrumbs(context, separator='/', root_name='Blog',
                       template='zinnia/tags/breadcrumbs.html',):
    """Return a breadcrumb for the application"""
    from zinnia.templatetags.zbreadcrumbs import retrieve_breadcrumbs

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


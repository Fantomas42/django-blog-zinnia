"""Template tags and filters for Zinnia"""
import re
from hashlib import md5
from datetime import datetime
try:
    from urllib.parse import urlencode
except ImportError:  # Python 2
    from urllib import urlencode

from django.db.models import Q
from django.db.models import Count
from django.conf import settings
from django.utils import timezone
from django.template import Library
from django.utils.encoding import smart_text
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.template.defaultfilters import stringfilter
from django.contrib.comments.models import CommentFlag
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments import get_model as get_comment_model

from tagging.models import Tag
from tagging.utils import calculate_cloud

from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.models.category import Category
from zinnia.managers import DRAFT
from zinnia.managers import tags_published
from zinnia.flags import PINGBACK, TRACKBACK
from zinnia.settings import PROTOCOL
from zinnia.comparison import VectorBuilder
from zinnia.comparison import pearson_score
from zinnia.templatetags.zcalendar import ZinniaCalendar
from zinnia.templatetags.zbreadcrumbs import retrieve_breadcrumbs

register = Library()

VECTORS = None
VECTORS_FACTORY = lambda: VectorBuilder(Entry.published.all(),
                                        ['title', 'excerpt', 'content'])
CACHE_ENTRIES_RELATED = {}

WIDONT_REGEXP = re.compile(r'\s+(\S+\s*)$')


@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def get_categories(context, template='zinnia/tags/categories.html'):
    """Return the published categories"""
    return {'template': template,
            'categories': Category.published.all().annotate(
                count_entries_published=Count('entries')),
            'context_category': context.get('category')}


@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def get_categories_tree(context, template='zinnia/tags/categories_tree.html'):
    """Return the categories as a tree"""
    return {'template': template,
            'categories': Category.objects.all(),
            'context_category': context.get('category')}


@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def get_authors(context, template='zinnia/tags/authors.html'):
    """Return the published authors"""
    return {'template': template,
            'authors': Author.published.all().annotate(
                count_entries_published=Count('entries')),
            'context_author': context.get('author')}


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
def get_draft_entries(number=5,
                      template='zinnia/tags/draft_entries.html'):
    """Return the latest draft entries"""
    return {'template': template,
            'entries': Entry.objects.filter(status=DRAFT)[:number]}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_random_entries(number=5, template='zinnia/tags/random_entries.html'):
    """Return random entries"""
    return {'template': template,
            'entries': Entry.published.order_by('?')[:number]}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_popular_entries(number=5, template='zinnia/tags/popular_entries.html'):
    """Return popular entries"""
    return {'template': template,
            'entries': Entry.published.filter(
                comment_count__gt=0).order_by(
                    '-comment_count')[:number]}


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

        related = sorted(entry_related.items(),
                         key=lambda k_v: (k_v[1], k_v[0]))
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
            timezone.now().date()
        year, month = date_month.timetuple()[:2]

    calendar = ZinniaCalendar()
    current_month = datetime(year, month, 1)
    if settings.USE_TZ:
        current_month = timezone.make_aware(
            current_month, timezone.utc)

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
            'calendar': calendar.formatmonth(
                year, month, previous_month=previous_month,
                next_month=next_month)}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_recent_comments(number=5, template='zinnia/tags/recent_comments.html'):
    """Return the most recent comments"""
    # Using map(smart_text... fix bug related to issue #8554
    entry_published_pks = map(smart_text,
                              Entry.published.values_list('id', flat=True))
    content_type = ContentType.objects.get_for_model(Entry)

    comments = get_comment_model().objects.filter(
        Q(flags=None) | Q(flags__flag=CommentFlag.MODERATOR_APPROVAL),
        content_type=content_type, object_pk__in=entry_published_pks,
        is_public=True).order_by('-submit_date')[:number]

    comments = comments.prefetch_related('content_object')

    return {'template': template,
            'comments': comments}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_recent_linkbacks(number=5,
                         template='zinnia/tags/recent_linkbacks.html'):
    """Return the most recent linkbacks"""
    entry_published_pks = map(smart_text,
                              Entry.published.values_list('id', flat=True))
    content_type = ContentType.objects.get_for_model(Entry)

    linkbacks = get_comment_model().objects.filter(
        content_type=content_type,
        object_pk__in=entry_published_pks,
        flags__flag__in=[PINGBACK, TRACKBACK],
        is_public=True).order_by('-submit_date')[:number]

    linkbacks = linkbacks.prefetch_related('content_object')

    return {'template': template,
            'linkbacks': linkbacks}


@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def zinnia_pagination(context, page, begin_pages=3, end_pages=3,
                      before_pages=2, after_pages=2,
                      template='zinnia/tags/pagination.html'):
    """Return a Digg-like pagination, by splitting long list of page
    into 3 blocks of pages"""
    GET_string = ''
    for key, value in context['request'].GET.items():
        if key != 'page':
            GET_string += '&%s=%s' % (key, value)

    begin = page.paginator.page_range[:begin_pages]
    end = page.paginator.page_range[-end_pages:]
    middle = page.paginator.page_range[max(page.number - before_pages - 1, 0):
                                       page.number + after_pages]

    if set(begin) & set(end):  # [1, 2, 3], [...], [2, 3, 4]
        begin = sorted(set(begin + end))  # [1, 2, 3, 4]
        middle, end = [], []
    elif begin[-1] + 1 == end[0]:  # [1, 2, 3], [...], [4, 5, 6]
        begin += end  # [1, 2, 3, 4, 5, 6]
        middle, end = [], []
    elif set(begin) & set(middle):  # [1, 2, 3], [2, 3, 4], [...]
        begin = sorted(set(begin + middle))  # [1, 2, 3, 4]
        middle = []
    elif begin[-1] + 1 == middle[0]:  # [1, 2, 3], [4, 5, 6], [...]
        begin += middle  # [1, 2, 3, 4, 5, 6]
        middle = []
    elif middle[-1] + 1 == end[0]:  # [...], [15, 16, 17], [18, 19, 20]
        end = middle + end  # [15, 16, 17, 18, 19, 20]
        middle = []
    elif set(middle) & set(end):  # [...], [17, 18, 19], [18, 19, 20]
        end = sorted(set(middle + end))  # [17, 18, 19, 20]
        middle = []

    return {'template': template, 'page': page, 'GET_string': GET_string,
            'begin': begin, 'middle': middle, 'end': end}


@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def zinnia_breadcrumbs(context, root_name='Blog',
                       template='zinnia/tags/breadcrumbs.html',):
    """Return a breadcrumb for the application"""
    path = context['request'].path
    context_object = context.get('object') or context.get('category') or \
        context.get('tag') or context.get('author')
    context_page = context.get('page_obj')
    breadcrumbs = retrieve_breadcrumbs(path, context_object,
                                       context_page, root_name)

    return {'template': template,
            'breadcrumbs': breadcrumbs}


@register.simple_tag
def get_gravatar(email, size=80, rating='g', default=None,
                 protocol=PROTOCOL):
    """Return url for a Gravatar"""
    GRAVATAR_PROTOCOLS = {'http': 'http://www',
                          'https': 'https://secure'}
    url = '%s.gravatar.com/avatar/%s.jpg' % (
        GRAVATAR_PROTOCOLS[protocol],
        md5(email.strip().lower()).hexdigest())
    options = {'s': size, 'r': rating}
    if default:
        options['d'] = default

    url = '%s?%s' % (url, urlencode(options))
    return url.replace('&', '&amp;')


@register.assignment_tag
def get_tags():
    """Return the published tags"""
    return Tag.objects.usage_for_queryset(
        Entry.published.all())


@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def get_tag_cloud(context, steps=6, min_count=None,
                  template='zinnia/tags/tag_cloud.html'):
    """Return a cloud of published tags"""
    tags = Tag.objects.usage_for_queryset(
        Entry.published.all(), counts=True,
        min_count=min_count)
    return {'template': template,
            'tags': calculate_cloud(tags, steps),
            'context_tag': context.get('tag')}


@register.filter(needs_autoescape=True)
@stringfilter
def widont(value, autoescape=None):
    """Adds an HTML non-breaking space between the final
    two words of the string to avoid "widowed" words"""
    esc = autoescape and conditional_escape or (lambda x: x)

    def replace(matchobj):
        return u'&nbsp;%s' % matchobj.group(1)

    value = WIDONT_REGEXP.sub(replace, esc(smart_text(value)))
    return mark_safe(value)


@register.inclusion_tag('zinnia/tags/dummy.html')
def zinnia_statistics(template='zinnia/tags/statistics.html'):
    """Return statistics on the content of Zinnia"""
    content_type = ContentType.objects.get_for_model(Entry)
    discussions = get_comment_model().objects.filter(
        content_type=content_type)

    entries = Entry.published
    categories = Category.objects
    tags = tags_published()
    authors = Author.published
    replies = discussions.filter(
        flags=None, is_public=True)
    pingbacks = discussions.filter(
        flags__flag=PINGBACK, is_public=True)
    trackbacks = discussions.filter(
        flags__flag=TRACKBACK, is_public=True)
    rejects = discussions.filter(is_public=False)

    entries_count = entries.count()
    replies_count = replies.count()
    pingbacks_count = pingbacks.count()
    trackbacks_count = trackbacks.count()

    if entries_count:
        first_entry = entries.order_by('creation_date')[0]
        last_entry = entries.latest()
        months_count = (last_entry.creation_date -
                        first_entry.creation_date).days / 31.0
        entries_per_month = entries_count / (months_count or 1.0)

        comments_per_entry = float(replies_count) / entries_count
        linkbacks_per_entry = float(pingbacks_count + trackbacks_count) / \
            entries_count

        total_words_entry = 0
        for e in entries.all():
            total_words_entry += e.word_count
        words_per_entry = float(total_words_entry) / entries_count

        words_per_comment = 0.0
        if replies_count:
            total_words_comment = 0
            for c in replies.all():
                total_words_comment += len(c.comment.split())
            words_per_comment = float(total_words_comment) / replies_count
    else:
        words_per_entry = words_per_comment = entries_per_month = \
            comments_per_entry = linkbacks_per_entry = 0.0

    return {'template': template,
            'entries': entries_count,
            'categories': categories.count(),
            'tags': tags.count(),
            'authors': authors.count(),
            'comments': replies_count,
            'pingbacks': pingbacks_count,
            'trackbacks': trackbacks_count,
            'rejects': rejects.count(),
            'words_per_entry': words_per_entry,
            'words_per_comment': words_per_comment,
            'entries_per_month': entries_per_month,
            'comments_per_entry': comments_per_entry,
            'linkbacks_per_entry': linkbacks_per_entry}

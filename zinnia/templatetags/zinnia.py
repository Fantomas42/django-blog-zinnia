"""Template tags and filters for Zinnia"""
import re
from datetime import date
from hashlib import md5
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.db.models import Q
from django.template import Library
from django.template.defaultfilters import stringfilter
from django.template.loader import select_template
from django.utils import timezone
from django.utils.encoding import smart_str
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from django_comments import get_model as get_comment_model
from django_comments.models import CommentFlag

from tagging.models import Tag
from tagging.utils import calculate_cloud

from ..breadcrumbs import retrieve_breadcrumbs
from ..calendar import Calendar
from ..comparison import EntryPublishedVectorBuilder
from ..context import get_context_first_matching_object
from ..context import get_context_first_object
from ..context import get_context_loop_positions
from ..flags import PINGBACK, TRACKBACK
from ..managers import DRAFT
from ..managers import tags_published
from ..models.author import Author
from ..models.category import Category
from ..models.entry import Entry
from ..settings import ENTRY_LOOP_TEMPLATES
from ..settings import PROTOCOL
from ..templating import loop_template_list


WIDONT_REGEXP = re.compile(
    r'\s+(\S+\s*)$')
DOUBLE_SPACE_PUNCTUATION_WIDONT_REGEXP = re.compile(
    r'\s+([-+*/%=;:!?]+&nbsp;\S+\s*)$')
END_PUNCTUATION_WIDONT_REGEXP = re.compile(
    r'\s+([?!]+\s*)$')

register = Library()


@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def get_categories(context, template='zinnia/tags/categories.html'):
    """
    Return the published categories.
    """
    return {'template': template,
            'categories': Category.published.all().order_by('title').annotate(
                count_entries_published=Count('entries')),
            'context_category': context.get('category')}


@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def get_categories_tree(context, template='zinnia/tags/categories_tree.html'):
    """
    Return the categories as a tree.
    """
    return {'template': template,
            'categories': Category.objects.all().annotate(
                count_entries=Count('entries')),
            'context_category': context.get('category')}


@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def get_authors(context, template='zinnia/tags/authors.html'):
    """
    Return the published authors.
    """
    return {'template': template,
            'authors': Author.published.all().annotate(
                count_entries_published=Count('entries')),
            'context_author': context.get('author')}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_recent_entries(number=5, template='zinnia/tags/entries_recent.html'):
    """
    Return the most recent entries.
    """
    return {'template': template,
            'entries': Entry.published.all()[:number]}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_featured_entries(number=5,
                         template='zinnia/tags/entries_featured.html'):
    """
    Return the featured entries.
    """
    return {'template': template,
            'entries': Entry.published.filter(featured=True)[:number]}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_draft_entries(number=5,
                      template='zinnia/tags/entries_draft.html'):
    """
    Return the last draft entries.
    """
    return {'template': template,
            'entries': Entry.objects.filter(status=DRAFT)[:number]}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_random_entries(number=5, template='zinnia/tags/entries_random.html'):
    """
    Return random entries.
    """
    return {'template': template,
            'entries': Entry.published.order_by('?')[:number]}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_popular_entries(number=5, template='zinnia/tags/entries_popular.html'):
    """
    Return popular entries.
    """
    return {'template': template,
            'entries': Entry.published.filter(
                comment_count__gt=0).order_by(
                '-comment_count', '-publication_date')[:number]}


@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def get_similar_entries(context, number=5,
                        template='zinnia/tags/entries_similar.html'):
    """
    Return similar entries.
    """
    entry = context.get('entry')
    if not entry:
        return {'template': template, 'entries': []}

    vectors = EntryPublishedVectorBuilder()
    entries = vectors.get_related(entry, number)

    return {'template': template,
            'entries': entries}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_archives_entries(template='zinnia/tags/entries_archives.html'):
    """
    Return archives entries.
    """
    return {'template': template,
            'archives': Entry.published.datetimes(
                'publication_date', 'month', order='DESC')}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_archives_entries_tree(
        template='zinnia/tags/entries_archives_tree.html'):
    """
    Return archives entries as a tree.
    """
    return {'template': template,
            'archives': Entry.published.datetimes(
                'publication_date', 'day', order='ASC')}


@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def get_calendar_entries(context, year=None, month=None,
                         template='zinnia/tags/entries_calendar.html'):
    """
    Return an HTML calendar of entries.
    """
    if not (year and month):
        day_week_month = (context.get('day') or
                          context.get('week') or
                          context.get('month'))
        publication_date = getattr(context.get('object'),
                                   'publication_date', None)
        if day_week_month:
            current_month = day_week_month
        elif publication_date:
            if settings.USE_TZ:
                publication_date = timezone.localtime(publication_date)
            current_month = publication_date.date()
        else:
            today = timezone.now()
            if settings.USE_TZ:
                today = timezone.localtime(today)
            current_month = today.date()
        current_month = current_month.replace(day=1)
    else:
        current_month = date(year, month, 1)

    dates = list(map(
        lambda x: settings.USE_TZ and timezone.localtime(x).date() or x.date(),
        Entry.published.datetimes('publication_date', 'month')))

    if current_month not in dates:
        dates.append(current_month)
        dates.sort()
    index = dates.index(current_month)

    previous_month = index > 0 and dates[index - 1] or None
    next_month = index != len(dates) - 1 and dates[index + 1] or None
    calendar = Calendar()

    return {'template': template,
            'next_month': next_month,
            'previous_month': previous_month,
            'calendar': calendar.formatmonth(
                current_month.year,
                current_month.month,
                previous_month=previous_month,
                next_month=next_month)}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_recent_comments(number=5, template='zinnia/tags/comments_recent.html'):
    """
    Return the most recent comments.
    """
    # Using map(smart_str... fix bug related to issue #8554
    entry_published_pks = map(smart_str,
                              Entry.published.values_list('id', flat=True))
    content_type = ContentType.objects.get_for_model(Entry)

    comments = get_comment_model().objects.filter(
        Q(flags=None) | Q(flags__flag=CommentFlag.MODERATOR_APPROVAL),
        content_type=content_type, object_pk__in=entry_published_pks,
        is_public=True).order_by('-pk')[:number]

    comments = comments.prefetch_related('content_object')

    return {'template': template,
            'comments': comments}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_recent_linkbacks(number=5,
                         template='zinnia/tags/linkbacks_recent.html'):
    """
    Return the most recent linkbacks.
    """
    entry_published_pks = map(smart_str,
                              Entry.published.values_list('id', flat=True))
    content_type = ContentType.objects.get_for_model(Entry)

    linkbacks = get_comment_model().objects.filter(
        content_type=content_type,
        object_pk__in=entry_published_pks,
        flags__flag__in=[PINGBACK, TRACKBACK],
        is_public=True).order_by('-pk')[:number]

    linkbacks = linkbacks.prefetch_related('content_object')

    return {'template': template,
            'linkbacks': linkbacks}


@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def zinnia_pagination(context, page, begin_pages=1, end_pages=1,
                      before_pages=2, after_pages=2,
                      template='zinnia/tags/pagination.html'):
    """
    Return a Digg-like pagination,
    by splitting long list of page into 3 blocks of pages.
    """
    get_string = ''
    for key, value in context['request'].GET.items():
        if key != 'page':
            get_string += '&%s=%s' % (key, value)

    page_range = list(page.paginator.page_range)
    begin = page_range[:begin_pages]
    end = page_range[-end_pages:]
    middle = page_range[max(page.number - before_pages - 1, 0):
                        page.number + after_pages]

    if set(begin) & set(middle):  # [1, 2, 3], [2, 3, 4], [...]
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

    if set(begin) & set(end):  # [1, 2, 3], [...], [2, 3, 4]
        begin = sorted(set(begin + end))  # [1, 2, 3, 4]
        middle, end = [], []
    elif begin[-1] + 1 == end[0]:  # [1, 2, 3], [...], [4, 5, 6]
        begin += end  # [1, 2, 3, 4, 5, 6]
        middle, end = [], []

    return {'template': template,
            'page': page,
            'begin': begin,
            'middle': middle,
            'end': end,
            'GET_string': get_string}


@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def zinnia_breadcrumbs(context, root_name='',
                       template='zinnia/tags/breadcrumbs.html',):
    """
    Return a breadcrumb for the application.
    """
    path = context['request'].path
    context_object = get_context_first_object(
        context, ['object', 'category', 'tag', 'author'])
    context_page = context.get('page_obj')
    breadcrumbs = retrieve_breadcrumbs(
        path, context_object, context_page, root_name)

    return {'template': template,
            'breadcrumbs': breadcrumbs}


@register.simple_tag(takes_context=True)
def zinnia_loop_template(context, default_template):
    """
    Return a selected template from his position within a loop
    and the filtering context.
    """
    matching, context_object = get_context_first_matching_object(
        context,
        ['category', 'tag', 'author', 'pattern',
         'year', 'month', 'week', 'day'])
    context_positions = get_context_loop_positions(context)

    templates = loop_template_list(
        context_positions, context_object, matching,
        default_template, ENTRY_LOOP_TEMPLATES)

    return select_template(templates)


@register.simple_tag
def get_gravatar(email, size=80, rating='g', default=None,
                 protocol=PROTOCOL):
    """
    Return url for a Gravatar.
    """
    gravatar_protocols = {'http': 'http://www',
                          'https': 'https://secure'}
    url = '%s.gravatar.com/avatar/%s' % (
        gravatar_protocols[protocol],
        md5(email.strip().lower().encode('utf-8')).hexdigest())
    options = {'s': size, 'r': rating}
    if default:
        options['d'] = default

    url = '%s?%s' % (url, urlencode(options))
    return url.replace('&', '&amp;')


@register.simple_tag
def get_tags():
    """
    Return the published tags.
    """
    return Tag.objects.usage_for_queryset(
        Entry.published.all())


@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def get_tag_cloud(context, steps=6, min_count=None,
                  template='zinnia/tags/tag_cloud.html'):
    """
    Return a cloud of published tags.
    """
    tags = Tag.objects.usage_for_queryset(
        Entry.published.all(), counts=True,
        min_count=min_count)
    return {'template': template,
            'tags': calculate_cloud(tags, steps),
            'context_tag': context.get('tag')}


@register.filter(needs_autoescape=True)
@stringfilter
def widont(value, autoescape=None):
    """
    Add an HTML non-breaking space between the final
    two words of the string to avoid "widowed" words.
    """
    esc = autoescape and conditional_escape or (lambda x: x)

    def replace(matchobj):
        return '&nbsp;%s' % matchobj.group(1)

    value = END_PUNCTUATION_WIDONT_REGEXP.sub(replace, esc(smart_str(value)))
    value = WIDONT_REGEXP.sub(replace, value)
    value = DOUBLE_SPACE_PUNCTUATION_WIDONT_REGEXP.sub(replace, value)

    return mark_safe(value)


@register.filter
def week_number(date):
    r"""
    Return the Python week number of a date.
    The django \|date:"W" returns incompatible value
    with the view implementation.
    """
    week_number = date.strftime('%W')
    if int(week_number) < 10:
        week_number = week_number[-1]
    return week_number


@register.filter
def comment_admin_urlname(action):
    """
    Return the admin URLs for the comment app used.
    """
    comment = get_comment_model()
    return 'admin:%s_%s_%s' % (
        comment._meta.app_label, comment._meta.model_name,
        action)


@register.filter
def user_admin_urlname(action):
    """
    Return the admin URLs for the user app used.
    """
    user = get_user_model()
    return 'admin:%s_%s_%s' % (
        user._meta.app_label, user._meta.model_name,
        action)


@register.inclusion_tag('zinnia/tags/dummy.html')
def zinnia_statistics(template='zinnia/tags/statistics.html'):
    """
    Return statistics on the content of Zinnia.
    """
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
        first_entry = entries.order_by('publication_date')[0]
        last_entry = entries.latest()
        months_count = (last_entry.publication_date -
                        first_entry.publication_date).days / 31.0
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

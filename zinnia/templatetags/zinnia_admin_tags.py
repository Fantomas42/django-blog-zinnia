"""Template tags and filters for Zinnia's admin"""
from django.template import Library
from django.contrib import comments
from django.contrib.contenttypes.models import ContentType

from zinnia.models import Entry
from zinnia.models import Author
from zinnia.models import Category
from zinnia.managers import tags_published

register = Library()


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_content_stats(
    template='admin/zinnia/widgets/_content_stats.html'):
    """Return statistics of the contents"""

    content_type = ContentType.objects.get_for_model(Entry)
    discussions = comments.get_model().objects.filter(
        content_type=content_type)

    entries = Entry.published
    categories = Category.objects
    tags = tags_published()
    authors = Author.published
    replies = discussions.filter(
        flags=None, is_public=True)
    pingbacks = discussions.filter(
        flags__flag='pingback', is_public=True)
    trackbacks = discussions.filter(
        flags__flag='trackback', is_public=True)
    rejects = discussions.filter(is_public=False)

    entries_count = entries.count()
    replies_count = replies.count()
    pingbacks_count = pingbacks.count()
    trackbacks_count = trackbacks.count()

    first_entry = entries.order_by('creation_date')[0]
    last_entry = entries.latest()
    months_count = (last_entry.creation_date - \
                    first_entry.creation_date).days / 31.0
    entries_per_month = months_count / entries_count

    comments_per_entry = replies_count / float(entries_count) or 1.0
    linkbacks_per_entry = (pingbacks_count + \
                           trackbacks_count) / float(entries_count) or 1.0

    total_words_entry = 0
    for e in entries.all():
        total_words_entry += e.word_count
    words_per_entry = total_words_entry / float(entries_count) or 1.0

    total_words_comment = 0
    for c in replies.all():
        total_words_comment += len(c.comment.split())
    words_per_comment = total_words_comment / float(replies_count) or 1.0

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
            'linkbacks_per_entry': linkbacks_per_entry
            }

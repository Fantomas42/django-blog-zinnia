"""Template tags and filters for Zinnia's admin"""
from django.template import Library
from django.contrib import comments
from django.contrib.contenttypes.models import ContentType

from zinnia.models import Entry
from zinnia.models import Author
from zinnia.models import Category
from zinnia.managers import DRAFT
from zinnia.managers import tags_published

register = Library()


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_draft_entries(
    number=5, template='admin/zinnia/widgets/_draft_entries.html'):
    """Return the latest draft entries"""
    return {'template': template,
            'entries': Entry.objects.filter(status=DRAFT)[:number]}


@register.inclusion_tag('zinnia/tags/dummy.html')
def get_content_stats(
    template='admin/zinnia/widgets/_content_stats.html'):
    """Return statistics of the contents"""
    content_type = ContentType.objects.get_for_model(Entry)

    discussions = comments.get_model().objects.filter(
        is_public=True, content_type=content_type)

    return {'template': template,
            'entries': Entry.published.count(),
            'categories': Category.objects.count(),
            'tags': tags_published().count(),
            'authors': Author.published.count(),
            'comments': discussions.filter(flags=None).count(),
            'pingbacks': discussions.filter(flags__flag='pingback').count(),
            'trackbacks': discussions.filter(flags__flag='trackback').count(),
            'rejects': comments.get_model().objects.filter(
                is_public=False, content_type=content_type).count(),
            }

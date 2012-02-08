"""Views for Zinnia sitemap"""
from django.views.generic.simple import direct_to_template

from zinnia.models import Entry
from zinnia.models import Category


def sitemap(request, **kwargs):
    """Wrapper around the direct to template generic view to
    force the update of the extra context"""
    if not kwargs.get('template'):
        kwargs['template'] = 'zinnia/sitemap.html'

    extra_context = kwargs.pop('extra_context', {})
    extra_context.update({'entries': Entry.published.all(),
                          'categories': Category.objects.all()})
    kwargs['extra_context'] = extra_context

    return direct_to_template(request, **kwargs)

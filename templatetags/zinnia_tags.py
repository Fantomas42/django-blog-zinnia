"""Template tags for Zinnia"""
try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5
    
from random import sample
from urllib import urlencode

from django.template import Library

from zinnia.models import Entry

register = Library()

@register.inclusion_tag('zinnia/tags/recent_entries.html')
def get_recent_entries(number):
    """Return the most recent entries"""
    return {'entries': Entry.published.all()[:number]}


@register.inclusion_tag('zinnia/tags/random_entries.html')
def get_random_entries(number=5):
    """Return random entries"""
    entries = Entry.published.all()
    if number > len(entries):
        number = len(entries)
    return {'entries': sample(entries, number)}

@register.inclusion_tag('zinnia/tags/popular_entries.html')
def get_popular_entries(number=5):
    """Return popular  entries"""
    entries_comment = [(e, e.get_n_comments()) for e in Entry.published.all()]
    
    entries_comment = sorted(entries_comment, key=lambda x:(x[1], x[0]),
                             reverse=True)[:number]
    entries = [entry for entry, n_comments in entries_comment]
    return {'entries': entries}


@register.inclusion_tag('zinnia/tags/archives_entries.html')
def get_archives_entries():
    """Return archives entries"""
    return {'archives': Entry.published.dates('creation_date', 'month', order='DESC')}

@register.simple_tag
def get_gravatar(email, size, rating, default=None):
    """Return url for a Gravatar"""
    url = 'http://www.gravatar.com/avatar/%s.jpg' % md5(email).hexdigest()
    options  = {'s': size, 'r': rating}
    if default:
        options['d'] = default

    return '%s?%s' % (url, urlencode(options))


"""
Set of" markup" function to transform plain text into HTML for Zinnia.
Code originally provided by django.contrib.markups
"""
import warnings

from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.html import linebreaks

from zinnia.settings import MARKDOWN_EXTENSIONS
from zinnia.settings import MARKUP_LANGUAGE
from zinnia.settings import RESTRUCTUREDTEXT_SETTINGS


def textile(value):
    """
    Textile processing.
    """
    try:
        import textile
    except ImportError:
        warnings.warn("The Python textile library isn't installed.",
                      RuntimeWarning)
        return value

    return textile.textile(force_text(value),
                           encoding='utf-8', output='utf-8')


def markdown(value, extensions=MARKDOWN_EXTENSIONS):
    """
    Markdown processing with optionally using various extensions
    that python-markdown supports.
    `extensions` is an iterable of either markdown.Extension instances
    or extension paths.
    """
    try:
        import markdown
    except ImportError:
        warnings.warn("The Python markdown library isn't installed.",
                      RuntimeWarning)
        return value

    return markdown.markdown(force_text(value), extensions=extensions)


def restructuredtext(value, settings=RESTRUCTUREDTEXT_SETTINGS):
    """
    RestructuredText processing with optionnally custom settings.
    """
    try:
        from docutils.core import publish_parts
    except ImportError:
        warnings.warn("The Python docutils library isn't installed.",
                      RuntimeWarning)
        return value

    parts = publish_parts(source=force_bytes(value),
                          writer_name='html4css1',
                          settings_overrides=settings)
    return force_text(parts['fragment'])


def html_format(value):
    """
    Returns the value formatted in HTML,
    depends on MARKUP_LANGUAGE setting.
    """
    if not value:
        return ''
    elif MARKUP_LANGUAGE == 'markdown':
        return markdown(value)
    elif MARKUP_LANGUAGE == 'textile':
        return textile(value)
    elif MARKUP_LANGUAGE == 'restructuredtext':
        return restructuredtext(value)
    elif '</p>' not in value:
        return linebreaks(value)
    return value

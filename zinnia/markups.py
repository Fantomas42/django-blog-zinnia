"""
Set of" markup" function to transform plain text into HTML for Zinnia.
Code originally provided by django.contrib.markups
"""
import warnings

from django.utils import six
from django.utils.encoding import force_text
from django.utils.encoding import force_bytes

from zinnia.settings import MARKDOWN_EXTENSIONS
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
    `extensions` may be a string of comma-separated extension paths
    or an iterable of either markdown.Extension instances or
    extension paths.
    Samples:
        'markdown.extensions.nl2br,markdown.extension.toc'
        ['markdown.extensions.nl2br', MyExtension(mysetting="foo")]
    """
    try:
        import markdown
    except ImportError:
        warnings.warn("The Python markdown library isn't installed.",
                      RuntimeWarning)
        return value

    if isinstance(extensions, six.string_types):
        extensions = [e for e in extensions.split(',') if e]

    return markdown.markdown(force_text(value),
                             extensions=extensions, safe_mode=False)


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

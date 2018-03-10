"""
Extensions for the Sphinx documation of Zinnia

Inspired, stealed and needed for
cross linking the django documentation.
"""
import inspect

from django.db import models
from django.utils.encoding import force_text
from django.utils.html import strip_tags


def skip_model_member(app, what, name, obj, skip, options):
    # These fields always fails !
    if name in ('tags', 'image'):
        return True
    return skip


def process_model_docstring(app, what, name, obj, options, lines):
    if inspect.isclass(obj) and issubclass(obj, models.Model):
        for field in obj._meta.fields:
            # Decode and strip any html out of the field's help text
            help_text = strip_tags(force_text(field.help_text))
            # Decode and capitalize the verbose name, for use if there isn't
            # any help text
            verbose_name = force_text(field.verbose_name).capitalize()

            if help_text:
                lines.append(':param %s: %s' % (field.attname, help_text))
            else:
                lines.append(':param %s: %s' % (field.attname, verbose_name))
            # Add the field's type to the docstring
            lines.append(':type %s: %s' % (field.attname,
                                           type(field).__name__))
    # Return the extended docstring
    return lines


def setup(app):
    app.add_crossref_type(
        directivename='setting',
        rolename='setting',
        indextemplate='pair: %s; setting',
    )
    app.add_crossref_type(
        directivename='templatetag',
        rolename='ttag',
        indextemplate='pair: %s; template tag'
    )
    app.add_crossref_type(
        directivename='templatefilter',
        rolename='tfilter',
        indextemplate='pair: %s; template filter'
    )
    app.connect('autodoc-process-docstring',
                process_model_docstring)
    app.connect('autodoc-skip-member',
                skip_model_member)

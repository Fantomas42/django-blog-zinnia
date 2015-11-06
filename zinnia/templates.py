"""Templates module for Zinnia"""
from django.template.defaultfilters import slugify

from zinnia.settings import ENTRY_LOOP_TEMPLATES


def loop_template_list(position, context_object, template_name=None):
    """
    Build a list of templates from loop positions and context lookups.
    """
    templates = []

    if position:
        if template_name:
            templates.append('%s_%s' % (template_name, position))
        templates.append('zinnia/%s_entry_detail.html' % position)

        class_context_key = context_object.__class__.__name__.lower()
        string_context_key = slugify(str(context_object))
        for key in ['default',
                    '%s-%s' % (class_context_key, string_context_key),
                    string_context_key,
                    class_context_key]:
            try:
                templates.insert(0, ENTRY_LOOP_TEMPLATES[key][position])
            except KeyError:
                pass

    templates.append(template_name)

    return templates

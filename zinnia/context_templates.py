"""Context Position module for Zinnia"""
from django.template.defaultfilters import slugify

from zinnia.settings import ENTRY_LOOP_TEMPLATES


def loop_position(context):
    try:
        loop_counter = context['forloop']['counter']
    except KeyError:
        return 0
    try:
        page = context['page_obj']
    except KeyError:
        return loop_counter
    return (page.number - 1) * page.paginator.per_page + loop_counter


def filter_template(context, position):
    context_object = context.get('category') or \
        context.get('tag') or context.get('author') or \
        context.get('year') or context.get('month') or \
        context.get('day') or context.get('week') or \
        context.get('pattern')

    class_context_key = context_object.__class__.__name__.lower()
    model_context_key = slugify(str(context_object))

    for key in ['%s-%s' % (class_context_key, model_context_key),
                model_context_key, class_context_key, 'default']:
        if key in ENTRY_LOOP_TEMPLATES:
            loop_key = key
            break
    try:
        return ENTRY_LOOP_TEMPLATES[loop_key][position]
    except KeyError:
        return None


def get_positional_templates(context, default_template):
    templates = []
    position = loop_position(context)
    if position:
        templates.extend(['%s_%s' % (default_template, position),
                          'zinnia/%s_entry_detail.html' % position])
        template = filter_template(context, position)
        if template:
            templates.insert(0, template)

    return templates

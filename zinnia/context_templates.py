"""Context Position module for Zinnia"""
from django.template.defaultfilters import slugify

from zinnia.settings import ENTRY_LOOP_TEMPLATES


def get_loop_position(context):
    """
    Return the paginated current position within a loop with context.
    """
    try:
        loop_counter = context['forloop']['counter']
    except KeyError:
        return 0
    try:
        page = context['page_obj']
    except KeyError:
        return loop_counter
    return (page.number - 1) * page.paginator.per_page + loop_counter


def get_context_object(context, context_lookups):
    """
    Return the first object found in the context,
    from a list of keys.
    """
    for key in context_lookups:
        context_object = context.get(key)
        if context_object:
            return context_object


def get_context_template(context, context_lookups, position):
    """
    Look into the context to find a matching key,
    and returns the associated template matching key and position
    in ENTRY_LOOP_TEMPLATES.
    """
    context_object = get_context_object(context, context_lookups)

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


def get_positional_templates(context, template_name=None, context_lookups=[]):
    """
    Build a list of templates from loop positions and context lookups.
    """
    templates = []
    position = get_loop_position(context)

    if position:
        if template_name:
            templates.append('%s_%s' % (template_name, position))
        templates.append('zinnia/%s_entry_detail.html' % position)

        context_template = get_context_template(
            context, context_lookups, position)
        if context_template:
            templates.insert(0, context_template)

    return templates

"""Context module for Zinnia"""


def get_context_first_object(context, context_lookups):
    """
    Return the first object found in the context,
    from a list of keys.
    """
    for key in context_lookups:
        context_object = context.get(key)
        if context_object:
            return context_object


def get_context_loop_position(context):
    """
    Return the paginated current position within a loop.
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

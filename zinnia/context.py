"""Context module for Zinnia"""


def get_context_first_matching_object(context, context_lookups):
    """
    Return the first object found in the context,
    from a list of keys, with the matching key.
    """
    for key in context_lookups:
        context_object = context.get(key)
        if context_object:
            return key, context_object
    return None, None


def get_context_first_object(context, context_lookups):
    """
    Return the first object found in the context,
    from a list of keys.
    """
    return get_context_first_matching_object(
        context, context_lookups)[1]


def get_context_loop_positions(context):
    """
    Return the paginated current position within a loop,
    and the non-paginated position.
    """
    try:
        loop_counter = context['forloop']['counter']
    except KeyError:
        return 0, 0
    try:
        page = context['page_obj']
    except KeyError:
        return loop_counter, loop_counter
    total_loop_counter = ((page.number - 1) * page.paginator.per_page +
                          loop_counter)
    return total_loop_counter, loop_counter

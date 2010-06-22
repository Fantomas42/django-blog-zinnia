"""Decorators for zinnia.views"""

def update_queryset(view, queryset,
                    queryset_parameter='queryset'):
    """Decorator around views based on a queryset
    passed in parameter, who will force the update
    of the queryset before executing the view.
    Related to issue http://code.djangoproject.com/ticket/8378"""

    def wrap(*args, **kwargs):
        """Regenerate the queryset before passing it to the view."""
        kwargs[queryset_parameter] = queryset()
        return view(*args, **kwargs)

    return wrap

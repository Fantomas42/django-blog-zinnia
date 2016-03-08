"""Cache mixins for Zinnia views"""


class EntryCacheMixin(object):
    """
    Mixin implementing cache on ``get_object`` method.
    """
    _cached_object = None

    def get_object(self, queryset=None):
        """
        Implement cache on ``get_object`` method to
        avoid repetitive calls, in POST.
        """
        if self._cached_object is None:
            self._cached_object = super(EntryCacheMixin, self).get_object(
                queryset)
        return self._cached_object

"""Callable Queryset mixins for Zinnia views"""
from django.core.exceptions import ImproperlyConfigured


class CallableQuerysetMixin(object):
    """Mixin for handling a callable queryset.
    Who will force the update of the queryset.
    Related to issue http://code.djangoproject.com/ticket/8378"""
    queryset = None

    def get_queryset(self):
        """Check that the queryset is defined and call it"""
        if self.queryset is None:
            raise ImproperlyConfigured(
                u"'%s' must define 'queryset'" % self.__class__.__name__)
        return self.queryset()

"""MimeType mixins for Zinnia views"""
from django.views.generic.base import TemplateView
from django.core.exceptions import ImproperlyConfigured


class MimeTypeMixin(object):
    """Mixin for handling the mimetype parameter"""
    mimetype = None

    def get_mimetype(self):
        """Return the mimetype of the response"""
        if self.mimetype is None:
            raise ImproperlyConfigured(
                u"%s requires either a definition of "
                "'mimetype' or an implementation of 'get_mimetype()'" %
                self.__class__.__name__)
        return self.mimetype


class TemplateMimeTypeView(MimeTypeMixin, TemplateView):
    """TemplateView with a configurable mimetype"""

    def render_to_response(self, context, **kwargs):
        """Render the view with a custom mimetype"""
        return super(TemplateMimeTypeView, self).render_to_response(
            context, mimetype=self.get_mimetype(), **kwargs)

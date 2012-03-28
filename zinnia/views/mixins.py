"""Mixins for Zinnia views"""
from django.views.generic import TemplateView
from django.core.exceptions import ImproperlyConfigured


class MimeTypeMixin(object):
    """Mixin for handling the mimetype parameter"""
    mimetype = None

    def get_mimetype(self):
        if self.mimetype is None:
            raise ImproperlyConfigured(
                "%s requires either a definition of "
                "'mimetype' or an implementation of 'get_mimetype()'" % \
                self.__class__.__name__)
        else:
            return self.mimetype


class TemplateMimeTypeView(MimeTypeMixin, TemplateView):
    """TemplateView with a configurable mimetype"""

    def render_to_response(self, context, **kwargs):
        return super(TemplateMimeTypeView, self).render_to_response(
            context, mimetype=self.get_mimetype(), **kwargs)

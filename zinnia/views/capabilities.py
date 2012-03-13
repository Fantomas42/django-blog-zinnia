from django.core.exceptions import ImproperlyConfigured
from django.contrib.sites.models import Site
from django.views.generic import TemplateView

from zinnia.settings import PROTOCOL, COPYRIGHT, FEEDS_FORMAT


class SimpleMixin(object):
    mimetype = None
    extra_context = {}

    def get_mimetype(self):
        if self.mimetype is None:
            raise ImproperlyConfigured(
                "%s requires either a definition of "
                "'mimetype' or an implementation of 'get_mimetype()'" % self.__class__.__name__)
        else:
            return self.mimetype

    def get_extra_context(self):
        return self.extra_context
    
    def get_context_data(self,**kwargs):
        context = super(SimpleMixin,self).get_context_data(**kwargs)
        context.update(self.get_extra_context())
        return context

class SimpleView(SimpleMixin, TemplateView):
    def render_to_response(self,context,**response_kwargs):
        response_kwargs = response_kwargs or {}
        response_kwargs['mimetype'] = self.get_mimetype()
        return super(SimpleView,self).render_to_response(context,**response_kwargs)
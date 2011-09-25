"""Views for the Zinnia Demo"""
from django.conf import settings
from django.template import loader
from django.template import Context
from django.http import HttpResponseServerError


def server_error(request, template_name='500.html'):
    """
    500 error handler.
    Templates: `500.html`
    Context:
    STATIC_URL
      Path of static media (e.g. "media.example.org")
    """
    t = loader.get_template(template_name)
    return HttpResponseServerError(
        t.render(Context({'STATIC_URL': settings.STATIC_URL})))

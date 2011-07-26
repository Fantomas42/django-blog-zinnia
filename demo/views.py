"""Views for the Zinnia Demo"""
from django.template import loader
from django.template import Context
from django.http import HttpResponseServerError

from zinnia.settings import MEDIA_URL


def server_error(request, template_name='500.html'):
    """
    500 error handler.
    Templates: `500.html`
    Context:
    MEDIA_URL
      Path of static media (e.g. "media.example.org")
    """
    t = loader.get_template(template_name)
    return HttpResponseServerError(
        t.render(Context({'ZINNIA_MEDIA_URL': MEDIA_URL})))

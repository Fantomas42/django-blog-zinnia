"""Default URL shortener backend for Zinnia"""
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from zinnia.settings import PROTOCOL


def backend(entry):
    """
    Default URL shortener backend for Zinnia.
    """
    return '%s://%s%s' % (PROTOCOL, Site.objects.get_current().domain,
                          reverse('zinnia:entry_shortlink', args=[entry.pk]))

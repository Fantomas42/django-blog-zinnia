"""Default URL shortener backend for Zinnia"""
import math
import string

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from zinnia.settings import PROTOCOL

base36 = lambda x: ''.join(
    [(string.digits + string.ascii_uppercase)[(x // 36 ** i) % 36]
     for i in range(int(math.log(x, 36)), -1, -1)]
    )


def backend(entry):
    """
    Default URL shortener backend for Zinnia.
    """
    return '%s://%s%s' % (
        PROTOCOL, Site.objects.get_current().domain,
        reverse('zinnia:entry_shortlink', args=[base36(entry.pk)]))

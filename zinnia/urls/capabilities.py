"""Urls for the zinnia capabilities"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns
from django.contrib.sites.models import Site

from zinnia.views.capabilities import SimpleView
from zinnia.settings import PROTOCOL
from zinnia.settings import COPYRIGHT
from zinnia.settings import FEEDS_FORMAT

extra_context = {'protocol': PROTOCOL,
                 'site': Site.objects.get_current()}

extra_context_opensearch = extra_context.copy()
extra_context_opensearch.update({'copyright': COPYRIGHT,
                                 'feeds_format': FEEDS_FORMAT})

urlpatterns = patterns('',
    url(r'^humans.txt$', SimpleView.as_view(
          template_name='zinnia/humans.txt',
          mimetype='text/plain'
        ),
        name='zinnia_humans'
    ),
    url(r'^rsd.xml$', SimpleView.as_view(
          template_name='zinnia/rsd.xml',
          mimetype='application/rsd+xml',
          extra_context=extra_context
        ),
        name='zinnia_rsd'
    ),
   url(r'^wlwmanifest.xml$', SimpleView.as_view(
          template_name='zinnia/wlwmanifest.xml',
          mimetype='application/wlwmanifest+xml',
          extra_context=extra_context,
        ),
       name='zinnia_wlwmanifest'),
   url(r'^opensearch.xml$', SimpleView.as_view(
          template_name='zinnia/opensearch.xml',
          mimetype='application/opensearchdescription+xml',
          extra_context=extra_context_opensearch,
        ),
       name='zinnia_opensearch'),
)
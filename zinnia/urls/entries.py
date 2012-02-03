"""Urls for the Zinnia entries"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from zinnia.models import Entry
from zinnia.settings import ALLOW_FUTURE

entry_conf = {'date_field': 'creation_date',
              'allow_future': ALLOW_FUTURE,
              'queryset': Entry.published.on_site(),
              'month_format': '%m'}

urlpatterns = patterns(
    'zinnia.views.entries',
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        'entry_detail', entry_conf,
        name='zinnia_entry_detail'),
    )

"""Poor test urls for the zinnia project"""
from django.conf.urls import include
from django.urls import include, re_path
from django.contrib import admin

from zinnia.views.entries import EntryDetail

admin.autodiscover()

blog_urls = ([
    re_path(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        EntryDetail.as_view(),
        name='entry_detail')],
    'zinnia'
)

urlpatterns = [
    re_path(r'^', include(blog_urls)),
    re_path(r'^admin/', admin.site.urls),
]

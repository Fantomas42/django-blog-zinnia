"""Poor test urls for the zinnia project"""
from django.contrib import admin
from django.conf.urls import url
from django.conf.urls import include
from django.conf.urls import patterns

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^', include('zinnia.urls.entries')),
    url(r'^admin/', include(admin.site.urls)),
)

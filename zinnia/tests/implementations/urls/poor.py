"""Poor test urls for the zinnia project"""
from django.contrib import admin
from django.conf.urls import url
from django.conf.urls import include

admin.autodiscover()

urlpatterns = [
    url(r'^', include('zinnia.urls.entries', namespace='zinnia')),
    url(r'^admin/', include(admin.site.urls)),
]

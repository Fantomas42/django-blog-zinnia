"""Urls for the zinnia categories"""
from django.conf.urls.defaults import *

from zinnia.models import Category

category_conf = {
    'queryset': Category.objects.all(),
}

urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.list_detail.object_list',
        category_conf, 'category_list'),
    url(r'^(?P<slug>[-\w]+)/$', 'zinnia.views.category_detail',
        name='category_detail'),
)

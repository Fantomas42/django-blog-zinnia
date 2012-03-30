"""Url for the Zinnia quick entry view"""
from django.conf.urls import url
from django.conf.urls import patterns

urlpatterns = patterns('zinnia.views.quick_entry',
                       url(r'^quick_entry/$', 'view_quick_entry',
                           name='zinnia_entry_quick_post')
                       )

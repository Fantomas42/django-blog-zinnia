"""Urls for the Zinnia comments"""
from django.conf.urls import url
from django.conf.urls import patterns

from zinnia.views.comments import CommentSuccess


urlpatterns = patterns(
    '',
    url(r'^success/$',
        CommentSuccess.as_view(),
        name='zinnia_comment_success')
)

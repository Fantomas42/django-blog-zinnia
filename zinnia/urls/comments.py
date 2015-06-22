"""Urls for the Zinnia comments"""
from django.conf.urls import url

from zinnia.urls import _
from zinnia.views.comments import CommentSuccess


urlpatterns = [
    url(_(r'^success/$'),
        CommentSuccess.as_view(),
        name='comment_success'),
]

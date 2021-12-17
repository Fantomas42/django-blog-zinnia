"""Urls for the Zinnia comments"""
from django.urls import re_path

from zinnia.urls import _
from zinnia.views.comments import CommentSuccess

urlpatterns = [
    re_path(_(r'^success/$'),
            CommentSuccess.as_view(),
            name='comment_success'),
]

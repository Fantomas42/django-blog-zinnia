"""Migrations for Zinnia"""
from django.contrib.auth import get_user_model

User = get_user_model()
user_name = User.__name__
user_table = User._meta.db_table
user_orm_label = '%s.%s' % (User._meta.app_label, User._meta.object_name)
user_model_label = '%s.%s' % (User._meta.app_label, User._meta.model_name)

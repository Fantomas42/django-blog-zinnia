from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    """
    A custom user profile
    """
    username = models.CharField(
        'username', max_length=30, unique=True, db_index=True)

    email = models.EmailField(
        'email address', max_length=254, unique=True)

    is_staff = models.BooleanField(
        'staff status', default=False,
        help_text='Designates whether the user can log into this admin site.')

    is_active = models.BooleanField(
        'active', default=True,
        help_text='Designates whether this user should be treated as '
        'active. Unselect this instead of deleting accounts.')

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def __unicode__(self):
        return self.email
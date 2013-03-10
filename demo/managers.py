from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, username, email=None, password=None, **extra_fields):

        if not email:
            raise ValueError('The given email must be set')

        email = UserManager.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            is_staff=False,
            is_active=True,
            is_superuser=False,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        u = self.create_user(email, email, password, **extra_fields)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u
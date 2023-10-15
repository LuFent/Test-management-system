from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


class AppUserManager(BaseUserManager):
    def create_user(self, email, password, full_name, **extra_fields):
        if not email:
            raise ValueError("An email is required!")
        if not password:
            raise ValueError("An password is required!")

        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name)
        user.set_password(password)
        user.is_superuser = False
        user.save()
        return user

    def create_superuser(self, email, password, full_name, **extra_fields):
        if not email:
            raise ValueError("An email is required!")
        if not password:
            raise ValueError("An password is required!")

        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name)
        user.set_password(password)
        user.is_superuser = True
        user.save()
        return user


class AppUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=50, unique=True)
    full_name = models.CharField(max_length=100)
    tokens_created = models.PositiveIntegerField(default=0)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "full_name",
    ]

    objects = AppUserManager()

    @property
    def is_staff(self):
        return self.is_superuser

    def __str__(self):
        return self.email


class RegistrationToken(models.Model):
    token = models.CharField(max_length=256, unique=True)

    expired_at = models.DateTimeField()

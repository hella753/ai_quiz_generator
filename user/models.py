import uuid
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, AnonymousUser
from django.utils.translation import gettext_lazy as _
from django.db import models
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(
        max_length=20,
        unique=True,
        help_text="Required. 20 character or fewer.",
        error_messages={
            "unique": "A user with that username already exists."
        },
        verbose_name=_("username")
    )
    email = models.EmailField(
        max_length=50,
        unique=True,
        verbose_name=_("email")
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("date_joined")
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name=_("first_name")
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name=_("lastname")
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into this admin site.",
        verbose_name=_("is_staff")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is_active")
    )

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.username}"


class VerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=2)
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() <= self.expires_at


class PasswordResetToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=60)
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() <= self.expires_at

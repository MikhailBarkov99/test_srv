"""User models for the messenger application."""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Custom user model extending Django's AbstractUser."""

    email = models.EmailField('email address', unique=True)
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])],
    )
    status_message = models.CharField(max_length=255, blank=True)
    last_seen = models.DateTimeField(default=timezone.now, db_index=True)

    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']

    def __str__(self) -> str:
        """Return a readable representation of the user."""
        return self.username

    @property
    def is_online(self) -> bool:
        """Return True when the user was active in the last five minutes."""
        return timezone.now() - self.last_seen <= timedelta(minutes=5)

    def update_last_seen(self) -> None:
        """Update the last seen timestamp to the current time."""
        self.last_seen = timezone.now()
        self.save(update_fields=['last_seen'])

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Ensure the username is unique and last seen defaults to now."""
        if not self.last_seen:
            self.last_seen = timezone.now()
        super().save(*args, **kwargs)

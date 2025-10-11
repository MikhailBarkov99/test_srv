"""Custom user model for the messenger application."""
from __future__ import annotations

from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


def user_avatar_path(instance: 'User', filename: str) -> str:
    """Return upload path for user avatars."""
    return f'avatars/{instance.username}/{filename}'


class User(AbstractUser):
    """Extends Django's ``AbstractUser`` with profile fields."""

    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to=user_avatar_path, null=True, blank=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)

    def mark_online(self) -> None:
        """Mark the user as online with the current timestamp."""
        self.is_online = True
        self.last_seen = timezone.now()
        self.save(update_fields=['is_online', 'last_seen'])

    def mark_offline(self) -> None:
        """Mark the user as offline and store last seen timestamp."""
        self.is_online = False
        self.last_seen = timezone.now()
        self.save(update_fields=['is_online', 'last_seen'])

    @property
    def display_name(self) -> str:
        """Return a human friendly name for UI usage."""
        full = self.get_full_name().strip()
        return full or self.username

    def last_seen_display(self) -> datetime | None:
        """Expose last seen time for serialization."""
        return self.last_seen

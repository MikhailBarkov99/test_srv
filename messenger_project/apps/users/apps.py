"""App configuration for custom user application."""
from __future__ import annotations

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Configuration class for the users app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'

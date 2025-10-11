"""App configuration for chat application."""
from __future__ import annotations

from django.apps import AppConfig


class ChatConfig(AppConfig):
    """Configuration class for chat app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.chat'

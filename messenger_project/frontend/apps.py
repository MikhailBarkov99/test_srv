"""App configuration for the frontend app."""
from __future__ import annotations

from django.apps import AppConfig


class FrontendConfig(AppConfig):
    """Configuration class for the frontend application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'frontend'

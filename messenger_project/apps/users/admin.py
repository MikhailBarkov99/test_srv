"""Admin configuration for user models."""
from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Custom admin for the User model."""

    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            'Messenger Profile',
            {'fields': ('avatar', 'status_message', 'last_seen')},
        ),
    )
    list_display = DjangoUserAdmin.list_display + ('status_message', 'last_seen', 'is_online')
    list_filter = DjangoUserAdmin.list_filter + ('last_seen',)
    readonly_fields = ('last_seen',)

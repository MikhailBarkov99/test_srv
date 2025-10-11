"""Admin registrations for chat related models."""
from __future__ import annotations

from django.contrib import admin

from .models import Chat, ChatMember, Message, MessageRead


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    """Admin view for chats."""

    list_display = ('name', 'is_group', 'created_by', 'created_at', 'updated_at')
    list_filter = ('is_group', 'created_at')
    search_fields = ('name', 'created_by__username')
    filter_horizontal = ('members',)


@admin.register(ChatMember)
class ChatMemberAdmin(admin.ModelAdmin):
    """Admin configuration for chat members."""

    list_display = ('chat', 'user', 'joined_at', 'is_admin')
    list_filter = ('is_admin',)
    search_fields = ('chat__name', 'user__username')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin view for messages."""

    list_display = ('chat', 'sender', 'created_at', 'is_deleted')
    list_filter = ('chat', 'sender', 'created_at')
    search_fields = ('content',)


@admin.register(MessageRead)
class MessageReadAdmin(admin.ModelAdmin):
    """Admin view for message read receipts."""

    list_display = ('message', 'user', 'read_at')
    list_filter = ('read_at',)
    search_fields = ('message__content', 'user__username')

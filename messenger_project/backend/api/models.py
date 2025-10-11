"""Models powering chats and messages."""
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Chat(models.Model):
    """Chat room model supporting private and group conversations."""

    CHAT_TYPE_CHOICES = (
        ('private', 'Private'),
        ('group', 'Group'),
    )

    name = models.CharField(max_length=255, blank=True)
    chat_type = models.CharField(max_length=20, choices=CHAT_TYPE_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_chats')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover - human readable representation
        return self.name or f"Chat {self.pk}"

    @property
    def is_group(self) -> bool:
        """Helper property to determine whether the chat is a group chat."""
        return self.chat_type == 'group'


class ChatMembership(models.Model):
    """Links users to chats with additional metadata."""

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_memberships')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)

    class Meta:
        unique_together = ('chat', 'user')

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user} in {self.chat}"


class Message(models.Model):
    """Stores individual chat messages with read receipts."""

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_sent')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read_by = models.ManyToManyField(User, related_name='messages_read', blank=True)

    class Meta:
        ordering = ['-created_at']

    def mark_read(self, user):
        """Mark the message as read by the provided user."""
        self.read_by.add(user)

    @property
    def is_edited(self) -> bool:
        """Return whether the message was edited after creation."""
        return self.updated_at - self.created_at > timezone.timedelta(seconds=1)

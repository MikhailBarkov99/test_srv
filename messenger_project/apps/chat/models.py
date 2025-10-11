"""Chat related models for the messenger application."""
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Chat(models.Model):
    """Model representing a chat conversation."""

    name = models.CharField(max_length=255)
    is_group = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='created_chats', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    members = models.ManyToManyField(User, through='ChatMember', related_name='chats')

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Chat'
        verbose_name_plural = 'Chats'
        indexes = [
            models.Index(fields=['updated_at']),
            models.Index(fields=['is_group']),
        ]

    def __str__(self) -> str:
        """Return chat name."""
        return self.name

    def add_member(self, user) -> None:
        """Add a user to the chat if they are not already a member."""
        ChatMember.objects.get_or_create(chat=self, user=user)

    @property
    def last_message(self):
        """Return the most recent message in the chat."""
        return self.messages.order_by('-created_at').first()


class ChatMember(models.Model):
    """Through model for chat membership."""

    chat = models.ForeignKey(Chat, related_name='chat_members', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='chat_memberships', on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)

    class Meta:
        unique_together = ('chat', 'user')
        verbose_name = 'Chat member'
        verbose_name_plural = 'Chat members'
        indexes = [
            models.Index(fields=['chat', 'user']),
        ]

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.user} in {self.chat}"


class Message(models.Model):
    """Model representing a message within a chat."""

    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        indexes = [
            models.Index(fields=['chat', 'created_at']),
        ]

    def __str__(self) -> str:
        """Return message snippet."""
        return f"Message by {self.sender} in {self.chat}"

    def mark_read_for(self, user) -> None:
        """Mark this message as read for the provided user."""
        MessageRead.objects.update_or_create(message=self, user=user)


class MessageRead(models.Model):
    """Track message read status per user."""

    message = models.ForeignKey(Message, related_name='read_receipts', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='read_messages', on_delete=models.CASCADE)
    read_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('message', 'user')
        verbose_name = 'Message read receipt'
        verbose_name_plural = 'Message read receipts'
        indexes = [
            models.Index(fields=['user', 'read_at']),
        ]

    def __str__(self) -> str:
        """String representation showing who read the message."""
        return f"{self.user} read {self.message}"

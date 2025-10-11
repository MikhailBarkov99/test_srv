"""Custom permissions for chat access control."""
from __future__ import annotations

from rest_framework.permissions import BasePermission


class IsChatParticipant(BasePermission):
    """Allow access only to users who are part of the chat."""

    message = 'You must be a member of this chat to access it.'

    def has_object_permission(self, request, view, obj) -> bool:  # type: ignore[override]
        chat = getattr(obj, 'chat', obj)
        return chat.memberships.filter(user=request.user).exists()

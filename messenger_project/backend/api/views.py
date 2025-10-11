"""REST API views for the messenger application."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from backend.users.serializers import UserProfileSerializer

from .models import Chat, ChatMembership, Message
from .permissions import IsChatParticipant
from .serializers import ChatSerializer, MessageSerializer

User = get_user_model()


class ChatViewSet(viewsets.ModelViewSet):
    """CRUD operations for chats."""

    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated, IsChatParticipant]

    def get_queryset(self):
        return Chat.objects.filter(memberships__user=self.request.user).distinct()

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search chats by name."""
        query = request.query_params.get('q', '')
        chats = self.get_queryset().filter(Q(name__icontains=query))
        page = self.paginate_queryset(chats)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add a user to the chat."""
        chat = self.get_object()
        user_id = request.data.get('user_id')
        ChatMembership.objects.get_or_create(chat=chat, user_id=user_id)
        return Response({'status': 'member added'})

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """Remove a user from the chat."""
        chat = self.get_object()
        user_id = request.data.get('user_id')
        ChatMembership.objects.filter(chat=chat, user_id=user_id).delete()
        return Response({'status': 'member removed'})


class MessageViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """List and create messages for a chat."""

    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsChatParticipant]

    def get_queryset(self):
        chat_id = self.request.query_params.get('chat')
        queryset = Message.objects.filter(chat__memberships__user=self.request.user)
        if chat_id:
            queryset = queryset.filter(chat_id=chat_id)
        return queryset.select_related('sender', 'chat').prefetch_related('read_by')

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a message as read by the current user."""
        message = self.get_object()
        message.mark_read(request.user)
        return Response({'status': 'marked as read'})


class ContactListView(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Expose a list of contacts (users) for the current user."""

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return User.objects.filter(Q(username__icontains=query) | Q(first_name__icontains=query)).order_by('username')

"""Serializers for chats, messages and related objects."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from backend.users.serializers import UserProfileSerializer

from .models import Chat, ChatMembership, Message

User = get_user_model()


class ChatMembershipSerializer(serializers.ModelSerializer):
    """Serialize membership data for chat participants."""

    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = ChatMembership
        fields = ('id', 'user', 'joined_at', 'is_admin')


class ChatSerializer(serializers.ModelSerializer):
    """Serialize chat details including member previews."""

    memberships = ChatMembershipSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = (
            'id',
            'name',
            'chat_type',
            'created_by',
            'created_at',
            'memberships',
            'last_message',
        )
        read_only_fields = ('created_by', 'created_at')

    def get_last_message(self, obj: Chat):
        message = obj.messages.first()
        return MessageSerializer(message).data if message else None

    def create(self, validated_data):
        request = self.context['request']
        chat = Chat.objects.create(created_by=request.user, **validated_data)
        participants = self.context['request'].data.get('participants', [])
        ChatMembership.objects.create(chat=chat, user=request.user, is_admin=True)
        for user_id in participants:
            if user_id == request.user.id:
                continue
            ChatMembership.objects.get_or_create(chat=chat, user_id=user_id)
        return chat


class MessageSerializer(serializers.ModelSerializer):
    """Serialize message content along with read receipts."""

    sender = UserProfileSerializer(read_only=True)
    read_by = UserProfileSerializer(read_only=True, many=True)

    class Meta:
        model = Message
        fields = (
            'id',
            'chat',
            'sender',
            'content',
            'created_at',
            'updated_at',
            'read_by',
            'is_edited',
        )
        read_only_fields = ('sender', 'created_at', 'updated_at', 'read_by', 'is_edited')

    def create(self, validated_data):
        request = self.context['request']
        validated_data['sender'] = request.user
        message = super().create(validated_data)
        message.mark_read(request.user)
        return message

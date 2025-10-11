"""Serializers for messenger REST API."""
from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers

from apps.chat.models import Chat, ChatMember, Message, MessageRead

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer used for user registration."""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
        )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Ensure the two password fields match and validate complexity."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        """Create a new user with a hashed password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for representing user data."""

    is_online = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'status_message',
            'avatar',
            'last_seen',
            'is_online',
        )
        read_only_fields = ('id', 'last_seen', 'is_online', 'avatar')

    def get_is_online(self, obj: User) -> bool:
        """Return whether the user is considered online."""
        return obj.is_online


class ChatMemberSerializer(serializers.ModelSerializer):
    """Serializer for chat members."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = ChatMember
        fields = ('id', 'user', 'joined_at', 'is_admin')
        read_only_fields = ('id', 'joined_at')


class MessageReadSerializer(serializers.ModelSerializer):
    """Serializer for message read receipts."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = MessageRead
        fields = ('id', 'user', 'read_at')
        read_only_fields = ('id', 'read_at', 'user')


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for reading message data."""

    sender = UserSerializer(read_only=True)
    read_receipts = MessageReadSerializer(read_only=True, many=True)

    class Meta:
        model = Message
        fields = (
            'id',
            'chat',
            'sender',
            'content',
            'attachment',
            'created_at',
            'updated_at',
            'is_deleted',
            'read_receipts',
        )
        read_only_fields = (
            'id',
            'created_at',
            'updated_at',
            'is_deleted',
            'read_receipts',
            'sender',
        )


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer used for creating and updating messages."""

    class Meta:
        model = Message
        fields = ('chat', 'content', 'attachment')

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Ensure a message has content or an attachment."""
        if not attrs.get('content') and not attrs.get('attachment'):
            raise serializers.ValidationError('Message must include text or attachment.')
        request = self.context['request']
        chat = attrs.get('chat')
        if chat and not chat.members.filter(id=request.user.id).exists():
            raise serializers.ValidationError('You are not a member of this chat.')
        return attrs

    def create(self, validated_data: dict[str, Any]) -> Message:
        """Create a message for the current user."""
        request = self.context['request']
        message = Message.objects.create(sender=request.user, **validated_data)
        Chat.objects.filter(pk=message.chat_id).update(updated_at=timezone.now())
        return message


class ChatSerializer(serializers.ModelSerializer):
    """Serializer for listing chats."""

    last_message = MessageSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = (
            'id',
            'name',
            'is_group',
            'created_by',
            'created_at',
            'updated_at',
            'last_message',
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'last_message', 'created_by')


class ChatDetailSerializer(ChatSerializer):
    """Detailed serializer including members."""

    members = ChatMemberSerializer(source='chat_members', many=True, read_only=True)
    member_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    member_usernames = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )

    class Meta(ChatSerializer.Meta):
        fields = ChatSerializer.Meta.fields + ('members', 'member_ids', 'member_usernames')

    def create(self, validated_data: dict[str, Any]) -> Chat:
        """Create chat and attach members."""
        member_ids = validated_data.pop('member_ids', [])
        member_usernames = validated_data.pop('member_usernames', [])
        if member_usernames:
            users = User.objects.filter(username__in=member_usernames).values_list('id', flat=True)
            member_ids.extend([uid for uid in users if uid not in member_ids])
        chat = super().create(validated_data)
        for user_id in member_ids:
            ChatMember.objects.get_or_create(chat=chat, user_id=user_id)
        return chat

    def update(self, instance: Chat, validated_data: dict[str, Any]) -> Chat:
        """Update chat details and synchronize membership."""
        member_ids = validated_data.pop('member_ids', None)
        member_usernames = validated_data.pop('member_usernames', [])
        if member_ids is not None and member_usernames:
            users = User.objects.filter(username__in=member_usernames).values_list('id', flat=True)
            member_ids.extend([uid for uid in users if uid not in member_ids])
        elif member_ids is None and member_usernames:
            member_ids = list(
                User.objects.filter(username__in=member_usernames).values_list('id', flat=True)
            )
        chat = super().update(instance, validated_data)
        if member_ids is not None:
            ChatMember.objects.filter(chat=chat).exclude(user_id__in=member_ids).delete()
            for user_id in member_ids:
                ChatMember.objects.get_or_create(chat=chat, user_id=user_id)
        return chat


class MessageReadUpdateSerializer(serializers.Serializer):
    """Serializer for marking messages as read."""

    read = serializers.BooleanField(default=True)

    def save(self, **kwargs: Any) -> MessageRead:
        """Mark the message as read for the current user."""
        message: Message = self.context['message']
        user = self.context['request'].user
        if self.validated_data.get('read'):
            receipt, _ = MessageRead.objects.update_or_create(
                message=message,
                user=user,
                defaults={'read_at': timezone.now()},
            )
            return receipt
        MessageRead.objects.filter(message=message, user=user).delete()
        raise serializers.ValidationError('Read flag must be true to mark message as read.')

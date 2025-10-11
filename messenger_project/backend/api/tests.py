"""Tests for API functionality."""
from __future__ import annotations

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from backend.users.models import User
from .models import Chat, ChatMembership, Message


class ChatApiTests(APITestCase):
    """Test chat creation and message flow."""

    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass1234')
        self.client.force_authenticate(self.user)

    def test_create_chat_and_message(self):
        response = self.client.post(reverse('chat-list'), {'name': 'General', 'chat_type': 'group', 'participants': []})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        chat_id = response.data['id']
        chat = Chat.objects.get(pk=chat_id)
        self.assertTrue(ChatMembership.objects.filter(chat=chat, user=self.user).exists())

        message_response = self.client.post(reverse('message-list'), {'chat': chat_id, 'content': 'Hello'})
        self.assertEqual(message_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.filter(chat=chat).count(), 1)

    def test_chat_list_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('chat-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

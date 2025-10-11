"""WebSocket consumers enabling real-time chat updates."""
from __future__ import annotations

import json
from typing import Any

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

from .models import Chat, Message
from .serializers import MessageSerializer

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """Handle WebSocket connections for chat rooms."""

    async def connect(self) -> None:
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.group_name = f'chat_{self.chat_id}'
        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
            return
        is_member = await self._is_member(user.id, self.chat_id)
        if not is_member:
            await self.close()
            return
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code: int) -> None:  # noqa: ARG002
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data: str | None = None, bytes_data: bytes | None = None) -> None:  # noqa: D401
        """Handle incoming messages from WebSocket clients."""

        if text_data is None:
            return
        data = json.loads(text_data)
        message = await self._create_message(self.scope['user'].id, self.chat_id, data.get('content', ''))
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat.message',
                'message': MessageSerializer(message).data,
            },
        )

    async def chat_message(self, event: dict[str, Any]) -> None:
        """Send the message payload to WebSocket clients."""
        await self.send(text_data=json.dumps(event['message']))

    @database_sync_to_async
    def _create_message(self, user_id: int, chat_id: int, content: str) -> Message:
        chat = Chat.objects.get(pk=chat_id)
        message = Message.objects.create(chat=chat, sender_id=user_id, content=content)
        message.read_by.add(user_id)
        return message

    @database_sync_to_async
    def _is_member(self, user_id: int, chat_id: int) -> bool:
        return Chat.objects.filter(id=chat_id, memberships__user_id=user_id).exists()

"""Views for the messenger REST API."""
from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from rest_framework import mixins, permissions, serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView as SimpleJWTTokenRefreshView

from apps.chat.models import Chat, Message

from .serializers import (
    ChatDetailSerializer,
    ChatSerializer,
    MessageCreateSerializer,
    MessageReadSerializer,
    MessageReadUpdateSerializer,
    MessageSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    """Pagination class with configurable page size."""

    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class RegisterView(APIView):
    """Handle user registration requests."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args: Any, **kwargs: Any) -> Response:
        """Create a new user and return serialized data."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = UserSerializer(user).data
        return Response(data, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """Blacklist refresh tokens on logout."""

    def post(self, request, *args: Any, **kwargs: Any) -> Response:
        """Blacklist the provided refresh token and respond with success."""
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as exc:  # pragma: no cover - defensive programming
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)


class UserViewSet(mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    """Read-only viewset for user data."""

    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    queryset = User.objects.all().order_by('username')

    def get_queryset(self):
        """Return queryset filtered by search parameter."""
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )
        return queryset

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request, *args: Any, **kwargs: Any) -> Response:
        """Return data for the authenticated user."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def perform_update(self, serializer: serializers.BaseSerializer) -> None:
        """Allow users to update only their own profile."""
        instance = serializer.instance
        if instance != self.request.user:
            raise permissions.PermissionDenied('You can only update your own profile.')
        serializer.save()


class ChatViewSet(viewsets.ModelViewSet):
    """CRUD operations for chats."""

    serializer_class = ChatSerializer
    pagination_class = StandardResultsSetPagination
    queryset = Chat.objects.all().select_related('created_by').prefetch_related('chat_members__user')

    def get_queryset(self):
        """Return chats the user participates in with optional search filter."""
        user = self.request.user
        queryset = super().get_queryset().filter(members=user).prefetch_related('messages__sender')
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in {'retrieve', 'create', 'update', 'partial_update'}:
            return ChatDetailSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer: serializers.BaseSerializer) -> None:
        """Set created_by and add members during chat creation."""
        member_ids = serializer.validated_data.get('member_ids', []) or []
        if self.request.user.id not in member_ids:
            member_ids.append(self.request.user.id)
        serializer.save(created_by=self.request.user, member_ids=member_ids)

    def perform_update(self, serializer: serializers.BaseSerializer) -> None:
        """Ensure the current user remains a member when updating a chat."""
        member_ids = serializer.validated_data.get('member_ids')
        member_usernames = serializer.validated_data.get('member_usernames')
        if member_ids is not None:
            if self.request.user.id not in member_ids:
                member_ids.append(self.request.user.id)
        elif member_usernames is not None:
            if self.request.user.username not in member_usernames:
                member_usernames.append(self.request.user.username)
        serializer.save(member_ids=member_ids, member_usernames=member_usernames)

    @action(detail=True, methods=['get'], url_path='messages')
    def messages(self, request, *args: Any, **kwargs: Any) -> Response:
        """Return paginated messages for a chat."""
        chat = self.get_object()
        messages = chat.messages.select_related('sender').prefetch_related('read_receipts__user')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(messages, request)
        serializer = MessageSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """Manage messages including create, retrieve, update, and delete."""

    queryset = Message.objects.select_related('chat', 'sender').prefetch_related('read_receipts__user')
    serializer_class = MessageSerializer
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        """Use a different serializer when creating or updating messages."""
        if self.action in {'create', 'update', 'partial_update'}:
            return MessageCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        """Limit messages to chats the current user participates in."""
        base_queryset = super().get_queryset()
        return base_queryset.filter(chat__members=self.request.user)

    def perform_create(self, serializer: serializers.BaseSerializer) -> None:
        """Save the message and mark sender as having read it."""
        message: Message = serializer.save()
        message.mark_read_for(self.request.user)

    def perform_update(self, serializer: serializers.BaseSerializer) -> None:
        """Allow updating the message content by the sender only."""
        message = self.get_object()
        if message.sender != self.request.user:
            raise permissions.PermissionDenied('You can only edit your own messages.')
        serializer.save()

    def perform_destroy(self, instance: Message) -> None:
        """Soft delete a message by flagging it as deleted."""
        if instance.sender != self.request.user:
            raise permissions.PermissionDenied('You can only delete your own messages.')
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])

    @action(detail=True, methods=['post'], url_path='read')
    def mark_read(self, request, *args: Any, **kwargs: Any) -> Response:
        """Mark a message as read for the current user."""
        message = self.get_object()
        serializer = MessageReadUpdateSerializer(data=request.data, context={'request': request, 'message': message})
        serializer.is_valid(raise_exception=True)
        receipt = serializer.save()
        data = MessageReadSerializer(receipt).data
        return Response(data, status=status.HTTP_200_OK)


class TokenPairView(TokenObtainPairView):
    """Custom token obtain pair view to include user data."""

    def post(self, request, *args: Any, **kwargs: Any) -> Response:
        """Return token pair along with user profile data."""
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            user = User.objects.get(username=request.data.get('username'))
            response.data['user'] = UserSerializer(user).data
        return response


class TokenRefreshView(SimpleJWTTokenRefreshView):
    """Wrapper around SimpleJWT refresh view for clarity."""

    pass


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_health(request) -> Response:
    """Provide a simple health endpoint for monitoring."""
    return Response({'status': 'ok', 'time': timezone.now()})

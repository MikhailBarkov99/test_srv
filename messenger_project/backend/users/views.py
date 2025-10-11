"""Views for user registration, authentication helpers and profile management."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .serializers import UserProfileSerializer, UserRegistrationSerializer

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """Allow anonymous users to create an account."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the authenticated user's profile."""

    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class UserSearchView(generics.ListAPIView):
    """Search users by username, first name or last name."""

    serializer_class = UserProfileSerializer

    def get_queryset(self):
        term = self.request.query_params.get('q', '')
        return User.objects.filter(
            Q(username__icontains=term)
            | Q(first_name__icontains=term)
            | Q(last_name__icontains=term)
        ).order_by('username')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def set_online_status(request):
    """Update the online status for the current user."""

    status_value = request.data.get('is_online', True)
    user = request.user
    if status_value:
        user.mark_online()
    else:
        user.mark_offline()
    return Response({'is_online': user.is_online, 'last_seen': user.last_seen})

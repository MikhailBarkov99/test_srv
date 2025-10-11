"""URL routing for the messenger REST API."""
from __future__ import annotations

from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from .views import (
    ChatViewSet,
    LogoutView,
    MessageViewSet,
    RegisterView,
    TokenPairView,
    TokenRefreshView,
    UserViewSet,
    api_health,
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('chats', ChatViewSet, basename='chat')
router.register('messages', MessageViewSet, basename='message')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', TokenPairView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path(
        'docs/',
        SpectacularSwaggerView.as_view(url_name='api-schema'),
        name='api-docs',
    ),
    path(
        'docs/redoc/',
        SpectacularRedocView.as_view(url_name='api-schema'),
        name='api-redoc',
    ),
    path(
        'docs/swagger/',
        SpectacularSwaggerView.as_view(url_name='api-schema'),
        name='api-swagger',
    ),
    path('health/', api_health, name='api-health'),
    path('', include(router.urls)),
]

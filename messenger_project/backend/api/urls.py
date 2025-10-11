"""Routes for the API app."""
from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ChatViewSet, ContactListView, MessageViewSet

router = DefaultRouter()
router.register(r'chats', ChatViewSet, basename='chat')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'contacts', ContactListView, basename='contact')

urlpatterns = [
    path('', include(router.urls)),
]

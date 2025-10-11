"""URL patterns for frontend templates."""
from __future__ import annotations

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('chat/<int:chat_id>/', views.chat_view, name='chat-detail'),
    path('chat/', views.chat_view, name='chat'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
]

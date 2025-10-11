"""Django views that serve the frontend templates."""
from __future__ import annotations

from django.shortcuts import render


def login_view(request):
    """Render the login page."""
    return render(request, 'login.html')


def register_view(request):
    """Render the registration page."""
    return render(request, 'register.html')


def index_view(request):
    """Render the chat overview page."""
    return render(request, 'index.html')


def chat_view(request, chat_id: int | None = None):
    """Render the chat conversation page."""
    return render(request, 'chat.html', {'chat_id': chat_id})


def profile_view(request):
    """Render the user profile page."""
    return render(request, 'profile.html')

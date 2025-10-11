"""User related tests."""
from __future__ import annotations

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class UserRegistrationTests(APITestCase):
    """Ensure registration endpoint works as expected."""

    def test_register_user(self):
        payload = {
            'username': 'bob',
            'password': 'StrongPass123',
            'password_confirm': 'StrongPass123',
            'email': 'bob@example.com',
        }
        response = self.client.post(reverse('users:register'), payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='bob').exists())

    def test_password_mismatch(self):
        payload = {
            'username': 'charlie',
            'password': 'StrongPass123',
            'password_confirm': 'StrongPass124',
        }
        response = self.client.post(reverse('users:register'), payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

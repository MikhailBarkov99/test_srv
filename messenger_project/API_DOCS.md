# Messenger API Documentation

This document summarises the available REST API endpoints. All endpoints are prefixed with `/api/` and require JWT authentication unless explicitly stated.

## Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | Register a new user |
| `/api/auth/login/` | POST | Obtain access and refresh tokens |
| `/api/auth/logout/` | POST | Blacklist refresh token |
| `/api/auth/refresh/` | POST | Refresh access token |

### Example: Register

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
        "username": "alice",
        "email": "alice@example.com",
        "password": "ChangeMe123",
        "password_confirm": "ChangeMe123"
      }'
```

### Example: Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "ChangeMe123"}'
```

## Users

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/users/` | GET | List users (search via `?search=`) |
| `/api/users/{id}/` | GET | Retrieve user profile |
| `/api/users/me/` | GET | Retrieve authenticated user profile |
| `/api/users/{id}/` | PATCH | Update user profile |

## Chats

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chats/` | GET | List chats the user belongs to |
| `/api/chats/` | POST | Create a chat (fields: `name`, `is_group`, `member_ids`, `member_usernames`) |
| `/api/chats/{id}/` | GET | Chat detail |
| `/api/chats/{id}/` | PATCH | Update chat name/members |
| `/api/chats/{id}/messages/` | GET | Paginated messages for chat |

### Example: Create chat

```bash
curl -X POST http://localhost:8000/api/chats/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
        "name": "Team",
        "is_group": true,
        "member_usernames": ["alice", "bob"]
      }'
```

## Messages

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/messages/` | POST | Send a message (fields: `chat`, `content`, `attachment`) |
| `/api/messages/{id}/` | GET | Retrieve message |
| `/api/messages/{id}/` | PATCH | Update message (sender only) |
| `/api/messages/{id}/` | DELETE | Soft delete message |
| `/api/messages/{id}/read/` | POST | Mark message as read |

### Example: Send message

```bash
curl -X POST http://localhost:8000/api/messages/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -F "chat=1" \
  -F "content=Hello team!"
```

## Utilities

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health/` | GET | Health check (no auth required) |
| `/api/schema/` | GET | OpenAPI schema (when enabled) |

## Pagination

List endpoints return paginated responses in the form:

```json
{
  "count": 40,
  "next": "http://localhost:8000/api/chats/?page=2",
  "previous": null,
  "results": []
}
```

Use `?page=` and `?page_size=` to navigate results.

## Error Handling

Errors follow standard DRF formats:

```json
{
  "detail": "Error message"
}
```

Validation errors provide field-level feedback.

## Rate Limiting

`django-ratelimit` is installed and ready for configuration. Update settings to enforce desired limits (e.g., login attempts per minute).

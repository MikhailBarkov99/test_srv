# Messenger Project

A full-featured real-time messenger built with Django, Django REST Framework and Django Channels. The application provides JWT authentication, chat management, messaging with read receipts, search, and a vanilla JavaScript front-end that consumes the REST API and WebSocket endpoints.

## Features

- User registration, authentication and profile management
- Private and group chats with membership management
- Real-time messaging powered by WebSockets (Django Channels + Redis)
- Message history with pagination and read receipts
- Search users and chats
- JWT authentication with refresh tokens
- Swagger UI documentation at `/api/docs/`
- Dockerized deployment with PostgreSQL, Redis and Nginx

## Quick Start

1. Clone the repository and change into the project directory.
2. Create a virtual environment and install dependencies from `requirements.txt`.
3. Copy `.env.example` to `.env` and update configuration values.
4. Apply migrations with `python backend/manage.py migrate`.
5. Create a superuser using `python backend/manage.py createsuperuser`.
6. Collect static files with `python backend/manage.py collectstatic`.
7. Start the development server: `python backend/manage.py runserver`.
8. Open `http://localhost:8000/frontend/index.html` (or serve via static files) to access the web client.

Detailed setup instructions are documented in [`README_LOCAL_DEV.md`](README_LOCAL_DEV.md). Docker deployment steps are available in [`README_DOCKER_DEPLOY.md`](README_DOCKER_DEPLOY.md). Database migration instructions for PostgreSQL are in [`DATABASE_MIGRATION.md`](DATABASE_MIGRATION.md).

## API Overview

| Endpoint | Description |
| --- | --- |
| `/auth/register/` | Register a new user |
| `/auth/token/` | Obtain JWT pair |
| `/auth/token/refresh/` | Refresh JWT |
| `/auth/me/` | Retrieve/update profile |
| `/auth/status/` | Update online status |
| `/api/chats/` | CRUD operations for chats |
| `/api/chats/{id}/add_member/` | Add member to chat |
| `/api/chats/{id}/remove_member/` | Remove member |
| `/api/chats/search/` | Search chats |
| `/api/messages/` | List/create messages |
| `/api/messages/{id}/mark_read/` | Mark message read |
| `/api/contacts/` | List contacts |
| `/ws/chats/<chat_id>/` | WebSocket endpoint for chat updates |

Swagger UI with model schemas and authentication documentation is available at `/api/docs/` once the server is running.

## Technology Stack

- **Backend:** Django, Django REST Framework, Django Channels, Redis
- **Authentication:** djangorestframework-simplejwt
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Documentation:** drf-yasg (Swagger UI)
- **Deployment:** Docker, docker-compose, Gunicorn, Nginx

## Screenshots

Screenshots of the UI can be added to the `frontend/assets/` directory and referenced here.

## Testing

Run Django tests with:

```bash
python backend/manage.py test
```

Pytest configuration is provided via `requirements-dev.txt` if you prefer pytest:

```bash
pytest
```

## License

This project is released under the MIT License. See [LICENSE](LICENSE) if available or update this section with your chosen license.

# Messenger Project

A production-ready messenger built with Django, Django REST Framework, and a responsive frontend served through Django templates. The project exposes a comprehensive REST API secured with JWT authentication and includes deployment artefacts for Docker-based environments.

## Features

- 🔐 JWT authentication with registration, login, logout, and refresh endpoints
- 💬 Private and group chats with full CRUD operations
- ✉️ Message history with pagination, read receipts, and attachment support
- 🔎 Search across chats and users
- 🖥️ Responsive frontend served via Django templates with modern JavaScript
- 📡 Ready for WebSocket upgrades via Django Channels
- 📄 Automatic OpenAPI schema generation (via `drf-spectacular`)
- 🧪 Test scaffolding and coverage tooling
- 📦 Docker and Docker Compose configuration for production deployment

## Architecture Overview

```
┌────────────────────┐
│   Frontend (JS)    │
│  Templates/Static  │
└────────┬───────────┘
         │ AJAX / JWT
┌────────▼───────────┐       ┌────────────────────┐
│ Django Views       │       │ PostgreSQL / SQLite │
│ (serves templates) │       └────────────────────┘
└────────┬───────────┘                 ▲
         │ REST API                    │ ORM
┌────────▼───────────┐       ┌────────────────────┐
│ Django REST        │◄──────│ Redis (optional)   │
│ Framework (API)    │       └────────────────────┘
└────────┬───────────┘
         │ JWT Auth
┌────────▼───────────┐
│ Business Logic     │
│ (Users/Chats)      │
└────────────────────┘
```

## Project Structure

```
messenger_project/
├── manage.py
├── messenger_project/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── chat/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── migrations/
│   │   │   └── __init__.py
│   │   └── models.py
│   └── users/
│       ├── __init__.py
│       ├── admin.py
│       └── models.py
├── frontend/
│   ├── __init__.py
│   ├── urls.py
│   ├── views.py
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/
│   │       ├── api.js
│   │       └── app.js
│   └── templates/
│       ├── base.html
│       ├── chat.html
│       ├── index.html
│       ├── login.html
│       ├── profile.html
│       ├── register.html
│       └── partials/chat_modal.html
├── staticfiles/
├── requirements.txt
├── requirements-postgres.txt
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── README.md
├── API_DOCS.md
├── DEPLOYMENT.md
└── .env.example
```

## Quick Start

### 1. Clone and set up the environment

```bash
git clone <repo_url>
cd messenger_project
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and set SECRET_KEY, DEBUG, database credentials, etc.
```

### 3. Apply migrations, collect static assets, and create a superuser

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 4. Run the development server

```bash
python manage.py runserver
```

Access the application:

- Frontend: http://localhost:8000/
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

## Testing

Run unit tests and generate coverage reports:

```bash
python manage.py test
coverage run --source='.' manage.py test
coverage report
```

## API Documentation

The API is fully documented in [API_DOCS.md](API_DOCS.md). An OpenAPI schema is exposed at `/api/schema/`, and interactive Swagger UI and Redoc frontends are available at `/api/docs/` and `/api/docs/redoc/` when running the Django server.

## Deployment

Docker and cloud deployment guides can be found in [DEPLOYMENT.md](DEPLOYMENT.md). The provided `docker-compose.yml` orchestrates the Django app, PostgreSQL, Redis, and Nginx reverse proxy.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

## License

This project is provided without a specific license. Adjust to your organisational needs.

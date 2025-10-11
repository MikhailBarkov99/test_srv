# Docker Deployment Guide

## 1. Prerequisites

- Docker 24+
- Docker Compose Plugin (v2+)

## 2. Configure Environment Variables

1. Copy `.env.example` to `.env` and adjust values for production (secure `SECRET_KEY`, disable `DEBUG`, update `ALLOWED_HOSTS`, set PostgreSQL credentials, configure Redis URL).
2. Ensure the `.env` file is located in the project root.

## 3. Build Images

```bash
docker compose build
```

## 4. Launch Containers

```bash
docker compose up -d
```

This starts the web, PostgreSQL, Redis and Nginx services.

## 5. Apply Migrations

```bash
docker compose exec web python backend/manage.py migrate
```

## 6. Create Superuser

```bash
docker compose exec web python backend/manage.py createsuperuser
```

## 7. Verify Deployment

- Visit `http://<server-host>/` for the application.
- API Swagger UI: `http://<server-host>/api/docs/`.

## 8. View Logs

```bash
docker compose logs -f web
```

## 9. Stop and Restart

- Stop: `docker compose down`
- Restart: `docker compose up -d`

## 10. Database Backup & Restore

- Backup PostgreSQL:
  ```bash
  docker compose exec db pg_dump -U messenger messenger > backup.sql
  ```
- Restore:
  ```bash
  cat backup.sql | docker compose exec -T db psql -U messenger messenger
  ```

## Additional Notes

- For development with live reload, use `docker-compose.dev.yml`:
  ```bash
  docker compose -f docker-compose.dev.yml up
  ```
- For production tuned settings, use `docker-compose.prod.yml`.

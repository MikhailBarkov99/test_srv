# Deployment Guide

This guide covers local development, Docker-based deployments, and production configuration with PostgreSQL and SSL.

## Local Development

1. **Clone the repository and install dependencies**
   ```bash
   git clone <repo_url>
   cd messenger_project
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Set SECRET_KEY, DEBUG=True, DATABASE=sqlite
   ```

3. **Run migrations and start server**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic --noinput
   python manage.py runserver
   ```

## Docker Deployment

1. **Build and run containers**
   ```bash
   docker-compose up -d --build
   ```

2. **Apply migrations and create superuser**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   docker-compose exec web python manage.py collectstatic --noinput
   ```

3. **Access services**
   - Application: http://localhost/
   - Django admin: http://localhost/admin/

## Cloud Deployment

1. **Provision server and install Docker**
   ```bash
   ssh user@your-server
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Deploy application**
   ```bash
   git clone <repo_url>
   cd messenger_project
   cp .env.example .env
   nano .env  # configure production settings (DEBUG=False, ALLOWED_HOSTS, PostgreSQL credentials)
   docker-compose up -d --build
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   docker-compose exec web python manage.py collectstatic --noinput
   ```

3. **Enable HTTPS with Let's Encrypt**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com -d www.your-domain.com
   ```

## PostgreSQL Migration

1. **Install PostgreSQL dependencies**
   ```bash
   pip install -r requirements-postgres.txt
   ```

2. **Configure `.env`**
   ```env
   DATABASE=postgresql
   DB_NAME=messenger_db
   DB_USER=messenger_user
   DB_PASSWORD=your_secure_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

3. **Create database and user**
   ```sql
   CREATE DATABASE messenger_db;
   CREATE USER messenger_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE messenger_db TO messenger_user;
   ```

4. **Migrate data from SQLite (optional)**
   ```bash
   python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 4 > datadump.json
   # Update .env to use PostgreSQL
   python manage.py migrate --run-syncdb
   python manage.py loaddata datadump.json
   ```

5. **Verify connection**
   ```bash
   python manage.py dbshell
   ```

## Security Hardening

- Set `DEBUG=False` in production
- Configure `ALLOWED_HOSTS`
- Use HTTPS and secure cookies
- Enable HSTS headers (already configured when DEBUG is False)
- Rotate JWT secret keys periodically
- Configure `django-ratelimit` for sensitive endpoints
- Use a CDN or object storage for large attachments in production

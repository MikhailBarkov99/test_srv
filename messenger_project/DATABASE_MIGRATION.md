# Migrating from SQLite to PostgreSQL

## 1. Install PostgreSQL & Dependencies

- Install PostgreSQL server and client tools for your platform.
- Install development headers if required (e.g., `libpq-dev` on Debian/Ubuntu).
- Ensure `psycopg2-binary` is installed (included in `requirements.txt`).

## 2. Create Database and User

```bash
sudo -u postgres psql
CREATE DATABASE messenger;
CREATE USER messenger WITH PASSWORD 'strongpassword';
ALTER ROLE messenger SET client_encoding TO 'utf8';
ALTER ROLE messenger SET default_transaction_isolation TO 'read committed';
ALTER ROLE messenger SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE messenger TO messenger;
\q
```

## 3. Update `settings.py`

Edit `backend/config/settings.py` to use the PostgreSQL database by setting `DATABASE_URL` in `.env`:

```
DATABASE_URL=postgres://messenger:strongpassword@localhost:5432/messenger
```

Restart the application to load new settings. The helper in `settings.py` automatically parses the URL.

## 4. Migrate Data

If you need to migrate existing data from SQLite:

1. Dump SQLite data:
   ```bash
   python backend/manage.py dumpdata --exclude auth.permission --exclude contenttypes --indent 2 > data.json
   ```
2. Update `.env` with the PostgreSQL `DATABASE_URL`.
3. Apply migrations:
   ```bash
   python backend/manage.py migrate
   ```
4. Load data:
   ```bash
   python backend/manage.py loaddata data.json
   ```

## 5. Environment Variables

- `DATABASE_URL` should point to the PostgreSQL database.
- Ensure `ALLOWED_HOSTS` includes your hostnames.
- Update `REDIS_URL` if Redis runs on a different host.

## 6. Verify Connection

Run migrations and tests to ensure the database works correctly:

```bash
python backend/manage.py check
python backend/manage.py migrate --plan
python backend/manage.py test
```

Monitor logs for any connection errors. Once confirmed, remove the SQLite file to avoid confusion.

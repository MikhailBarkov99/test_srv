# Local Development Guide

## 1. Prepare the Environment

1. Install **Python 3.10+**.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 2. Configure the Project

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
2. Update `.env` with your settings (secret key, allowed hosts, database URL, Redis URL).
3. Apply database migrations:
   ```bash
   python backend/manage.py migrate
   ```
4. Create a superuser:
   ```bash
   python backend/manage.py createsuperuser
   ```
5. Collect static files:
   ```bash
   python backend/manage.py collectstatic
   ```

## 3. Run the Project

1. Start the Django server:
   ```bash
   python backend/manage.py runserver
   ```
2. Channels runs inside the ASGI server automatically. For local development you can rely on the built-in runserver.
3. Access the API at `http://127.0.0.1:8000/` and Swagger UI at `http://127.0.0.1:8000/api/docs/`.
4. Open the frontend static page: `frontend/index.html` (serve via `python -m http.server` if needed).

## 4. Additional Commands

- Create sample data:
  ```bash
  python backend/manage.py shell < scripts/sample_data.py
  ```
  (Create `scripts/sample_data.py` with your fixtures.)

- Run tests:
  ```bash
  python backend/manage.py test
  ```
  or using pytest (after installing `requirements-dev.txt`):
  ```bash
  pytest
  ```

- Run linters/formatters:
  ```bash
  black backend
  isort backend
  ```

Happy coding!

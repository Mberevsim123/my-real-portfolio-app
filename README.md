# Backend Portfolio

Professional backend developer portfolio built with Django to showcase projects, technical skills, blog posts, and contact information.

**Contents**

- **What it is**: A production-ready Django portfolio and blog with user accounts, project showcase, and an API.
- **Where to look**: configuration and runtime settings are in [portfolio_app/portfolio_app/settings.py](portfolio_app/portfolio_app/settings.py#L1-L40) and the application entrypoint is [portfolio_app/manage.py](portfolio_app/manage.py#L1).

**Features**

- Accounts system with a custom user model, registration, email verification, and password reset.
- Rich text blog editor via CKEditor and image uploads.
- Project listing and detail pages with tagging and search.
- REST API endpoints (DRF) with pagination, filtering and token auth.
- Optional Celery + Redis task processing and scheduled jobs.
- Optional AWS S3-backed static/media storage.
- Security, caching, and production-ready settings (Postgres, Whitenoise, HSTS).

Tech stack

- Python 3.11+ and Django 5
- PostgreSQL for production-grade persistence
- Django REST Framework for API endpoints
- Celery + Redis for background tasks (optional)
- AWS S3 (optional) for static and media file storage
- Whitenoise + Gunicorn for simple deployments

Requirements

- See the pinned dependencies in [requirements.txt](requirements.txt).

Quick start (development)

1. Clone the repo and change to the project directory:

   ```bash
   git clone <repository-url>
   cd portfolio_project
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Configure environment variables (example):
   - `SECRET_KEY` — Django secret key
   - `DEBUG` — `True` for development
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` — Postgres connection
   - `REDIS_URL` — (optional) Redis for cache/Celery
   - `USE_S3`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME` — (optional) S3 storage
   - `EMAIL_*` settings for outgoing email

   The project uses `python-decouple` in [portfolio_app/portfolio_app/settings.py](portfolio_app/portfolio_app/settings.py#L1) to read environment variables.

4. Run migrations, create a superuser and collect static files:

   ```bash
   cd portfolio_app
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic --noinput
   ```

5. Start the development server:

   ```bash
   python manage.py runserver
   ```

Running Celery (optional)

From the `portfolio_app` directory:

```bash
celery -A portfolio_app worker --loglevel=info
celery -A portfolio_app beat --loglevel=info
```

Deployment notes

- Use PostgreSQL in production; configure `DATABASES` via environment variables.
- Serve static files with Whitenoise or an S3-backed CDN when `USE_S3=True`.
- Use Gunicorn behind a reverse proxy (nginx) for production. Example:

```bash
gunicorn portfolio_app.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

- Ensure `DEBUG=False` and appropriate `ALLOWED_HOSTS`, `SECRET_KEY`, and secure cookie settings.

Management commands & utilities

- A management command to bootstrap site data exists: `python manage.py init_site` (see `portfolio/management/commands/init_site.py`).

Testing

- Run the Django test suite:

```bash
python manage.py test
```

Contributing

- Contributions are welcome. Fork the repository, open a feature branch, add tests, and submit a pull request.

License

- See the `LICENSE` file in the repository root for licensing details.

Contact

- This repository contains a personal portfolio site — use the site contact form in production or open an issue on the repository for questions about this codebase.

If you'd like, I can also:

- add a runnable Dockerfile and docker-compose for local development,
- generate a `.env.example` listing recommended environment variables,
- or run the test suite and fix any small issues found.

**Architecture**

High-level architecture (Mermaid):

```mermaid
graph LR
   client[User / Browser]
   nginx[Nginx / Reverse Proxy]
   gunicorn[Gunicorn]
   django[Django (portfolio_app)]
   db[(PostgreSQL)]
   redis[(Redis / Cache / Broker)]
   celery[Celery workers]
   s3[(AWS S3)]

   client --> nginx --> gunicorn --> django
   django --> db
   django --> redis
   django --> s3
   django --> celery
   celery --> redis
   celery --> db
```

Notes:

- The project is designed to run behind a reverse proxy (nginx) with Gunicorn serving the WSGI app.
- Optional services: Redis for caching and as Celery broker, Celery workers for background jobs, and S3 for static/media storage.

**Folder structure (key files & directories)**

```
portfolio_project/
├─ LICENSE
├─ README.md
├─ requirements.txt
├─ portfolio_app/
│  ├─ manage.py
+│  ├─ portfolio_app/
+│  │  ├─ asgi.py
+│  │  ├─ settings.py
+│  │  ├─ urls.py
+│  │  └─ wsgi.py
+│  ├─ accounts/
+│  │  ├─ models.py
+│  │  ├─ views.py
+│  │  ├─ forms.py
+│  │  └─ urls.py
+│  ├─ portfolio/
+│  │  ├─ models.py
+│  │  ├─ views.py
+│  │  ├─ api/
+│  │  │  ├─ serializers.py
+│  │  │  └─ viewsets.py
+│  │  └─ management/commands/init_site.py
+│  ├─ static/
+│  └─ templates/
├─ logs/
└─ media/
```

Quick pointers:

- App settings, security, and deployment configuration are in [portfolio_app/portfolio_app/settings.py](portfolio_app/portfolio_app/settings.py#L1-L40).
- Use [portfolio_app/manage.py](portfolio_app/manage.py#L1) for local management commands.

Want me to also export these diagrams as PNG/SVG files inside a new `/docs` directory and add a `.env.example`? I can do that next.

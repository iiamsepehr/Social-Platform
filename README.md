# Social Platform (Django UserHub)

A Django-based social platform with user accounts, posts, comments, likes, follows, and notifications, exposed through both server-rendered views and a REST API.

This project is under active development. This README reflects the current state of the codebase, not a target feature set. See [Roadmap](#roadmap) for what's planned next.

## Overview

The platform has two parallel surfaces:

- **`accounts` / `posts`** — traditional Django views (session-based auth, HTML templates) covering signup, login, profile management, an admin panel (ban/timeout/delete users), following, and notifications.
- **`api`** — a DRF-powered REST API (`/api/v1/`) exposing users, posts, comments, and notifications as a resource-oriented interface, built on the same underlying models.

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Framework | Django 5.2 |
| API | Django REST Framework |
| Database | PostgreSQL (via `psycopg`) |
| Auth | Session auth + JWT (`djangorestframework-simplejwt`) |
| Static files | WhiteNoise |
| Config | `python-dotenv` (`.env`-based settings) |

## Features

**Accounts**
- Custom `User` model extending `AbstractUser`, with role-based access (`USER` / `ADMIN`)
- Signup, login, logout, profile editing (username, email, password), account deletion
- Admin panel for managing users: add, delete, ban, unban, timeout
- Follow / unfollow between users, with database-level constraints preventing self-follows and duplicate follows

**Posts**
- Create, read, update, delete posts and comments
- Likes on posts, with a unique constraint preventing duplicate likes per user/post
- Notifications generated for likes, comments, and follows, with a read/unread state

**API (`/api/v1/`)**
- `users/`, `posts/`, `comments/`, `notifications/` — router-registered `ViewSet`s
- JWT and session authentication supported side by side (see [`docs/authentication.md`](docs/authentication.md))
- Object-level permissions: `IsOwnerOrAdmin` (author or admin can modify/delete) and `IsAdminRole`
- Pagination (`PageNumberPagination`, 10 items/page by default)
- Filtering and search via `django-filter`, `SearchFilter`, and `OrderingFilter`
- Query efficiency: `select_related` used on `Post`, `Comment`, and `Notification` querysets to avoid N+1 lookups
- Custom actions: follow/unfollow a user (`POST`/`DELETE /users/{id}/follow/`), mark a notification as read (`POST /notifications/{id}/read/`)

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL

### Installation

```bash
git clone https://github.com/iiamsepehr/Social-Platform.git
cd Social-Platform

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### Environment variables

Copy `.env.example` to `.env` and fill in your local values:

```bash
cp .env.example .env
```

Required variables: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, and the PostgreSQL connection details (`DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT`). `SECRET_KEY` must be a non-empty value — Django will not start with it blank.

### Run migrations and start the server

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The app is available at `http://127.0.0.1:8000/`, with the API under `http://127.0.0.1:8000/api/v1/` and the Django admin at `http://127.0.0.1:8000/admin/`.

## Project Structure

```
Django_UserHub/     # project settings, root URLconf, WSGI/ASGI entrypoints
accounts/           # custom User model, auth views, admin panel, follows, notifications
posts/              # Post, Comment, Like models and views
api/                # DRF serializers, viewsets, permissions, API routing
docs/               # authentication, testing, performance, and deployment docs
```

## Documentation

| Doc | Covers |
|---|---|
| [`docs/authentication.md`](docs/authentication.md) | JWT endpoints, usage, and configuration |
| [`docs/testing.md`](docs/testing.md) | Running the test suite, coverage, structure |
| [`docs/performance.md`](docs/performance.md) | Query indexing and load-test results |
| [`docs/deployment.md`](docs/deployment.md) | Docker Compose setup and configuration |

## Design Notes

- **Custom user model from day one** — `AUTH_USER_MODEL` is set to a custom `User` extending `AbstractUser`, avoiding the well-known pain of migrating off Django's default user model later.
- **Database-level integrity, not just application logic** — constraints like `unique_follow`, `prevent_self_follow`, and `unique_post_like` are enforced at the database layer via `UniqueConstraint`/`CheckConstraint`, not just checked in views.
- **Object-level permissions over blanket flags** — `IsOwnerOrAdmin` checks ownership per-object rather than relying on a single global permission class, so the same endpoint can allow read access broadly while restricting writes to the owner or an admin.

## Roadmap

**Implemented:**
- JWT authentication alongside session auth
- Automated test suite (pytest/pytest-django) with coverage reporting
- Containerization via Docker Compose (Django + Gunicorn + WhiteNoise + Postgres)
- Query indexing and load testing

**Planned:**
- API rate limiting / throttling on DRF endpoints
- CI/CD pipeline for linting, testing, and deployment
- Caching and background jobs (Redis, Celery/Celery Beat)
- Real-time updates (Django Channels/WebSockets)
- Observability (structured logging, error tracking)
- API documentation via `drf-spectacular` (OpenAPI schema)
- Code quality tooling (Ruff, Black, mypy, pre-commit)
- Infrastructure as code (Terraform), Nginx in front of Gunicorn
- Architecture Decision Records (ADRs)

## License

Not yet specified.

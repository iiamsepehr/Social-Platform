# Deployment (Docker)

Containerizes the app for a reproducible local or production-adjacent environment: Django running under Gunicorn, WhiteNoise serving static files, and PostgreSQL, managed by Docker Compose.

## Files

| File | Purpose |
|---|---|
| `Dockerfile` | Builds the Django app image (Python 3.12), installs `requirements.txt`, runs Gunicorn, includes a healthcheck |
| `entrypoint.sh` | Runs on container start: applies migrations, collects static files, then hands off to Gunicorn |
| `docker-compose.yml` | Wires up two services — `web` (the Django app) and `db` (Postgres 16) — with a healthcheck so `web` waits for `db` to be ready |
| `.dockerignore` | Keeps `venv/`, `.git/`, local `.env`, etc. out of the image build context |
| `.env.docker.example` | Template env file for Compose; copy to `.env` before building |

## Running It

```bash
cp .env.docker.example .env
# edit .env: set a real SECRET_KEY and POSTGRES_PASSWORD

docker compose up --build
```

`db` starts and waits until Postgres reports healthy (`pg_isready`), then `web` builds, waits for that healthcheck via `depends_on: condition: service_healthy`, runs migrations and `collectstatic` via `entrypoint.sh`, and starts Gunicorn on port 8000.

Visit `http://localhost:8000/login/` (the root `/` route is not the app's entry point).

## Static Files

Static files are served by [WhiteNoise](https://whitenoise.readthedocs.io/) rather than a separate Nginx container:

- `whitenoise.middleware.WhiteNoiseMiddleware` sits directly after `SecurityMiddleware` in `MIDDLEWARE` (a WhiteNoise requirement).
- `STORAGES["staticfiles"]` uses `whitenoise.storage.CompressedManifestStaticFilesStorage`, which serves compressed, content-hashed filenames for cache-busting.
- `whitenoise` is listed in `requirements.txt`.

This is appropriate for the project's current size; a full production deployment would still typically put Nginx (or similar) in front for TLS, request buffering, and higher load — tracked separately under "Infrastructure as code" in the roadmap.

## Build Notes

- `requirements.txt` specifies `psycopg[binary]`, which ships a precompiled wheel, so the image does not need `gcc`/`libpq-dev` installed to build `psycopg` from source.
- `ALLOWED_HOSTS` is read from an `ALLOWED_HOSTS` env var (comma-separated), defaulting to `localhost,127.0.0.1`. Outside of `DEBUG=True`, Django rejects every request with an `Invalid HTTP_HOST header` error if this is empty.
- The `Dockerfile` includes a `HEALTHCHECK` that requests `/login/` using Python's standard library, avoiding the need for `curl`/`wget` in the image.

## Known Gaps

- No Nginx in front of Gunicorn — WhiteNoise handles static files adequately at the project's current scale, but production would benefit from a reverse proxy for TLS and load handling.
- No multi-stage build — less impactful now that the image no longer installs build tools that would need stripping out afterward.
- `seed_performance_data` / `seed_data` are not run automatically; invoke them manually via `docker compose exec web python manage.py seed_performance_data ...` if seeded data is needed in the container.

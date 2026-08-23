# Testing

This project uses `pytest` + `pytest-django` for the test suite and `pytest-cov` (built on `coverage.py`) for coverage reporting.

## Running the Tests

```bash
pip install -r requirements-dev.txt
pytest
```

With a coverage report:

```bash
pytest --cov=accounts --cov=posts --cov=api --cov-report=term-missing
```

`.coveragerc` excludes migrations, `manage.py`, and `apps.py` boilerplate from the report, since none of that is logic worth measuring coverage on.

## Database

Tests run against the same PostgreSQL engine configured in `settings.py` (via `DATABASE_*` env vars). There is no SQLite fallback, so a local or CI Postgres instance is required.

## Structure

Each app has a `tests/` package instead of a single `tests.py`, grouped by what's under test:

```
accounts/tests/
    test_models.py        # User, Follow — role logic, DB-level constraints
    test_views.py          # signup/login flows, ban & timeout enforcement, follow/unfollow
    test_admin_views.py    # admin-only moderation views (access control + actions)

posts/tests/
    test_models.py         # Post, Comment, Like — ordering, constraints

api/tests/
    test_permissions.py    # IsAdminRole, IsOwnerOrAdmin as isolated unit tests
    test_posts.py           # PostViewSet — CRUD, pagination, ownership
    test_comments.py        # CommentViewSet — CRUD, ownership
    test_users_follow.py    # UserViewSet.follow action
    test_notifications.py   # NotificationViewSet — recipient scoping, mark_read
    test_jwt_auth.py        # token issuance, refresh, verify, blacklist
```

Shared fixtures (`user`, `other_user`, `admin_user`, `auth_client`, `admin_client_api`, etc.) live in the root `conftest.py`.

## Coverage by Area

| Area | Coverage | Notes |
|---|---|---|
| `api/views.py` (DRF viewsets) | 100% | Primary product surface |
| `api/serializers.py` | 100% | |
| `api/permissions.py` | 92% | |
| `accounts/models.py`, `posts/models.py` | 100% | Constraints (`unique_follow`, `prevent_self_follow`, `unique_post_like`) are tested at the DB level |
| `accounts/views.py` (session-based) | 58% | Signup/login/ban/timeout covered; change-username/email/password and delete-account flows are not |
| `accounts/admin_views.py` | 78% | Core moderation actions covered; some edge branches are not |
| `posts/views.py` (session-based) | 15% | The DRF API is the primary tested interface; older session-based post CRUD views are next in line |
| `*/management/commands/seed_*.py` | 0% | Dev/benchmarking tooling, not application logic |

**Overall: 75%** across `accounts`, `posts`, and `api` (excluding migrations), from 66 tests. Closing the gap in `posts/views.py` is the next planned increment on this roadmap item.

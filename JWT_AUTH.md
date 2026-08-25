# Authentication

The API supports token-based auth via [`djangorestframework-simplejwt`](https://django-rest-framework-simplejwt.readthedocs.io/), alongside the existing session-based auth. Session auth is kept so the DRF browsable API and the older session-based account pages continue to work unchanged.

## Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/v1/token/` | POST | Exchange username + password for an access + refresh token pair |
| `/api/v1/token/refresh/` | POST | Exchange a refresh token for a new access token (rotation is on, so a new refresh token is also returned) |
| `/api/v1/token/verify/` | POST | Check whether a given token is still valid |
| `/api/v1/token/blacklist/` | POST | Invalidate a refresh token — the JWT equivalent of "log out" |

## Usage

Obtain a token:

```bash
curl -X POST http://localhost:8000/api/v1/token/ \
    -H "Content-Type: application/json" \
    -d '{"username": "yourusername", "password": "yourpassword"}'
```

Response:
```json
{"access": "eyJ...", "refresh": "eyJ..."}
```

Use the access token on any endpoint that requires authentication:

```bash
curl http://localhost:8000/api/v1/notifications/ \
    -H "Authorization: Bearer <access token>"
```

Refresh an expired access token:

```bash
curl -X POST http://localhost:8000/api/v1/token/refresh/ \
    -H "Content-Type: application/json" \
    -d '{"refresh": "<refresh token>"}'
```

Log out by blacklisting the refresh token so it can't be reused even if it leaks:

```bash
curl -X POST http://localhost:8000/api/v1/token/blacklist/ \
    -H "Content-Type: application/json" \
    -d '{"refresh": "<refresh token>"}'
```

## Configuration

Set in `SIMPLE_JWT` in `settings.py`:

- **Access token lifetime: 30 minutes.** Short-lived by design — a leaked token has a small exposure window.
- **Refresh token lifetime: 7 days.**
- **Rotation and blacklisting are both enabled** (`ROTATE_REFRESH_TOKENS`, `BLACKLIST_AFTER_ROTATION`): every time a refresh token is used, the old one is invalidated and a new one issued, so a stolen refresh token that has already been used once cannot be replayed. This is why `rest_framework_simplejwt.token_blacklist` is in `INSTALLED_APPS` and required its own migration.

## Test Coverage

Covered by `api/tests/test_jwt_auth.py`: token issuance with valid/invalid credentials, authenticated and unauthenticated access, garbage tokens, refresh, verify, and blacklist-then-reuse.

## Known Limitations

- Both session and JWT auth are accepted on every endpoint covered by `DEFAULT_AUTHENTICATION_CLASSES`; there is no per-endpoint restriction to JWT-only.
- No frontend/session-view integration — this is purely additive for API clients. Session-based login (`/login/`) is unaffected.
- The blacklist table grows unbounded unless pruned. `simplejwt` ships a `flushexpiredtokens` management command for this; it is not yet scheduled to run periodically.

# Performance: Query Indexing & Load Testing

This documents the benchmarking behind two composite indexes: `post_author_created_idx` and `notif_recipient_created_idx`.

**Environment:** PostgreSQL 16, local development machine, single connection, no caching. Dataset generated with `manage.py seed_performance_data`.

## Dataset

```bash
python manage.py seed_performance_data --posts 20000 --comments 40000 --notifications 20000
```

| Table | Rows |
|---|---|
| `posts_post` | 20,000 |
| `posts_comment` | 40,000 |
| `accounts_notification` | 20,000 |

## Query Benchmarks (`EXPLAIN ANALYZE`)

Both queries mirror the API's actual access pattern: a single user's posts or notifications, newest first, first page (`LIMIT 10`) — matching `GET /api/v1/posts/?author=<id>` and `GET /api/v1/notifications/`.

### `Post` — filter by `author_id`, order by `-created_at`

| | Plan | Execution time |
|---|---|---|
| Before (FK index only) | Bitmap Heap Scan → in-memory sort (top-N heapsort) | 3.16 ms |
| After (`post_author_created_idx` on `(author_id, created_at DESC)`) | Index Scan, no separate sort step | 0.067 ms |

~47x faster. The composite index is already in the required sort order, so the separate sort step is eliminated.

### `Notification` — filter by `recipient_id`, order by `-created_at`

| | Plan | Execution time |
|---|---|---|
| Before (no index) | Bitmap Heap Scan → in-memory sort | 2.78 ms |
| After (`notif_recipient_created_idx` on `(recipient_id, created_at DESC)`) | Index Scan, no separate sort step | 0.047 ms |

~59x faster.

At 20K rows the unindexed numbers are already small in absolute terms; the practical benefit is that the unindexed plan degrades linearly with table size, while the indexed plan stays roughly flat since Postgres can walk the index in order and stop at 10 rows.

## Load Test (Locust)

`locustfile.py` drives the two indexed endpoints plus `/api/v1/comments/` as a comparison point, authenticating through the session-based login flow.

```bash
locust -f locustfile.py --host=http://127.0.0.1:8000 \
    --users 50 --spawn-rate 10 --run-time 30s --headless \
    --csv=benchmarks/locust_report
```

**Result:** 1,173 requests, 0 failures, ~39 req/s sustained, against Django's single-process development server:

| Endpoint | Requests | Median | p95 | p99 |
|---|---|---|---|---|
| `GET /api/v1/posts/` | 533 | 44 ms | 95 ms | 160 ms |
| `GET /api/v1/notifications/` | 359 | 29 ms | 72 ms | 160 ms |
| `GET /api/v1/comments/` | 181 | 69 ms | 110 ms | 190 ms |
| `POST /login/` | 50 | 410 ms | 560 ms | 570 ms |

The `POST /login/` figure is an order of magnitude slower than the indexed GET endpoints by design, not by defect — it reflects Django's password hasher (PBKDF2, 700K+ iterations) doing real cryptographic work on every login, not a database or index cost. It appears in the results because every simulated user logs in once at the start of its session. The two indexed read endpoints held a 44 ms and 29 ms median respectively under 50 concurrent users with a 0% failure rate, on an unoptimized development server — not a production capacity figure, which would require Gunicorn with multiple workers (and ideally Nginx in front).

## Reproducing

```bash
python manage.py migrate
python manage.py seed_performance_data --posts 20000 --comments 40000 --notifications 20000

# EXPLAIN ANALYZE via manage.py shell, or directly in psql:
psql -d social_platform -c "EXPLAIN ANALYZE SELECT * FROM posts_post WHERE author_id = <id> ORDER BY created_at DESC LIMIT 10;"

# Load test
pip install locust
locust -f locustfile.py --host=http://127.0.0.1:8000 --users 50 --spawn-rate 10 --run-time 30s --headless
```

## Next Steps

- Re-run the load test behind Gunicorn (multiple workers) for a production-representative throughput number.
- Re-run without session-login overhead, using JWT auth, to isolate read-endpoint throughput.
- Add slow-query monitoring (e.g. `django-silk` or Postgres `log_min_duration_statement`) to catch regressions automatically.

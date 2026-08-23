"""
Locust load test for Social-Platform.

Targets the two endpoints backed by the indexes added in this round of
performance work:

  - GET /api/v1/posts/          (uses post_author_created_idx via ordering/filtering)
  - GET /api/v1/notifications/  (uses notif_recipient_created_idx, filtered by recipient)

Run headless, e.g.:

    locust -f locustfile.py --host=http://127.0.0.1:8000 \
        --users 50 --spawn-rate 10 --run-time 30s --headless \
        --csv=benchmarks/locust_report
"""

from locust import HttpUser, task, between


class SocialPlatformUser(HttpUser):
    wait_time = between(0.5, 2)

    def on_start(self):
        # Log in via the session-based Django login view (no JWT yet — see roadmap).
        login_page = self.client.get("/login/")
        csrf_token = self.client.cookies.get("csrftoken")

        self.client.post(
            "/login/",
            data={
                "username": "loadtest1",
                "password": "LoadTest123!",
                "csrfmiddlewaretoken": csrf_token,
            },
            headers={"Referer": self.client.base_url + "/login/"},
        )

    @task(3)
    def list_posts(self):
        self.client.get("/api/v1/posts/", name="/api/v1/posts/")

    @task(2)
    def list_notifications(self):
        self.client.get("/api/v1/notifications/", name="/api/v1/notifications/")

    @task(1)
    def list_comments(self):
        self.client.get("/api/v1/comments/", name="/api/v1/comments/")

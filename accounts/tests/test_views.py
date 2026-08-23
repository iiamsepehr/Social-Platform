import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from accounts.models import User


pytestmark = pytest.mark.django_db


class TestSignup:

    def test_signup_creates_user_and_logs_in(self):
        client = Client()

        response = client.post(
            reverse("signup"),
            {
                "username": "newperson",
                "email": "newperson@example.com",
                "password": "SomeSecurePass123!",
            },
        )

        assert response.status_code == 302
        assert User.objects.filter(username="newperson").exists()

        # session should now be authenticated -> profile page loads
        profile_response = client.get(reverse("profile"))
        assert profile_response.status_code == 200


class TestLogin:

    def test_login_success_redirects_to_profile(self, user):
        client = Client()

        response = client.post(
            reverse("login"),
            {"username": user.username, "password": "TestPass123!"},
        )

        assert response.status_code == 302
        assert response.url == reverse("profile")

    def test_login_wrong_password_shows_error(self, user):
        client = Client()

        response = client.post(
            reverse("login"),
            {"username": user.username, "password": "wrong-password"},
        )

        assert response.status_code == 200
        messages = list(response.context["messages"])
        assert any("Invalid username or password" in str(m) for m in messages)

    def test_banned_user_cannot_log_in(self, user):
        user.is_banned = True
        user.save()

        client = Client()
        response = client.post(
            reverse("login"),
            {"username": user.username, "password": "TestPass123!"},
        )

        assert response.status_code == 302
        assert response.url == reverse("login")

        # confirm session was never authenticated
        profile_response = client.get(reverse("profile"))
        assert profile_response.status_code == 302

    def test_timed_out_user_cannot_log_in_until_expiry(self, user):
        user.timeout_until = timezone.now() + timedelta(minutes=10)
        user.save()

        client = Client()
        response = client.post(
            reverse("login"),
            {"username": user.username, "password": "TestPass123!"},
        )

        assert response.status_code == 302
        assert response.url == reverse("login")

    def test_expired_timeout_clears_and_allows_login(self, user):
        user.timeout_until = timezone.now() - timedelta(minutes=10)
        user.save()

        client = Client()
        response = client.post(
            reverse("login"),
            {"username": user.username, "password": "TestPass123!"},
        )

        assert response.status_code == 302
        assert response.url == reverse("profile")

        user.refresh_from_db()
        assert user.timeout_until is None


class TestFollowViews:

    def test_follow_and_unfollow_user(self, user, other_user):
        client = Client()
        client.force_login(user)

        follow_response = client.post(
            reverse("follow_user", args=[other_user.id])
        )
        assert follow_response.status_code in (200, 302)
        assert other_user.followers.filter(follower=user).exists()

        unfollow_response = client.post(
            reverse("unfollow_user", args=[other_user.id])
        )
        assert unfollow_response.status_code in (200, 302)
        assert not other_user.followers.filter(follower=user).exists()

    def test_anonymous_cannot_follow(self, other_user):
        client = Client()
        response = client.post(
            reverse("follow_user", args=[other_user.id])
        )
        # login_required decorator redirects anonymous users
        assert response.status_code == 302

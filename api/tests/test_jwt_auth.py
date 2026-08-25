import pytest
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken


pytestmark = pytest.mark.django_db


def token_url():
    return reverse("token_obtain_pair")


def refresh_url():
    return reverse("token_refresh")


def verify_url():
    return reverse("token_verify")


def blacklist_url():
    return reverse("token_blacklist")


class TestObtainToken:

    def test_valid_credentials_return_access_and_refresh(self, api_client, user):
        response = api_client.post(
            token_url(), {"username": user.username, "password": "TestPass123!"}
        )
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data

    def test_invalid_password_rejected(self, api_client, user):
        response = api_client.post(
            token_url(), {"username": user.username, "password": "wrong"}
        )
        assert response.status_code == 401


class TestUseToken:

    def test_access_token_authenticates_requests(self, api_client, user):
        token_response = api_client.post(
            token_url(), {"username": user.username, "password": "TestPass123!"}
        )
        access = token_response.data["access"]

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get(reverse("notifications-list"))
        assert response.status_code == 200

    def test_no_token_is_rejected_on_authenticated_endpoint(self, api_client):
        response = api_client.get(reverse("notifications-list"))
        assert response.status_code == 401

    def test_garbage_token_is_rejected(self, api_client):
        api_client.credentials(HTTP_AUTHORIZATION="Bearer not-a-real-token")
        response = api_client.get(reverse("notifications-list"))
        assert response.status_code == 401


class TestRefreshToken:

    def test_refresh_returns_new_access_token(self, user):
        refresh = RefreshToken.for_user(user)

        from rest_framework.test import APIClient
        client = APIClient()
        response = client.post(refresh_url(), {"refresh": str(refresh)})

        assert response.status_code == 200
        assert "access" in response.data

    def test_invalid_refresh_token_rejected(self, api_client):
        response = api_client.post(refresh_url(), {"refresh": "not-a-real-token"})
        assert response.status_code == 401


class TestVerifyToken:

    def test_valid_access_token_verifies(self, api_client, user):
        token_response = api_client.post(
            token_url(), {"username": user.username, "password": "TestPass123!"}
        )
        access = token_response.data["access"]

        response = api_client.post(verify_url(), {"token": access})
        assert response.status_code == 200


class TestBlacklistToken:

    def test_blacklisting_refresh_token_invalidates_it(self, api_client, user):
        token_response = api_client.post(
            token_url(), {"username": user.username, "password": "TestPass123!"}
        )
        refresh = token_response.data["refresh"]

        blacklist_response = api_client.post(blacklist_url(), {"refresh": refresh})
        assert blacklist_response.status_code == 200

        # the blacklisted refresh token can no longer be used to get a new access token
        reuse_response = api_client.post(refresh_url(), {"refresh": refresh})
        assert reuse_response.status_code == 401

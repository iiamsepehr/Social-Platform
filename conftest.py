import pytest
from rest_framework.test import APIClient

from accounts.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_factory(db):
    """Factory for creating Users with sane defaults, overridable per call."""

    counter = {"n": 0}

    def create_user(**kwargs):
        counter["n"] += 1
        defaults = {
            "username": f"user{counter['n']}",
            "email": f"user{counter['n']}@example.com",
            "password": "TestPass123!",
        }
        defaults.update(kwargs)
        password = defaults.pop("password")
        user = User.objects.create_user(password=password, **defaults)
        return user

    return create_user


@pytest.fixture
def user(user_factory):
    return user_factory(username="alice", email="alice@example.com")


@pytest.fixture
def other_user(user_factory):
    return user_factory(username="bob", email="bob@example.com")


@pytest.fixture
def admin_user(user_factory):
    return user_factory(
        username="admin1",
        email="admin1@example.com",
        role=User.ADMIN,
        is_staff=True,
    )


@pytest.fixture
def auth_client(api_client, user):
    """APIClient authenticated as a normal user."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def other_auth_client(api_client, other_user):
    """APIClient authenticated as a second, distinct normal user."""
    api_client.force_authenticate(user=other_user)
    return api_client


@pytest.fixture
def admin_client_api(api_client, admin_user):
    """APIClient authenticated as an admin (named to avoid clashing with
    pytest-django's own 'admin_client' Django-test-client fixture)."""
    api_client.force_authenticate(user=admin_user)
    return api_client

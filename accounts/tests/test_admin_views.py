import pytest
from django.test import Client
from django.urls import reverse

from accounts.models import User


pytestmark = pytest.mark.django_db


class TestAdminAccessControl:

    def test_anonymous_redirected_to_login(self):
        client = Client()
        response = client.get(reverse("admin_users"))
        assert response.status_code == 302

    def test_normal_user_forbidden(self, user):
        client = Client()
        client.force_login(user)
        response = client.get(reverse("admin_users"))
        assert response.status_code == 403

    def test_admin_can_view_user_list(self, admin_user):
        client = Client()
        client.force_login(admin_user)
        response = client.get(reverse("admin_users"))
        assert response.status_code == 200


class TestAdminUserModeration:

    def test_admin_can_ban_user(self, admin_user, user):
        client = Client()
        client.force_login(admin_user)

        response = client.post(reverse("admin_ban_user", args=[user.id]))
        assert response.status_code == 302

        user.refresh_from_db()
        assert user.is_banned is True

    def test_admin_can_unban_user(self, admin_user, user):
        user.is_banned = True
        user.save()

        client = Client()
        client.force_login(admin_user)

        response = client.post(reverse("admin_unban_user", args=[user.id]))
        assert response.status_code == 302

        user.refresh_from_db()
        assert user.is_banned is False

    def test_admin_can_timeout_user(self, admin_user, user):
        client = Client()
        client.force_login(admin_user)

        response = client.post(reverse("admin_timeout_user", args=[user.id]))
        assert response.status_code == 302

        user.refresh_from_db()
        assert user.timeout_until is not None

    def test_admin_cannot_ban_self(self, admin_user):
        client = Client()
        client.force_login(admin_user)

        client.post(reverse("admin_ban_user", args=[admin_user.id]))

        admin_user.refresh_from_db()
        assert admin_user.is_banned is False

    def test_admin_can_delete_user(self, admin_user, user):
        client = Client()
        client.force_login(admin_user)

        client.post(reverse("admin_delete_user", args=[user.id]))

        assert not User.objects.filter(id=user.id).exists()

    def test_admin_cannot_delete_self(self, admin_user):
        client = Client()
        client.force_login(admin_user)

        client.post(reverse("admin_delete_user", args=[admin_user.id]))

        assert User.objects.filter(id=admin_user.id).exists()

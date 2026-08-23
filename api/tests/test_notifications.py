import pytest
from django.urls import reverse

from accounts.models import Notification


pytestmark = pytest.mark.django_db


def notifications_url():
    return reverse("notifications-list")


def mark_read_url(notification_id):
    return reverse("notifications-mark-read", args=[notification_id])


class TestListNotifications:

    def test_anonymous_cannot_list_notifications(self, api_client):
        response = api_client.get(notifications_url())
        assert response.status_code in (401, 403)

    def test_user_only_sees_own_notifications(self, auth_client, user, other_user):
        Notification.objects.create(
            recipient=user, actor=other_user, notification_type=Notification.FOLLOW
        )
        Notification.objects.create(
            recipient=other_user, actor=user, notification_type=Notification.FOLLOW
        )

        response = auth_client.get(notifications_url())
        assert response.status_code == 200
        assert response.data["count"] == 1


class TestMarkRead:

    def test_recipient_can_mark_notification_read(self, auth_client, user, other_user):
        notification = Notification.objects.create(
            recipient=user, actor=other_user, notification_type=Notification.FOLLOW
        )
        response = auth_client.post(mark_read_url(notification.id))
        assert response.status_code == 200

        notification.refresh_from_db()
        assert notification.is_read is True

    def test_marking_already_read_notification_is_idempotent(self, auth_client, user, other_user):
        notification = Notification.objects.create(
            recipient=user,
            actor=other_user,
            notification_type=Notification.FOLLOW,
            is_read=True,
        )
        response = auth_client.post(mark_read_url(notification.id))
        assert response.status_code == 200
        assert "already read" in response.data["detail"].lower()

    def test_cannot_mark_another_users_notification(self, other_auth_client, user, other_user):
        notification = Notification.objects.create(
            recipient=user, actor=other_user, notification_type=Notification.FOLLOW
        )
        response = other_auth_client.post(mark_read_url(notification.id))
        # get_queryset() is scoped to request.user, so it's invisible -> 404
        assert response.status_code == 404

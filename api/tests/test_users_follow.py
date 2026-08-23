import pytest
from django.urls import reverse

from accounts.models import Follow


pytestmark = pytest.mark.django_db


def follow_url(user_id):
    return reverse("users-follow", args=[user_id])


class TestFollow:

    def test_anonymous_cannot_follow(self, api_client, other_user):
        response = api_client.post(follow_url(other_user.id))
        assert response.status_code in (401, 403)

    def test_authenticated_user_can_follow(self, auth_client, user, other_user):
        response = auth_client.post(follow_url(other_user.id))
        assert response.status_code == 201
        assert Follow.objects.filter(follower=user, following=other_user).exists()

    def test_cannot_follow_self(self, auth_client, user):
        response = auth_client.post(follow_url(user.id))
        assert response.status_code == 400
        assert not Follow.objects.filter(follower=user, following=user).exists()

    def test_cannot_follow_twice(self, auth_client, user, other_user):
        Follow.objects.create(follower=user, following=other_user)
        response = auth_client.post(follow_url(other_user.id))
        assert response.status_code == 400


class TestUnfollow:

    def test_authenticated_user_can_unfollow(self, auth_client, user, other_user):
        Follow.objects.create(follower=user, following=other_user)
        response = auth_client.delete(follow_url(other_user.id))
        assert response.status_code == 200
        assert not Follow.objects.filter(follower=user, following=other_user).exists()

    def test_unfollow_when_not_following_returns_400(self, auth_client, other_user):
        response = auth_client.delete(follow_url(other_user.id))
        assert response.status_code == 400

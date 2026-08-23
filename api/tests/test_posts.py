import pytest
from django.urls import reverse

from posts.models import Post


pytestmark = pytest.mark.django_db


def posts_url():
    return reverse("posts-list")


def post_detail_url(post_id):
    return reverse("posts-detail", args=[post_id])


class TestListPosts:

    def test_anonymous_can_list_posts(self, api_client, user):
        Post.objects.create(author=user, title="t", content="c")
        response = api_client.get(posts_url())
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_list_is_paginated_at_ten(self, api_client, user):
        for i in range(15):
            Post.objects.create(author=user, title=f"t{i}", content="c")

        response = api_client.get(posts_url())
        assert response.status_code == 200
        assert response.data["count"] == 15
        assert len(response.data["results"]) == 10
        assert response.data["next"] is not None


class TestCreatePost:

    def test_anonymous_cannot_create_post(self, api_client):
        response = api_client.post(
            posts_url(), {"title": "t", "content": "c"}
        )
        assert response.status_code in (401, 403)

    def test_authenticated_user_can_create_post(self, auth_client, user):
        response = auth_client.post(
            posts_url(), {"title": "hello", "content": "world"}
        )
        assert response.status_code == 201
        assert Post.objects.count() == 1
        assert Post.objects.first().author == user

    def test_author_is_forced_to_request_user(self, auth_client, user, other_user):
        # even if a client tried to spoof the author, perform_create ignores it
        response = auth_client.post(
            posts_url(),
            {"title": "hello", "content": "world", "author": other_user.id},
        )
        assert response.status_code == 201
        assert Post.objects.first().author == user


class TestUpdateDeletePost:

    def test_owner_can_update_own_post(self, auth_client, user):
        post = Post.objects.create(author=user, title="old", content="c")
        response = auth_client.patch(
            post_detail_url(post.id), {"title": "new"}
        )
        assert response.status_code == 200
        post.refresh_from_db()
        assert post.title == "new"

    def test_non_owner_cannot_update_post(self, other_auth_client, user):
        post = Post.objects.create(author=user, title="old", content="c")
        response = other_auth_client.patch(
            post_detail_url(post.id), {"title": "hacked"}
        )
        assert response.status_code == 403
        post.refresh_from_db()
        assert post.title == "old"

    def test_admin_can_update_others_post(self, admin_client_api, user):
        post = Post.objects.create(author=user, title="old", content="c")
        response = admin_client_api.patch(
            post_detail_url(post.id), {"title": "moderated"}
        )
        assert response.status_code == 200

    def test_owner_can_delete_own_post(self, auth_client, user):
        post = Post.objects.create(author=user, title="old", content="c")
        response = auth_client.delete(post_detail_url(post.id))
        assert response.status_code == 204
        assert not Post.objects.filter(id=post.id).exists()

    def test_non_owner_cannot_delete_post(self, other_auth_client, user):
        post = Post.objects.create(author=user, title="old", content="c")
        response = other_auth_client.delete(post_detail_url(post.id))
        assert response.status_code == 403
        assert Post.objects.filter(id=post.id).exists()

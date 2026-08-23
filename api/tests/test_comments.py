import pytest
from django.urls import reverse

from posts.models import Comment, Post


pytestmark = pytest.mark.django_db


def comments_url():
    return reverse("comments-list")


def comment_detail_url(comment_id):
    return reverse("comments-detail", args=[comment_id])


@pytest.fixture
def a_post(user):
    return Post.objects.create(author=user, title="t", content="c")


class TestCreateComment:

    def test_anonymous_cannot_comment(self, api_client, a_post):
        response = api_client.post(
            comments_url(), {"post": a_post.id, "content": "hi"}
        )
        assert response.status_code in (401, 403)

    def test_authenticated_user_can_comment(self, auth_client, user, a_post):
        response = auth_client.post(
            comments_url(), {"post": a_post.id, "content": "nice post"}
        )
        assert response.status_code == 201
        comment = Comment.objects.get()
        assert comment.author == user
        assert comment.post == a_post


class TestModifyComment:

    def test_owner_can_delete_own_comment(self, auth_client, user, a_post):
        comment = Comment.objects.create(post=a_post, author=user, content="c")
        response = auth_client.delete(comment_detail_url(comment.id))
        assert response.status_code == 204

    def test_non_owner_cannot_delete_comment(self, other_auth_client, user, a_post):
        comment = Comment.objects.create(post=a_post, author=user, content="c")
        response = other_auth_client.delete(comment_detail_url(comment.id))
        assert response.status_code == 403
        assert Comment.objects.filter(id=comment.id).exists()

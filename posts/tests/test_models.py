import pytest
from django.db import IntegrityError, transaction

from posts.models import Comment, Like, Post


pytestmark = pytest.mark.django_db


class TestPostModel:

    def test_str_returns_title(self, user):
        post = Post.objects.create(author=user, title="Hello", content="World")
        assert str(post) == "Hello"

    def test_default_ordering_is_newest_first(self, user):
        older = Post.objects.create(author=user, title="older", content="x")
        newer = Post.objects.create(author=user, title="newer", content="x")

        titles = list(Post.objects.values_list("title", flat=True))
        assert titles.index("newer") < titles.index("older")


class TestCommentModel:

    def test_str_includes_author_and_truncated_content(self, user):
        post = Post.objects.create(author=user, title="t", content="c")
        comment = Comment.objects.create(
            post=post, author=user, content="a" * 50
        )
        assert str(comment).startswith(f"{user.username}:")


class TestLikeModel:

    def test_duplicate_like_raises_integrity_error(self, user):
        post = Post.objects.create(author=user, title="t", content="c")
        Like.objects.create(post=post, user=user)

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Like.objects.create(post=post, user=user)

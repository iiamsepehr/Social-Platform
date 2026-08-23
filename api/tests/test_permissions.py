import pytest
from django.contrib.auth.models import AnonymousUser

from api.permissions import IsAdminRole, IsOwnerOrAdmin
from posts.models import Post


pytestmark = pytest.mark.django_db


class DummyRequest:
    def __init__(self, user):
        self.user = user


class TestIsAdminRole:

    def test_denies_anonymous(self):
        perm = IsAdminRole()
        assert perm.has_permission(DummyRequest(AnonymousUser()), None) is False

    def test_denies_normal_user(self, user):
        perm = IsAdminRole()
        assert perm.has_permission(DummyRequest(user), None) is False

    def test_allows_admin(self, admin_user):
        perm = IsAdminRole()
        assert perm.has_permission(DummyRequest(admin_user), None) is True


class TestIsOwnerOrAdmin:

    def test_allows_owner(self, user):
        post = Post.objects.create(author=user, title="t", content="c")
        perm = IsOwnerOrAdmin()
        assert perm.has_object_permission(DummyRequest(user), None, post) is True

    def test_denies_non_owner(self, user, other_user):
        post = Post.objects.create(author=user, title="t", content="c")
        perm = IsOwnerOrAdmin()
        assert perm.has_object_permission(DummyRequest(other_user), None, post) is False

    def test_allows_admin_regardless_of_ownership(self, user, admin_user):
        post = Post.objects.create(author=user, title="t", content="c")
        perm = IsOwnerOrAdmin()
        assert perm.has_object_permission(DummyRequest(admin_user), None, post) is True

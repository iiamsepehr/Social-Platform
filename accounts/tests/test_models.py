import pytest
from django.db import IntegrityError, transaction

from accounts.models import Follow, User


pytestmark = pytest.mark.django_db


class TestUserModel:

    def test_role_defaults_to_user(self, user_factory):
        u = user_factory()
        assert u.role == User.USER
        assert u.is_normal_user() is True
        assert u.is_admin() is False

    def test_is_admin_true_for_admin_role(self, user_factory):
        u = user_factory(role=User.ADMIN)
        assert u.is_admin() is True
        assert u.is_normal_user() is False


class TestFollowModel:

    def test_follow_created_between_two_users(self, user, other_user):
        follow = Follow.objects.create(follower=user, following=other_user)
        assert follow.follower == user
        assert follow.following == other_user

    def test_duplicate_follow_raises_integrity_error(self, user, other_user):
        Follow.objects.create(follower=user, following=other_user)

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Follow.objects.create(follower=user, following=other_user)

    def test_self_follow_blocked_by_check_constraint(self, user):
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Follow.objects.create(follower=user, following=user)

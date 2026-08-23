from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    USER = "USER"
    ADMIN = "ADMIN"

    ROLE_CHOICES = (
        (USER, "User"),
        (ADMIN, "Admin"),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=USER
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_banned = models.BooleanField(
        default=False
    )

    timeout_until = models.DateTimeField(
        null=True,
        blank=True
    )

    def is_admin(self):
        return self.role == self.ADMIN

    def is_normal_user(self):
        return self.role == self.USER

class Follow(models.Model):

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following"
    )

    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"],
                name="unique_follow"
            ),
            models.CheckConstraint(
                condition=~models.Q(follower=models.F("following")),
                name="prevent_self_follow"
            ),
        ]

class Notification(models.Model):

    LIKE = "LIKE"
    COMMENT = "COMMENT"
    FOLLOW = "FOLLOW"

    TYPE_CHOICES = [
        (LIKE, "Like"),
        (COMMENT, "Comment"),
        (FOLLOW, "Follow"),
    ]

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_notifications"
    )

    notification_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES
    )

    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )

    comment = models.ForeignKey(
        "posts.Comment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_read = models.BooleanField(
        default=False
    )

    class Meta:

        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["recipient", "-created_at"],
                name="notif_recipient_created_idx",
            ),
        ]
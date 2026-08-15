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
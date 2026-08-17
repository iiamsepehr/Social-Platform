from rest_framework import serializers
from accounts.models import User, Follow, Notification
from posts.models import Post, Comment, Like

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "email",
            "role",
            "created_at",
            "is_banned",
            "timeout_until",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "is_banned",
            "timeout_until",
        ]


class PostSerializer(serializers.ModelSerializer):

    author = UserSerializer(
        read_only=True
    )

    class Meta:
        model = Post

        fields = [
            "id",
            "author",
            "title",
            "content",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "author",
            "created_at",
            "updated_at",
        ]

class CommentSerializer(serializers.ModelSerializer):

    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment

        fields = [
            "id",
            "post",
            "author",
            "content",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "author",
            "created_at",
            "updated_at",
        ]


class LikeSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)

    class Meta:
        model = Like

        fields = [
            "id",
            "post",
            "user",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "created_at",
        ]


class FollowSerializer(serializers.ModelSerializer):

    follower = UserSerializer(read_only=True)

    class Meta:
        model = Follow

        fields = [
            "id",
            "follower",
            "following",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "follower",
            "created_at",
        ]


class NotificationSerializer(serializers.ModelSerializer):

    actor = UserSerializer(read_only=True)

    class Meta:
        model = Notification

        fields = [
            "id",
            "recipient",
            "actor",
            "notification_type",
            "post",
            "comment",
            "created_at",
            "is_read",
        ]

        read_only_fields = [
            "id",
            "recipient",
            "actor",
            "created_at",
        ]
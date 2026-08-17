from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.models import User, Follow, Notification
from posts.models import Post, Comment, Like
from .serializers import UserSerializer, PostSerializer, CommentSerializer, LikeSerializer, FollowSerializer, NotificationSerializer
from .permissions import IsAdminRole, IsOwnerOrAdmin


class UserViewSet(
    viewsets.ReadOnlyModelViewSet
):

    queryset = (
        User.objects
        .all()
        .order_by("id")
    )

    serializer_class = UserSerializer

    permission_classes = [
        IsAuthenticatedOrReadOnly
    ]

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="follow",
        permission_classes=[IsAuthenticated],
    )
    def follow(self, request, pk=None):

        target_user = self.get_object()

        if target_user == request.user:
            return Response(
                {
                    "detail":
                    "You cannot follow yourself."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == "POST":

            follow, created = Follow.objects.get_or_create(
                follower=request.user,
                following=target_user,
            )

            if not created:
                return Response(
                    {
                        "detail":
                        "Already following this user."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "detail":
                    "User followed."
                },
                status=status.HTTP_201_CREATED,
            )

        deleted, _ = Follow.objects.filter(
            follower=request.user,
            following=target_user,
        ).delete()

        if deleted == 0:
            return Response(
                {
                    "detail":
                    "You are not following this user."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail":
                "User unfollowed."
            },
            status=status.HTTP_200_OK,
        )

class PostViewSet(viewsets.ModelViewSet):

    queryset = (
        Post.objects
        .select_related("author")
        .all()
        .order_by("-created_at")
    )

    serializer_class = PostSerializer

    def get_permissions(self):

        if self.action in [
            "update",
            "partial_update",
            "destroy",
        ]:
            permission_classes = [
                IsOwnerOrAdmin
            ]

        else:
            permission_classes = [
                IsAuthenticatedOrReadOnly
            ]

        return [
            permission()
            for permission
            in permission_classes
        ]

    def perform_create(self, serializer):

        serializer.save(
            author=self.request.user
        )

class CommentViewSet(viewsets.ModelViewSet):

    queryset = (
        Comment.objects
        .select_related(
            "author",
            "post",
        )
        .all()
        .order_by("-created_at")
    )

    serializer_class = CommentSerializer

    def get_permissions(self):

        if self.action in [
            "update",
            "partial_update",
            "destroy",
        ]:
            permission_classes = [
                IsOwnerOrAdmin
            ]

        else:
            permission_classes = [
                IsAuthenticatedOrReadOnly
            ]

        return [
            permission()
            for permission
            in permission_classes
        ]

    def perform_create(self, serializer):

        serializer.save(
            author=self.request.user
        )

class NotificationViewSet(
    viewsets.ReadOnlyModelViewSet
):

    serializer_class = NotificationSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        return (
            Notification.objects
            .filter(
                recipient=self.request.user
            )
            .select_related(
                "actor",
                "post",
                "comment",
            )
            .order_by(
                "-created_at"
            )
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="read",
    )
    def mark_read(
        self,
        request,
        pk=None,
    ):

        notification = self.get_object()

        if notification.is_read:
            return Response(
                {
                    "detail":
                    "Notification already read."
                }
            )

        notification.is_read = True
        notification.save(
            update_fields=["is_read"]
        )

        return Response(
            {
                "detail":
                "Notification marked as read."
            }
        )
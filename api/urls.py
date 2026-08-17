from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    PostViewSet,
    CommentViewSet,
    NotificationViewSet,
)


router = DefaultRouter()

router.register(
    "users",
    UserViewSet,
    basename="users",
)

router.register(
    "posts",
    PostViewSet,
    basename="posts",
)

router.register(
    "comments",
    CommentViewSet,
    basename="comments",
)

router.register(
    "notifications",
    NotificationViewSet,
    basename="notifications",
)

urlpatterns = router.urls
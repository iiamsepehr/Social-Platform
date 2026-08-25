from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)
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

urlpatterns = router.urls + [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # POST a refresh token here to invalidate it — the JWT equivalent of logout.
    path("token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
]
from django.urls import path
from . import views, admin_views

urlpatterns = [

    path(
        "signup/",
        views.signup,
        name="signup"
    ),


    path(
        "login/",
        views.user_login,
        name="login"
    ),


    path(
        "logout/",
        views.user_logout,
        name="logout"
    ),


    path(
        "profile/",
        views.profile,
        name="profile"
    ),

    path(
        "admin-test/",
        views.admin_test,
        name="admin_test"
    ),

    path(
        "change-username/",
        views.change_username,
        name="change_username"
    ),

    path(
        "change-email/",
        views.change_email,
        name="change_email"
    ),

    path(
        "change-password/",
        views.change_password,
        name="change_password"
    ),

    path(
        "delete-account/",
        views.delete_account,
        name="delete_account"
    ),

    path(
        "admin-panel/users/",
        admin_views.view_users,
        name="admin_users"
    ),

    path(
        "admin-panel/users/add/",
        admin_views.add_user,
        name="admin_add_user"
    ),

    path(
        "admin-panel/users/<int:user_id>/delete/",
        admin_views.delete_user,
        name="admin_delete_user"
    ),

]
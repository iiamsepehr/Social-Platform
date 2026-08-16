from django.urls import path
from . import views


urlpatterns = [

    path(
        "posts/",
        views.post_list,
        name="post_list"
    ),

    path(
        "posts/create/",
        views.create_post,
        name="post_create"
    ),

    path(
        "posts/<int:post_id>/",
        views.post_detail,
        name="post_detail"
    ),

    path(
        "posts/<int:post_id>/delete/",
        views.delete_post,
        name="post_delete"
    ),

    path(
        "admin-panel/posts/<int:post_id>/delete/",
        views.admin_delete_post,
        name="admin_delete_post"
    ),

    path(
        "posts/<int:post_id>/edit/",
        views.edit_post,
        name="post_edit"
    ),

    path(
        "admin-panel/posts/<int:post_id>/edit/",
        views.admin_edit_post,
        name="admin_edit_post"
    ),

]
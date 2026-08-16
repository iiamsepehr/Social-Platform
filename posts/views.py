from django.shortcuts import render, redirect, get_object_or_404
from .models import Post
from .forms import PostForm
from accounts.decorators import admin_required


def post_list(request):

    posts = Post.objects.all().order_by("-created_at")

    return render(
        request,
        "posts/post_list.html",
        {
            "posts": posts
        }
    )


def post_detail(request, post_id):

    post = get_object_or_404(
        Post,
        id=post_id
    )

    return render(
        request,
        "posts/post_detail.html",
        {
            "post": post
        }
    )


def create_post(request):

    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":

        form = PostForm(request.POST)

        if form.is_valid():

            post = form.save(
                commit=False
            )

            post.author = request.user

            post.save()

            return redirect(
                "post_detail",
                post_id=post.id
            )

    else:

        form = PostForm()

    return render(
        request,
        "posts/post_create.html",
        {
            "form": form
        }
    )

def edit_post(request, post_id):

    if not request.user.is_authenticated:
        return redirect("login")

    post = get_object_or_404(
        Post,
        id=post_id
    )

    # فقط صاحب Post اجازه ویرایش دارد
    if post.author != request.user:

        return redirect(
            "post_detail",
            post_id=post.id
        )

    if request.method == "POST":

        form = PostForm(
            request.POST,
            instance=post
        )

        if form.is_valid():

            form.save()

            return redirect(
                "post_detail",
                post_id=post.id
            )

    else:

        form = PostForm(
            instance=post
        )

    return render(
        request,
        "posts/post_edit.html",
        {
            "form": form,
            "post": post
        }
    )

def delete_post(request, post_id):

    if not request.user.is_authenticated:
        return redirect("login")

    if request.method != "POST":
        return redirect(
            "post_detail",
            post_id=post_id
        )

    post = get_object_or_404(
        Post,
        id=post_id
    )

    if post.author != request.user:
        return redirect(
            "post_detail",
            post_id=post.id
        )

    post.delete()

    return redirect(
        "post_list"
    )


@admin_required
def admin_delete_post(request, post_id):

    if request.method != "POST":
        return redirect("post_list")

    post = get_object_or_404(
        Post,
        id=post_id
    )

    post.delete()

    return redirect(
        "post_list"
    )

@admin_required
def admin_edit_post(request, post_id):

    if request.method == "POST":

        post = get_object_or_404(
            Post,
            id=post_id
        )

        form = PostForm(
            request.POST,
            instance=post
        )

        if form.is_valid():

            form.save()

            return redirect(
                "post_detail",
                post_id=post.id
            )

    else:

        post = get_object_or_404(
            Post,
            id=post_id
        )

        form = PostForm(
            instance=post
        )

    return render(
        request,
        "posts/post_edit.html",
        {
            "form": form,
            "post": post
        }
    )
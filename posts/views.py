from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Comment, Like
from .forms import PostForm, CommentForm
from accounts.decorators import admin_required
from accounts.models import Notification
from django.core.paginator import Paginator
from django.db.models import Q


def post_list(request):

    posts = Post.objects.all()

    # Search
    query = request.GET.get("q", "").strip()
    if query:

        posts = posts.filter(
            Q(title__icontains=query)
            |
            Q(content__icontains=query)
            |
            Q(author__username__icontains=query)
        )

    # Author Filter
    author = request.GET.get(
        "author",
        ""
    ).strip()

    if author:

        posts = posts.filter(
            author__username__icontains=author
        )

    # Sorting
    sort = request.GET.get(
        "sort",
        "newest"
    )


    if sort == "oldest":

        posts = posts.order_by(
            "created_at"
        )


    elif sort == "title_asc":

        posts = posts.order_by(
            "title"
        )


    elif sort == "title_desc":

        posts = posts.order_by(
            "-title"
        )


    else:

        posts = posts.order_by(
            "-created_at"
        )


    # Pagination
    paginator = Paginator(
        posts,
        5
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )


    return render(
        request,
        "posts/post_list.html",
        {
            "page_obj": page_obj,
            "query": query,
            "author": author,
            "sort": sort,
        }
    )

def post_detail(request, post_id):

    post = get_object_or_404(
        Post,
        id=post_id
    )

    user_liked = False

    if request.user.is_authenticated:

        user_liked = Like.objects.filter(
            post=post,
            user=request.user
        ).exists()

    return render(
        request,
        "posts/post_detail.html",
        {
            "post": post,
            "user_liked": user_liked,
            "comment_form": CommentForm(),
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

def like_post(request, post_id):

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

    like, created = Like.objects.get_or_create(
        post=post,
        user=request.user
    )

    if created and post.author != request.user:

        Notification.objects.create(
            recipient=post.author,
            actor=request.user,
            notification_type=Notification.LIKE,
            post=post
        )

    return redirect(
        "post_detail",
        post_id=post.id
    )

def unlike_post(request, post_id):

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

    Like.objects.filter(
        post=post,
        user=request.user
    ).delete()

    return redirect(
        "post_detail",
        post_id=post.id
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

def add_comment(request, post_id):

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

    form = CommentForm(request.POST)

    if form.is_valid():

        comment = form.save(
            commit=False
        )

        comment.post = post
        comment.author = request.user
        comment.save()

        if post.author != request.user:

            Notification.objects.create(
                recipient=post.author,
                actor=request.user,
                notification_type=Notification.COMMENT,
                post=post,
                comment=comment
            )

    return redirect(
        "post_detail",
        post_id=post.id
    )

def edit_comment(request, comment_id):

    if not request.user.is_authenticated:
        return redirect("login")

    comment = get_object_or_404(
        Comment,
        id=comment_id
    )

    if comment.author != request.user:

        return redirect(
            "post_detail",
            post_id=comment.post.id
        )

    if request.method == "POST":

        form = CommentForm(
            request.POST,
            instance=comment
        )

        if form.is_valid():

            form.save()

            return redirect(
                "post_detail",
                post_id=comment.post.id
            )

    else:

        form = CommentForm(
            instance=comment
        )

    return render(
        request,
        "posts/comment_edit.html",
        {
            "form": form,
            "comment": comment
        }
    )

def delete_comment(request, comment_id):

    if not request.user.is_authenticated:
        return redirect("login")

    comment = get_object_or_404(
        Comment,
        id=comment_id
    )

    if (
        comment.author != request.user
        and not request.user.is_admin()
    ):

        return redirect(
            "post_detail",
            post_id=comment.post.id
        )

    if request.method == "POST":

        post_id = comment.post.id

        comment.delete()

        return redirect(
            "post_detail",
            post_id=post_id
        )

    return redirect(
        "post_detail",
        post_id=comment.post.id
    )
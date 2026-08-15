from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import PostForm


@login_required
def create_post(request):

    if request.method == "POST":

        form = PostForm(request.POST)

        if form.is_valid():

            post = form.save(commit=False)

            post.author = request.user

            post.save()

            return redirect("profile")

    else:

        form = PostForm()

    return render(
        request,
        "posts/create_post.html",
        {
            "form": form
        }
    )
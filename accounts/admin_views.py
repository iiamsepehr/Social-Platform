from datetime import timedelta
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import User
from .forms import AdminCreateUserForm
from .decorators import admin_required
@admin_required
def view_users(request):

    users = User.objects.all()

    return render(
        request,
        "accounts/admin/users.html",
        {
            "users": users
        }
    )

@admin_required
def add_user(request):

    if request.method == "POST":

        form = AdminCreateUserForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect(
                "admin_users"
            )

    else:

        form = AdminCreateUserForm()

    return render(
        request,
        "accounts/admin/add_user.html",
        {
            "form": form
        }
    )

@admin_required
def delete_user(request, user_id):

    if request.method != "POST":
        return redirect("admin_users")

    user = User.objects.get(id=user_id)

    if user == request.user:
        return redirect("admin_users")

    user.delete()

    return redirect("admin_users")

@admin_required
def ban_user(request, user_id):

    if request.method != "POST":
        return redirect("admin_users")

    user = User.objects.get(id=user_id)

    if user == request.user:
        return redirect("admin_users")

    user.is_banned = True
    user.timeout_until = None
    user.save()

    return redirect("admin_users")


@admin_required
def unban_user(request, user_id):

    if request.method != "POST":
        return redirect("admin_users")

    user = User.objects.get(id=user_id)

    if user == request.user:
        return redirect("admin_users")

    user.is_banned = False
    user.save()

    return redirect("admin_users")


@admin_required
def timeout_user(request, user_id):

    if request.method != "POST":
        return redirect("admin_users")

    user = User.objects.get(id=user_id)

    if user == request.user:
        return redirect("admin_users")

    user.timeout_until = timezone.now() + timedelta(minutes=10)
    user.is_banned = False
    user.save()

    return redirect("admin_users")
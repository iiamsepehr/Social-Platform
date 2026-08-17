from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignupForm, ChangeUsernameForm, ChangeEmailForm, ChangePasswordForm, DeleteAccountForm
from .decorators import admin_required
from django.utils import timezone
from .models import User, Follow, Notification


def signup(request):

    if request.method == "POST":

        form = SignupForm(request.POST)


        if form.is_valid():

            user = form.save(
                commit=False
            )

            user.set_password(
                form.cleaned_data["password"]
            )

            user.save()

            login(
                request,
                user
            )

            messages.success(
                request,
                "Account created successfully."
            )

            return redirect(
                "profile"
            )


    else:

        form = SignupForm()


    return render(
        request,
        "accounts/signup.html",
        {
            "form": form
        }
    )



def user_login(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:

            if user.is_banned:

                messages.error(
                    request,
                    "Your account has been banned."
                )

                return redirect("login")


            if (
                user.timeout_until is not None
                and user.timeout_until > timezone.now()
            ):

                messages.error(
                    request,
                    "Your account is temporarily unavailable."
                )

                return redirect("login")


            if (
                user.timeout_until is not None
                and user.timeout_until <= timezone.now()
            ):

                user.timeout_until = None
                user.save()


            login(
                request,
                user
            )

            messages.success(
                request,
                "Logged in successfully."
            )

            return redirect(
                "profile"
            )


        messages.error(
            request,
            "Invalid username or password."
        )


    return render(
        request,
        "accounts/login.html"
    )

def user_logout(request):

    logout(request)

    messages.success(
        request,
        "Logged out successfully."
    )

    return redirect(
        "login"
    )

@login_required
def profile(request):

    return render(
        request,
        "accounts/profile.html"
    )

@login_required
def change_username(request):

    if request.method == "POST":

        form = ChangeUsernameForm(
            request.POST,
            instance=request.user
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Username changed successfully."
            )

            return redirect(
                "profile"
            )


    else:

        form = ChangeUsernameForm(
            instance=request.user
        )


    return render(
        request,
        "accounts/change_username.html",
        {
            "form": form
        }
    )

@login_required
def change_email(request):

    if request.method == "POST":

        form = ChangeEmailForm(
            request.POST,
            instance=request.user
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Email changed successfully."
            )

            return redirect(
                "profile"
            )


    else:

        form = ChangeEmailForm(
            instance=request.user
        )


    return render(
        request,
        "accounts/change_email.html",
        {
            "form": form
        }
    )

@login_required
def change_password(request):

    if request.method == "POST":

        form = ChangePasswordForm(
            request.user,
            request.POST
        )


        if form.is_valid():

            user = form.save()


            update_session_auth_hash(
                request,
                user
            )


            messages.success(
                request,
                "Password changed successfully."
            )


            return redirect(
                "profile"
            )


    else:

        form = ChangePasswordForm(
            request.user
        )


    return render(
        request,
        "accounts/change_password.html",
        {
            "form": form
        }
    )

@login_required
def delete_account(request):

    if request.method == "POST":

        form = DeleteAccountForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            user = request.user

            logout(request)

            user.delete()


            messages.success(
                request,
                "Account deleted successfully."
            )


            return redirect(
                "signup"
            )


    else:

        form = DeleteAccountForm()


    return render(
        request,
        "accounts/delete_account.html",
        {
            "form": form
        }
    )

@admin_required
def admin_test(request):

    return render(
        request,
        "accounts/profile.html"
    )


def user_profile(request, user_id):

    profile_user = get_object_or_404(
        User,
        id=user_id
    )

    is_following = False

    if request.user.is_authenticated:

        is_following = Follow.objects.filter(
            follower=request.user,
            following=profile_user
        ).exists()

    return render(
        request,
        "accounts/user_profile.html",
        {
            "profile_user": profile_user,
            "is_following": is_following,
        }
    )

@login_required
def follow_user(request, user_id):

    if request.method != "POST":
        return redirect(
            "user_profile",
            user_id=user_id
        )

    target = get_object_or_404(
        User,
        id=user_id
    )

    if target == request.user:
        return redirect(
            "user_profile",
            user_id=target.id
        )

    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=target
    )

    if created:

        Notification.objects.create(
            recipient=target,
            actor=request.user,
            notification_type=Notification.FOLLOW
        )

    return redirect(
        "user_profile",
        user_id=target.id
    )

@login_required
def unfollow_user(request, user_id):

    if request.method != "POST":
        return redirect(
            "user_profile",
            user_id=user_id
        )

    target = get_object_or_404(
        User,
        id=user_id
    )

    Follow.objects.filter(
        follower=request.user,
        following=target
    ).delete()

    return redirect(
        "user_profile",
        user_id=target.id
    )

@login_required
def notifications(request):

    notifications = request.user.notifications.select_related(
        "actor",
        "post",
        "comment"
    ).order_by("-created_at")

    return render(
        request,
        "accounts/notifications.html",
        {
            "notifications": notifications
        }
    )
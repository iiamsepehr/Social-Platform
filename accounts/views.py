from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignupForm, ChangeUsernameForm, ChangeEmailForm, ChangePasswordForm, DeleteAccountForm
from .decorators import admin_required
from django.utils import timezone

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
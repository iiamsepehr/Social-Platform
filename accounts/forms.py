from django import forms
from .models import User
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm, UserCreationForm

class SignupForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput
    )


    class Meta:
        model = User

        fields = [
            "username",
            "email",
            "password"
        ]

class AdminCreateUserForm(UserCreationForm):

    class Meta:
        model = User

        fields = [
            "username",
            "email",
            "role",
        ]

class ChangeUsernameForm(forms.ModelForm):

    class Meta:
        model = User

        fields = [
            "username"
        ]

class ChangeEmailForm(forms.ModelForm):

    class Meta:
        model = User

        fields = [
            "email"
        ]

class ChangePasswordForm(PasswordChangeForm):
    pass

class DeleteAccountForm(AuthenticationForm):
    pass
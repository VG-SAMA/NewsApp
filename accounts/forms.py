"""
Forms for user registration and login.

Includes:
- RegisterForm: Custom user registration form for `CustomUser` model.
- LoginForm: Simple login form for username/password authentication.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class RegisterForm(UserCreationForm):
    """
    Form for creating a new user account.

    Inherits from Django's `UserCreationForm` and adds custom fields
    and widgets for styling and placeholder text.
    """

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'role',
            'password1',
            'password2',
        ]

        widgets = {
            'username': forms.TextInput(
                attrs={
                    'placeholder': 'Username',
                    'class': 'form-control',
                    'border-color': 'darkcyan',
                }
            ),
            'first_name': forms.TextInput(
                attrs={'placeholder': 'First Name', 'class': 'form-control'}
            ),
            'last_name': forms.TextInput(
                attrs={'placeholder': 'Last Name', 'class': 'form-control'}
            ),
            'email': forms.EmailInput(
                attrs={'placeholder': 'Email', 'class': 'form-control'}
            ),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_username(self):
        """
        Ensure the username is unique.

        Raises:
            ValidationError: If the username is already in use.
        """

        username = self.cleaned_data.get("username")
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "Username is already in use, please choose another"
            )
        return username

    def clean_email(self):
        """
        Ensure the email is unique.

        Raises:
            ValidationError: If the email is already in use.
        """

        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already in use")
        return email


class LoginForm(forms.Form):
    """
    Simple login form for authenticating users.

    Fields:
        - username: User's username.
        - password: User's password.
    """

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Username"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        )
    )

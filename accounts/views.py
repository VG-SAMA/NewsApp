"""
Views for user registration, login, logout, and password management.

Includes:
- Registration and login views
- Role-based redirection
- Password reset workflow with token generation and email
- Test page access control

References:
https://docs.djangoproject.com/en/5.2/ref/contrib/auth/#django.contrib.auth.models.User.set_password
https://docs.djangoproject.com/en/5.2/topics/auth/default/
"""

from django.shortcuts import render, redirect
from django.http import (
    HttpRequest,
    HttpResponseServerError,
    HttpResponseRedirect,
)
from .forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from decorators.index import manager_publishers_required, journalist_required, editor_required, reader_required  # type: ignore
from django.contrib.auth.decorators import login_required
from helpers import index
import secrets
from datetime import datetime, timedelta
from hashlib import sha1
from .models import CustomUser, ResetToken
from django.core.mail import EmailMessage
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

helpers = index.Helpers()


def home_page():
    """
    Return the URL for the registration page.
    """
    return reverse('accounts:register')


def register(request: HttpRequest):
    """
    Handle new user registration.

    POST:
        - Validate form data
        - Create user
        - Log the user in
        - Redirect based on role

    GET:
        - Render empty registration form
    """

    helpers.clear_messages(request)

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            # Save user and log in immediately
            user = form.save()
            login(request, user)
            messages.success(
                request, "Registration successful! You are now logged in."
            )
            return route_to(request)

        else:
            # Show form errors in Bootstrap alerts
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def login_user(request: HttpRequest):
    """
    Handle user login.

    POST:
        - Authenticate username and password
        - Log in user
        - Redirect based on role

    GET:
        - Render empty login form
    """

    helpers.clear_messages(request)
    if request.method != 'POST':
        form = LoginForm()
        return render(request, 'accounts/login.html', {'form': form})

    if request.method == 'POST':
        print(request.POST)

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return route_to(request)

        else:
            messages.error(request, 'Invalid username or password')
    form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_user(request: HttpRequest):
    """
    Log the user out and redirect to login page.
    """

    logout(request)
    return redirect('accounts:login')


def route_to(request: HttpRequest):
    """
    Redirect user to appropriate dashboard based on role.

    Returns:
        - Redirect to publisher/admin creation for Manage_Publishers
        - Redirect to readers, editors, or journalists dashboard
        - Server error if role cannot be determined
    """

    user_type = getattr(request.user, 'role', '')

    try:
        if request.user.groups.filter(name='Manage_Publishers').exists():
            return redirect('news:all_publishers')

        elif user_type == 'reader':
            return redirect('news:readers_dashboard')

        elif user_type == 'editor':
            return redirect('news:editors_dashboard')

        elif user_type == 'journalist':
            return redirect('news:journalists_dashboard')

    except:
        return HttpResponseServerError(
            'Error 500: Internal Server Error. Sorry the server could not validate what your role is'
        )

    logout_user(request)
    return redirect('accounts:login')


@login_required
# @manager_publishers_required
# @journalist_required
@reader_required
def test_page(request: HttpRequest):
    """
    Test page to verify decorator authorisation access.
    """

    return render(
        request,
        'accounts/test.html',
        {'msg': 'this is the test page.'},
    )


def clear_messages(request: HttpRequest):
    """Function to clear the messages from request."""
    list(messages.get_messages(request))


# Emails, forgot password and tokens
def forgot_password_form(request: HttpRequest):
    """Render the forgot password form page."""
    return render(request, 'accounts/forgot_password.html')


def build_email(user: AbstractUser, reset_url: str):
    """
    Build a password reset email for the given user.

    Returns a Django EmailMessage object.
    """

    subject = 'Password Reset'
    email_address = user.email
    domain = 'vidaal702@gmail.com'
    body = f'Hi {user.username} here is the link to reset your password: {reset_url}'
    email = EmailMessage(subject, body, domain, [email_address])
    return email


def generate_reset_url(user: AbstractUser):
    """
    Generate a unique password reset URL for the user.

    Saves a ResetToken instance with 5-minute expiry.
    """

    domain = 'http://127.0.0.1:8000'
    url = f'{domain}/accounts/reset_password/'
    token = str(secrets.token_urlsafe(16))

    expiry_date = datetime.now() + timedelta(minutes=5)

    # creates the token and encodes it
    ResetToken.objects.create(
        user=user,
        token=sha1(token.encode()).hexdigest(),
        expiry_date=expiry_date,
    )

    url += f'{token}/'
    return url


def send_password_reset_email(request: HttpRequest):
    """
    Handle sending the password reset email.

    Validates email exists and sends reset link, or shows error.
    """

    clear_messages(request)
    user_email = request.POST.get('email')

    print(user_email)
    if user_email:
        user = CustomUser.objects.get(email=user_email)

        # calls methods to build and send reset link email
        url = generate_reset_url(user)
        email = build_email(user, url)
        email.send()

        return render(
            request,
            'accounts/password_reset_info.html',
            {
                'msg': 'Password reset email has been sent, please check your inbox'
            },
        )

    messages.error(request, 'Password was not found please try again')
    return redirect('accounts:forgot_password')


def reset_user_password(request: HttpRequest, token: str):
    """
    Render the password reset page after verifying the token.

    Stores user ID and token in session for validation on password change.
    """

    try:
        # sha1(token.encode()).hexdigest()

        # finds user token in db
        user_token = ResetToken.objects.get(
            token=sha1(token.encode()).hexdigest()
        )

        if user_token.expiry_date < timezone.now():
            # if user_token.expiry_date.replace(tzinfo=None) < datetime.now(): # type: ignore
            user_token.delete()

        request.session['user_id'] = user_token.user.pk  # type: ignore
        request.session['token'] = token

    except Exception as e:
        user_token = None
        messages.error(request, str(e))
        print(e)

    return render(
        request, 'accounts/password_reset.html', {'token': user_token}
    )


def change_user_password(user_id: str, password: str):
    """Update the user's password and save the user instance."""

    # find user and reset their password
    user = CustomUser.objects.get(pk=user_id)
    user.set_password(password)
    user.save()


def reset_password(request: HttpRequest):
    """
    Change user password after validation.

    Checks session for user_id and token, validates password confirmation,
    updates password, and deletes the ResetToken.
    """

    user_id = request.session.get('user_id')
    token = request.session.get('token')
    password = request.POST.get('password')
    password_conf = request.POST.get('password_conf')

    if not user_id or not token:
        messages.error(
            request,
            "Invalid or expired session. Please request a new password reset.",
        )
        return redirect('accounts:forgot_password')

    if password:
        # check password entries match each other
        if password == password_conf:
            change_user_password(user_id, password)

            ResetToken.objects.get(
                token=sha1(token.encode()).hexdigest()
            ).delete()
            return HttpResponseRedirect(reverse('accounts:login'))

        else:
            return HttpResponseRedirect(reverse('accounts:password_reset'))

    return redirect('accounts:login')

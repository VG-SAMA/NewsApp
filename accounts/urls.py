from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('test/', views.test_page, name='test'),
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout_user'),
    # passwod reset
    path(
        'forgot_password/', views.forgot_password_form, name='forgot_password'
    ),
    path(
        'send_password_reset/',
        views.send_password_reset_email,
        name='send_password_reset',
    ),
    path(
        'reset_password/<str:token>/',
        views.reset_user_password,
        name='password_reset',
    ),
    path(
        'password_reset/', views.reset_password, name='password_reset_change'
    ),
]

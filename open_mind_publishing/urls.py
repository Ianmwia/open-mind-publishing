"""
URL configuration for open_mind_publishing project.
"""
from django.contrib import admin
from django.urls import path
from .api import api  # <-- Import the main API instance
from allauth.headless.account import views as headless_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Django Ninja API routes (accounts + projects)
    path('api/', api.urls),

    # ─── Allauth Headless Auth Endpoints (JWT) ───────────────────────────────
    path(
        'api/auth/login/',
        headless_views.LoginView.as_api_view(client='app'),
        name='api_login'
    ),
    path(
        'api/auth/signup/',
        headless_views.SignupView.as_api_view(client='app'),
        name='api_signup'
    ),
    path(
        'api/auth/session/',
        headless_views.SessionView.as_api_view(client='app'),
        name='api_session'
    ),
    path(
        'api/auth/password/change/',
        headless_views.ChangePasswordView.as_api_view(client='app'),
        name='api_change_password'
    ),
    path(
        'api/auth/password/request/',
        headless_views.RequestPasswordResetView.as_api_view(client='app'),
        name='api_request_password_reset'
    ),
    path(
        'api/auth/password/reset/',
        headless_views.ResetPasswordView.as_api_view(client='app'),
        name='api_reset_password'
    ),
    path(
        'api/auth/email/verify/',
        headless_views.VerifyEmailView.as_api_view(client='app'),
        name='api_verify_email'
    ),
    path(
        'api/auth/logout/',
        headless_views.LogoutView.as_api_view(client='app'),
        name='api_logout'
    ),
]

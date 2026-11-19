from django.urls import path

from apps.users.views import LoginView, MeView, RefreshTokenView, RegisterView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/token/refresh/", RefreshTokenView.as_view(), name="auth-token-refresh"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
]

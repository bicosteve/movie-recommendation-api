from django.urls import path

from .views import (
    RegisterView,
    VerifyEmailView,
    LoginView,
    LogoutView,
    RefreshTokenView,
)


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-account/", VerifyEmailView.as_view(), name="verify-account"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token-refresh"),
]

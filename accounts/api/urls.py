from django.urls import path

from .views import (
    RegisterView,
    VerifyAccountView,
    LoginView,
    LogoutView,
    RefreshTokenView,
)


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-account/", VerifyAccountView.as_view(), name="verify-account"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token-refresh"),
]

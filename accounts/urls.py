from django.urls import path
from .views_templates import (
    register_page,
    login_page,
    forgot_password_page,
    reset_password_page,
    profile_page, 
)

from .views import RegisterView, LoginView, VerifyEmailView, ProfileView
from django.conf import settings


app_name = "accounts_pages"


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path(
        "verify/<uidb64>/<token>/",
        VerifyEmailView.as_view(),
        name="verify",
    ),
    path("profile/", ProfileView.as_view(), name="profile"),
]

urlpatterns = []

if settings.DEBUG:
    urlpatterns = [
    path("register/", register_page),
    path("login/", login_page),
    path("forgot-password/", forgot_password_page),
    path("reset-password/<int:uid>/<str:token>/", reset_password_page),
    path("profile/", profile_page),
]
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView,
    LogoutView,
    VerifyEmailView,
    RegisterView,
    ForgotPasswordView,
    ResetPasswordView,
    ProfileView,
    AdminProfileViewSet,
    AdminUserViewSet,
)

app_name = "accounts_api"

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("refresh/", TokenRefreshView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("register/", RegisterView.as_view()),
    path("verify-email/<int:uid>/<str:token>/", VerifyEmailView.as_view()),
    path("forgot-password/", ForgotPasswordView.as_view()),
    path("reset-password/<int:uid>/<str:token>/", ResetPasswordView.as_view()),
    path("profile/", ProfileView.as_view()),
]

router = DefaultRouter()
router.register("admin/users", AdminUserViewSet, basename="admin-users")
router.register("admin/profiles", AdminProfileViewSet, basename="admin-profiles")

urlpatterns += router.urls


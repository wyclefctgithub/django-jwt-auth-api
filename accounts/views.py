from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics
from django.contrib.auth import get_user_model
from .tokens import email_verification_token, password_reset_token
from .serializers import LoginSerializer, RegisterSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, ProfileSerializer, AdminProfileSerializer, AdminUserSerializer
from .permissions import IsOwnerOrAdmin, IsAdminUserStrict
from .models import UserProfile
from rest_framework import viewsets
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView


User = get_user_model()

# Create your views here.

class LoginRateThrottle(AnonRateThrottle):
    rate = "5/min"


class LoginView(TokenObtainPairView):
    throttle_classes = [LoginRateThrottle]


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        
class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_object(self):
        return self.request.user.profile

class VerifyEmailView(APIView):
    permission_classes = []

    def get(self, request, uid, token):
        user = User.objects.filter(pk=uid).first()

        if not user:
            return Response(
                {"detail": "Invalid user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not email_verification_token.check_token(user, token):
            return Response(
                {"detail": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = True
        user.save(update_fields=["is_active"])

        return Response({"detail": "Email verified successfully"})
    

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "If the email exists, a reset link has been sent."},
            status=status.HTTP_200_OK,
        )
    

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uid, token):
        user = User.objects.filter(pk=uid).first()
        if not user:
            return Response(
                {"detail": "Invalid reset link"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not password_reset_token.check_token(user, token):
            return Response(
                {"detail": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)

        return Response({"detail": "Password reset successful"})
    
    
class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUserStrict]
    lookup_field = "id"


class AdminProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.select_related("user")
    serializer_class = AdminProfileSerializer
    permission_classes = [IsAdminUserStrict]
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, UserProfile
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail
from .tokens import email_verification_token, password_reset_token

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = User
        fields = ("email", "password")

    def create(self, validated_data):
        request = self.context["request"]

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            is_active=False,
        )

        uid = user.pk
        token = email_verification_token.make_token(user)

        verify_url = request.build_absolute_uri(
            reverse(
                "accounts_api:verify-email",
                args=[uid, token],
            )
        )

        send_mail(
            subject="Verify your email",
            message=f"Click to verify your account:\n{verify_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password")
        
        if not user.is_active:
            raise serializers.ValidationError("Account is not active")
        
        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
    

class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = ("email", "full_name", "avatar")
        read_only_fields = ("email",)

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        # Do not reveal if email exists
        return email

    def save(self, **kwargs):
        request = self.context["request"]
        email = self.validated_data["email"]

        user = User.objects.filter(email=email, is_active=True).first()
        if not user:
            return  # silent success

        token = password_reset_token.make_token(user)
        uid = user.pk

        reset_url = request.build_absolute_uri(
            reverse("accounts:reset-password", args=[uid, token])
        )

        send_mail(
            subject="Reset your password",
            message=f"Click to reset your password:\n{reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )



class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8, write_only=True)

    def save(self, user):
        user.set_password(self.validated_data["password"])
        user.save(update_fields=["password"])


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
        )
        read_only_fields = ("id", "date_joined")


class AdminProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "email",
            "full_name",
            "avatar",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "email", "created_at", "updated_at")

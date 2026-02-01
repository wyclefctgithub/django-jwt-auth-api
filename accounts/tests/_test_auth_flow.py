from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()


class AuthFlowTests(APITestCase):

    def setUp(self):
        self.email = "test@example.com"
        self.password = "StrongPass123"

    def test_register_user(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": self.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=self.email)
        self.assertFalse(user.is_active)

    def test_email_verification(self):
        user = User.objects.create_user(
            email=self.email,
            password=self.password,
            is_active=False,
        )

        from accounts.tokens import email_verification_token
        token = email_verification_token.make_token(user)

        response = self.client.get(
            f"/api/auth/verify-email/{user.id}/{token}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_login_after_verification(self):
        user = User.objects.create_user(
            email=self.email,
            password=self.password,
            is_active=True,
        )

        response = self.client.post(
            "/api/auth/login/",
            {
                "email": self.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_profile_requires_authentication(self):
        response = self.client.get("/api/auth/profile/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_owner_access(self):
        user = User.objects.create_user(
            email=self.email,
            password=self.password,
            is_active=True,
        )

        login = self.client.post(
            "/api/auth/login/",
            {
                "email": self.email,
                "password": self.password,
            },
            format="json",
        )

        token = login.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

        response = self.client.get("/api/auth/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class RegistrationTest(APITestCase):
    def test_user_can_register(self):
        url = reverse("accounts_api:register")

        data = {
            "email": "test@example.com",
            "password": "StrongPass123!",
            "password2": "StrongPass123!",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())


class EmailVerificationTest(APITestCase):
    def test_email_verification(self):
        user = User.objects.create_user(
            email="verify@example.com",
            password="StrongPass123!",
            is_active=False,
        )

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        url = reverse(
            "accounts_api:verify-email",
            args=[uid, token],
        )

        response = self.client.get(url)
        user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(user.is_active)

class LoginTest(APITestCase):
    def test_login_returns_tokens(self):
        User.objects.create_user(
            email="login@example.com",
            password="StrongPass123!",
            is_active=True,
        )

        url = reverse("accounts_api:login")

        data = {
            "email": "login@example.com",
            "password": "StrongPass123!",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

class ProfileTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="profile@example.com",
            password="StrongPass123!",
            is_active=True,
        )

        login = self.client.post(
            reverse("accounts_api:login"),
            {
                "email": "profile@example.com",
                "password": "StrongPass123!",
            },
        )

        self.access = login.data["access"]

    def test_profile_requires_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")
        response = self.client.get(reverse("accounts_api:profile"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)


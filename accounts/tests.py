# tests/test_auth_views.py
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class CustomObtainPairViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("token_obtain_pair")
        self.password = "testpassword123"
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password=self.password,
            is_active=True,
        )

    def test_login_success(self):
        """Should return access & refresh tokens for valid credentials."""
        response = self.client.post(
            self.url,
            {"username": self.user.username, "password": self.password},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password(self):
        """Should return 401 for incorrect password."""
        response = self.client.post(
            self.url,
            {"username": self.user.username, "password": "wrongpassword"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)

    def test_login_nonexistent_user(self):
        """Should return 401 for non-existent user."""
        response = self.client.post(
            self.url, {"username": "ghost", "password": "irrelevant"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_unverified_user(self):
        """
        Should return 400 for unverified users if your serializer
        checks verification (e.g., `is_active=False` or `is_verified=False`).
        """
        unverified_user = User.objects.create_user(
            username="unverified",
            email="unverified@example.com",
            password="password123",
            is_active=False,
        )

        response = self.client.post(
            self.url,
            {"username": unverified_user.username, "password": "password123"},
            format="json",
        )

        # If your serializer raises ValidationError("User not verified")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("logout")
        self.password = "strongpass123"
        self.user = User.objects.create_user(
            username="logoutuser",
            email="logout@example.com",
            password=self.password,
            is_active=True,
        )
        # Generate tokens for the user
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.refresh_token = str(refresh)

    def test_logout_success(self):
        """Should blacklist refresh token and return 200."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.post(
            self.url, {"refresh": self.refresh_token}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["msg"], "Logged out successfully")

    def test_logout_missing_refresh_token(self):
        """Should return 400 if no refresh token is provided."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Refresh token required")

    def test_logout_invalid_refresh_token(self):
        """Should return 400 if refresh token is invalid."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.post(
            self.url, {"refresh": "invalidtoken"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_logout_no_access_token(self):
        """Should return 401 if no access token is provided."""
        response = self.client.post(
            self.url, {"refresh": self.refresh_token}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

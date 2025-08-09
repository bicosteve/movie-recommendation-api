from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch

User = get_user_model()


class RecommendationMovieViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("recommend")
        self.password = "strongpass123"
        self.user = User.objects.create_user(
            username="reco_user",
            email="reco@example.com",
            password=self.password,
            is_active=True,
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    @patch("./services/rating.py")
    def test_get_recommendations_success(self, mock_get_recommendation):
        """Should return 200 and list of recommended movies."""
        # Mock service output
        mock_get_recommendation.return_value = [
            {"movie_id": 101, "title": "Inception", "rating_prediction": 40.8},
            {"movie_id": 202, "title": "The Matrix", "rating_prediction": 50.7},
        ]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["title"], "Inception")
        mock_get_recommendation.assert_called_once_with(self.user.id)

    def test_get_recommendations_unauthorized(self):
        """Should return 401 if no token is provided."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RateMovieViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("recommend")
        self.password = "strongpass123"
        self.user = User.objects.create_user(
            username="rateuser",
            email="rateuser@example.com",
            password=self.password,
            is_active=True,
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    @patch("./services/rating.py")  # Update import path
    def test_rate_movie_success(self, mock_rate_movie):
        """Should store rating and return 201."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        payload = {"movie_id": 101, "rating": 40.5}

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["msg"], "Rating created!")
        mock_rate_movie.assert_called_once_with(self.user.id, 101, 40.5)

    def test_rate_movie_validation_error(self):
        """Should return 400 if data is invalid."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        payload = {"movie_id": "", "rating": ""}  # invalid

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_rate_movie_unauthorized(self):
        """Should return 401 if no access token is provided."""
        payload = {"movie_id": 101, "rating": 40.5}

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

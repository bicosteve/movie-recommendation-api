from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers


from .serializers import RatingSerializer, RecommendationSerializer
from recommender.services.rating import RatingService
from recommender.repositories.rating import RatingRepository
from recommender.models_.recommender_model import RecommederModel
from .schema import (
    recommendation_response,
    rate_movie_request_schema,
    rate_movie_success_schema,
    rate_movie_error_schema,
)


# Create your views here.
class RecommendationMovieView(APIView):
    """
    API endpoint for retrieving movie recommendations for an authenticated user.

    Authentication:
        - Uses custom JWTAuthentication to verify and decode user tokens.
        - Requires the user to be logged in (IsAuthenticated permission class).

    Purpose:
        - Provide personalized movie recommendations based on the user's
          rating history and a recommendation model.

    Schema Documentation:
        - 200: Returns a list of recommended movies serialized by RecommendationSerializer.
        - 401: Returns an error message if the request is unauthorized.

    Typical Use Case:
        - A frontend app calls this endpoint after a user logs in to fetch
          their personalized movie recommendations.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: recommendation_response,
            401: inline_serializer(
                name="UnauthorizedResponse",
                fields={
                    "detail": serializers.CharField(help_text="Authentication error")
                },
            ),
        },
        description="Lists movie recommendations for authenticated user",
    )
    def get(self, request):
        """
        Handle GET requests to fetch personalized movie recommendations.

        Workflow:
            1. Retrieve the authenticated user's ID from the request object.
            2. Instantiate the RatingService, which coordinates between the
               data repository (RatingRepository) and the recommendation model (RecommederModel).
            3. Call the service's get_recommendation method to fetch
               a list of recommended movies tailored to the user.
            4. Serialize the recommendations into a JSON-friendly format using
               RecommendationSerializer.
            5. Return the serialized data as the HTTP response.

        Returns:
            - 200 OK: List of recommended movies in serialized form.
            - 401 Unauthorized: Error if the JWT token is missing, expired, or invalid.

        Example Response (200 OK):
            [
                {
                    "movie_id": 101,
                    "title": "Inception",
                    "rating_prediction": 40.8
                },
                {
                    "movie_id": 202,
                    "title": "The Matrix",
                    "rating_prediction": 50.7
                }
            ]
        """
        user_id = request.user.id
        cache_key = f"recommended_movies:{user_id}"
        movies = cache.get(cache_key)

        if movies is None:
            print("Fetching movies from db...!")

            service = RatingService(
                repository=RatingRepository(),
                model=RecommederModel(),
            )

            recommendations = service.get_recommendation(user_id)

            cache.set(cache_key, recommendations, timeout=3600)

        else:
            recommendations = movies

        serializer = RecommendationSerializer(recommendations, many=True)

        return Response(serializer.data)


class RateMovieView(APIView):
    """
    API endpoint for submitting a movie rating by an authenticated user.

    Authentication:
        - Uses custom JWTAuthentication to verify and decode user tokens.
        - Requires the user to be logged in (IsAuthenticated permission class).

    Purpose:
        - Allow authenticated users to rate movies.
        - Ratings will be stored and can later be used by the recommendation system
          to personalize movie suggestions.

    Schema Documentation:
        - Request: Expects JSON containing `movie_id` and `rating` (validated by RatingSerializer).
        - 201: Returns a success message when the rating is stored successfully.
        - 400: Returns validation errors if the input is invalid.
        - 401: Returns an error if the request is unauthorized.

    Typical Use Case:
        - A frontend application calls this endpoint when a user submits a rating for a movie
          they have watched, enabling the system to refine future recommendations.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=rate_movie_request_schema,
        responses={
            201: rate_movie_success_schema,
            400: rate_movie_error_schema,
            401: inline_serializer(
                name="UnauthorizedResponse",
                fields={
                    "detail": serializers.CharField(help_text="Authentication error")
                },
            ),
        },
        description="Submit a rating for a movie. Requires authentication.",
    )
    def post(self, request):
        """
        Handle POST requests to create or update a user's rating for a movie.

        Workflow:
            1. Validate the incoming request data using RatingSerializer.
               - Ensures `movie_id` is valid and `rating` is within acceptable range.
            2. If validation fails, return a 400 Bad Request with error details.
            3. Retrieve the authenticated user's ID from the request.
            4. Extract the `movie_id` and `rating` values from validated data.
            5. Instantiate RatingService with:
               - RatingRepository for database operations.
               - RecommederModel for any model-based rating logic.
            6. Call the service's rate_movie method to store the rating.
            7. Return a 201 Created response with a success message.

        Returns:
            - 201 Created: If the rating was saved successfully.
            - 400 Bad Request: If validation fails for any field.
            - 401 Unauthorized: If the JWT token is missing, expired, or invalid.

        Example Request:
            {
                "movie_id": 101,
                "rating": 40.5
            }

        Example Response (201 Created):
            {
                "msg": "Rating created!"
            }
        """
        serializer = RatingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=400)

        user_id = request.user.id
        movie_id = serializer.validated_data["movie_id"]
        rating = serializer.validated_data["rating"]

        service = RatingService(
            repository=RatingRepository(),
            model=RecommederModel(),
        )

        service.rate_movie(user_id, movie_id, rating)

        return Response({"msg": "Rating created!"}, status=201)

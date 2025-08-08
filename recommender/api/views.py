from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import RatingSerializer
from recommender.services.rating import RatingService
from recommender.repositories.rating import RatingRepository
from recommender.models_.recommender_model import RecommederModel


# Create your views here.
class RecommendationMovieView(APIView):
    """
    API view that returns recommended movies for the authenticated user.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_summary="Get movie recommendations",
        operation_description="Returns a list of recommended movies for the authenticated user based on their past ratings and preferences.",
        responses={
            200: openapi.Response(
                description="List of recommended movies",
                schema=RatingSerializer(many=True),
                examples={
                    "application/json": [
                        {
                            "movie_id": 12,
                            "rating": 4.5,
                            "title": "Inception",
                            "poster_url": "https://image.tmdb.org/t/p/w500/inception.jpg",
                        },
                        {
                            "movie_id": 42,
                            "rating": 4.2,
                            "title": "Interstellar",
                            "poster_url": "https://image.tmdb.org/t/p/w500/interstellar.jpg",
                        },
                    ]
                },
            ),
            401: openapi.Response(
                description="Unauthorized – user must be authenticated with a valid JWT token"
            ),
        },
        security=[{"Bearer": []}],
    )
    def get(self, request):
        user_id = request.user.id

        repo = RatingRepository()
        model = RecommederModel()

        service = RatingService(repo, model)

        recommendations = service.get_recommendation(user_id)

        serializer = RatingSerializer(recommendations, many=True)

        return Response(serializer.data)


class RateMovieView(APIView):
    """
    API view to allow authenticated users to rate a movie.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_summary="Rate a movie",
        operation_description="Allows an authenticated user to submit a rating for a specific movie.",
        request_body=RatingSerializer,
        responses={
            201: openapi.Response(
                description="Rating submitted successfully",
                examples={"application/json": {"msg": "Rating returned"}},
            ),
            400: openapi.Response(
                description="Invalid input",
                examples={
                    "application/json": {
                        "error": {
                            "movie_id": ["This field is required."],
                            "rating": ["Ensure this value is less than or equal to 5."],
                        }
                    }
                },
            ),
            401: openapi.Response(
                description="Unauthorized – missing or invalid JWT token"
            ),
        },
        security=[{"Bearer": []}],
    )
    def post(self, request):
        serializer = RatingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=400)

        user_id = request.user.id
        movie_id = serializer.validated_data["movie_id"]
        rating = serializer.validated_data["rating"]

        repo = RatingRepository()
        model = RecommederModel()
        service = RatingService(repo, model)

        service.rate_movie(user_id, movie_id, rating)

        return Response({"msg": "Rating returned"}, status=201)

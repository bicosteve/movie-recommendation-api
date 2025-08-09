from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import RatingSerializer, RecommendationSerializer
from recommender.services.rating import RatingService
from recommender.repositories.rating import RatingRepository
from recommender.models_.recommender_model import RecommederModel


movie_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "movie_id": openapi.Schema(
            type=openapi.TYPE_INTEGER, description="ID of the movie"
        ),
        "rating": openapi.Schema(
            type=openapi.TYPE_NUMBER, format="float", description="Predicted rating"
        ),
        "title": openapi.Schema(
            type=openapi.TYPE_STRING, description="Title of the movie"
        ),
        "poster_url": openapi.Schema(
            type=openapi.TYPE_STRING, description="Full URL to the poster image"
        ),
    },
)

# Define the response schema as a list of movies
movies_list_schema = openapi.Schema(
    type=openapi.TYPE_ARRAY,
    items=movie_schema,
    example=[
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
    ],
)


# Create your views here.
class RecommendationMovieView(APIView):
    """
    API view that returns recommended movies for the authenticated user.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_summary="Get movie recommendations",
        operation_description="Returns a list of recommended movies for the authenticated user based on their past ratings and preferences.",
        responses={
            200: openapi.Response(
                description="List of recommended movies",
                schema=movies_list_schema,
            ),
            401: openapi.Response(
                description="Unauthorized – user must be authenticated with a valid JWT token"
            ),
        },
        security=[{"Bearer": []}],
    )
    def get(self, request):
        user_id = request.user.id

        service = RatingService(
            repository=RatingRepository(),
            model=RecommederModel(),
        )

        recommendations = service.get_recommendation(user_id)

        serializer = RecommendationSerializer(recommendations, many=True)

        return Response(serializer.data)


class RateMovieView(APIView):
    """
    API view to allow authenticated users to rate a movie.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_summary="Rate a movie",
        operation_description="Allows an authenticated user to submit a rating for a specific movie.",
        request_body=RatingSerializer,  # Expected input structure
        responses={
            201: openapi.Response(
                description="Rating submitted successfully",
                schema=openapi.Schema(  # Explicit schema for success response
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "msg": openapi.Schema(
                            type=openapi.TYPE_STRING, example="Rating returned"
                        ),
                    },
                ),
                examples={"application/json": {"msg": "Rating returned"}},
            ),
            400: openapi.Response(
                description="Invalid input",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "movie_id": openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Items(type=openapi.TYPE_STRING),
                                    example=["This field is required."],
                                ),
                                "rating": openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Items(type=openapi.TYPE_STRING),
                                    example=[
                                        "Ensure this value is less than or equal to 5."
                                    ],
                                ),
                            },
                        )
                    },
                ),
            ),
            401: openapi.Response(
                description="Unauthorized – missing or invalid JWT token",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Authentication credentials were not provided.",
                        )
                    },
                ),
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

        service = RatingService(
            repository=RatingRepository(),
            model=RecommederModel(),
        )

        service.rate_movie(user_id, movie_id, rating)

        return Response({"msg": "Rating created!"}, status=201)

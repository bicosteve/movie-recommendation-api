from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import render

from .serializers import RatingSerializer, RecommendationSerializer
from recommender.services.rating import RatingService
from recommender.repositories.rating import RatingRepository
from recommender.models_.recommender_model import RecommederModel


# Create your views here.
class RecommendationMovieView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

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

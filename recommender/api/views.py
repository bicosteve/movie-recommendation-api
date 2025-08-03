from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render

from .serializers import RatingSerializer
from recommender.services.rating import RatingService
from recommender.repositories.rating import RatingRepository
from recommender.models_.recommender_model import RecommederModel


# Create your views here.
class RecommendationMovieView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id

        repo = RatingRepository()
        model = RecommederModel()

        service = RatingService(repo, model)

        recommendations = service.get_recommendation(user_id)

        serializer = RatingSerializer(recommendations, many=True)

        return Response(serializer.data)


class RateMovieView(APIView):
    permission_classes = [IsAuthenticated]

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

from rest_framework import serializers
import re

from movies.models import Movie


class RatingSerializer(serializers.Serializer):
    movie_id = serializers.CharField()
    rating = serializers.FloatField()

    def validate_movie_id(self, value):
        if int(value) < 1:
            raise serializers.ValidationError(f"Movie ID {value} cannot be less than 1")

        if not Movie.objects.filter(tmdb_id=value).exists():
            raise serializers.ValidationError(f"Movie with ID {value} does not exist")

        return value

    def validate_rating(self, value):
        if not (1 <= float(value) <= 100):
            raise serializers.ValidationError(
                f"Movie rating cannot be less than 1 or greater 100: {value}"
            )

        return value


class RecommendationSerializer(serializers.Serializer):
    tmdb_id = serializers.IntegerField()
    title = serializers.CharField()
    overview = serializers.CharField()
    release_date = serializers.DateField()
    score = serializers.FloatField()

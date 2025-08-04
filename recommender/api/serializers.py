from rest_framework import serializers
import re


class RatingSerializer(serializers.Serializer):
    movie_id = serializers.CharField()
    rating = serializers.FloatField()

    def validate_movie_id(self, value):
        if value < 1:
            raise serializers.ValidationError(f"Movie id {value} cannot be less than 1")
        return value

    def validate_rating(self, value):
        if not (1 < value <= 100):
            raise serializers.ValidationError(
                f"Movie rating cannot be less than 1 or greater 100: {value}"
            )

        return value

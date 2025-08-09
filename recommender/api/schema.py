from drf_spectacular.utils import inline_serializer
from rest_framework import serializers

recommendation_response = serializers.ListSerializer(
    child=inline_serializer(
        name="Recommendation Reposne",
        fields={
            "movie_id": serializers.IntegerField(help_text="TMDb or internal movie ID"),
            "title": serializers.CharField(help_text="Movie title"),
            "overview": serializers.CharField(help_text="Brief movie description"),
            "release_date": serializers.DateField(
                help_text="Release date (YYYY-MM-DD)"
            ),
            "rating": serializers.FloatField(
                help_text="Predicted recommendation score"
            ),
        },
    )
)


# Request schema matches RatingSerializer
rate_movie_request_schema = inline_serializer(
    name="RateMovieRequest",
    fields={
        "movie_id": serializers.IntegerField(help_text="TMDb or internal movie ID"),
        "rating": serializers.FloatField(
            help_text="Rating given to the movie (1.0 - 100.0)"
        ),
    },
)

# Success response schema
rate_movie_success_schema = inline_serializer(
    name="RateMovieSuccessResponse",
    fields={
        "msg": serializers.CharField(help_text="Confirmation message"),
    },
)

# Error response schema
rate_movie_error_schema = inline_serializer(
    name="RateMovieErrorResponse",
    fields={
        "error": serializers.JSONField(help_text="Validation error details"),
    },
)

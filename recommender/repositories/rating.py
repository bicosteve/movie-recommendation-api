import logging
from django.db import IntegrityError, DatabaseError
from recommender.models import Rating
from movies.models import Movie

logger = logging.getLogger(__name__)


class RatingRepository:
    def add_rating(self, user_id, movie_id, rating):
        try:
            rating_object, created = Rating.objects.update_or_create(
                user_id=user_id,
                movie_id=movie_id,
                defaults={"rating": rating},
            )

            logger.info(
                f"{'Created' if created else 'Updated'} rating for user {user_id}, movie {movie_id}"
            )

            return True

        except IntegrityError as e:
            logger.error(f"Integritiy error while saving rating:  {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to insert rating because of: {str(e)}")
            return False

    def get_user_ratings(self, user_id):
        ratings = (
            Rating.objects.filter(user_id=user_id)
            .select_related("movie")
            .values("movie_id", "rating")
        )

        return list(ratings)

    def get_unrated_movies(self, user_id):

        rated_movies_id = Rating.objects.filter(user_id=user_id).values_list(
            "movie_id", flat=True
        )
        unrated_movies = Movie.objects.exclude(tmdb_id__in=rated_movies_id).values(
            "tmdb_id", "title", "overview", "release_date", "created"
        )
        return list(unrated_movies)

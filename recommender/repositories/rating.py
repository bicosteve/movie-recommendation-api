import logging
from django.db import connection, transaction, IntegrityError, DatabaseError

logger = logging.getLogger(__name__)


class RatingRepository:
    def __init__(self):
        self.cursor = connection.cursor()

    def add_rating(self, user_id, movie_id, rating):
        try:
            q = """
                INSERT INTO ratings( user_id,movie_id,rating)
                VALUES (%s,%s,%s)
                ON DUPLICATE KEY UPDATE rating = VALUES(rating)
            """
            self.cursor.execute(q, [user_id, movie_id, rating])

            logger.info(f"Inserted rating for user {user_id}, movie {movie_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to insert rating because of {str(e)}")
            return False

    def fetch_dict(self, query, params=None):
        self.cursor.execute(query, params or [])
        columns = [col[0] for col in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def get_user_ratings(self, user_id):
        q = """
            SELECT movie_id, rating FROM ratings 
            WHERE user_id = %s
        """
        return self.fetch_dict(q, [user_id])

    def get_unrated_movies(self, user_id):
        q = """
            SELECT tmdb_id, title, description, release_date
            FROM movies 
            WHERE tmdb_id NO in (
                SELECT movie_id FROM rating WHERE user_id = %s
            )
        """

        self.cursor.execute(q, [user_id])
        columns = [col[0] for col in self.cursor.fetchall()]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

from django.db import connection, transaction, IntegrityError, DatabaseError


class RatingRepository:
    def __init__(self):
        self.cursor = connection.cursor()

    def add_rating(self, user_id, movie_id, rating):
        q = """
            INSERT INTO ratings(user_id,movie_id,rating)
            VALUES (%s,%s,%s) RETURNING id;
        """
        self.cursor.execute(q, [user_id, movie_id, rating])

        id = self.cursor.fetchone()[0]
        return id

    def fetch_dict(self, query, params=None):
        self.cursor.execute(query, params or [])
        columns = [col[0] for col in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def get_all_ratings(self, user_id):
        q = """
            SELECT user_id,movie_id, rating FROM ratings 
            WHERE user_id = %s
        """
        return self.fetch_dict(q, [user_id])

    def get_unrated_movies(self):
        pass

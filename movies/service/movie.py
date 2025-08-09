import os
from movies.repo.movies import MovieRepository


class MovieService:
    def __init__(self):
        self.movie_repo = MovieRepository()

    def insert_movies(self, movies):
        inserted = failed = 0
        for movie in movies:
            result = self.repo.add_movie(movie)
            if result["status"] == "failed":
                failed += 1
            else:
                inserted += 1

        return {"inserted": inserted, "failed": failed}

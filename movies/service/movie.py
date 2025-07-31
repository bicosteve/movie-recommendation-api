from movies.repo.movies import MovieRepository


class MovieService:
    def __init__(self):
        self.movie_repo = MovieRepository()

    def insert_movies(self, movies):
        is_added = self.movie_repo.add_movies(movies)
        if not is_added:
            return False
        return True
